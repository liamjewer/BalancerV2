#include "wheel.h"

#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <gpiod.hpp>

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>

namespace {

constexpr int AS5600_ADDR = 0x36;
constexpr uint8_t REG_RAW_ANGLE = 0x0C;
const std::string PWM_CHIP = "/sys/class/pwm/pwmchip0";
using Val = gpiod::line::value;

void sysfs_write(const std::string& path, long value) {
    std::ofstream(path) << value;
}

bool read_raw_angle(int fd, int& raw) {     // 0..4095, false on I2C failure
    uint8_t reg = REG_RAW_ANGLE, b[2];
    if (write(fd, &reg, 1) != 1 || read(fd, b, 2) != 2) return false;
    raw = ((b[0] & 0x0F) << 8) | b[1];
    return true;
}

}

std::unique_ptr<gpiod::line_request> Wheel::stby_request;

Wheel::Wheel(const WheelConfig& config) : cfg(config) {}

Wheel::~Wheel() {
    if (dir_request) set_duty(0.0f); // stop
    if (!pwm_path.empty()) sysfs_write(pwm_path + "/enable", 0);
    if (i2c_fd >= 0) close(i2c_fd);
}

bool Wheel::encoder_init() {
    i2c_fd = open(cfg.i2c_dev.c_str(), O_RDWR);
    if (i2c_fd < 0 || ioctl(i2c_fd, I2C_SLAVE, AS5600_ADDR) < 0) {
        std::cerr << "cannot open encoder bus " << cfg.i2c_dev << "\n";
        return false;
    }
    return true;
}

bool Wheel::driver_init() {
    // hardware PWM channel
    pwm_path = PWM_CHIP + "/pwm" + std::to_string(cfg.pwm_channel);
    if (!std::ifstream(pwm_path + "/period"))
        sysfs_write(PWM_CHIP + "/export", cfg.pwm_channel);
    if (!std::ifstream(pwm_path + "/period")) {
        std::cerr << "PWM channel unavailable (is the overlay enabled?)\n";
        return false;
    }
    sysfs_write(pwm_path + "/duty_cycle", 0);      // duty must never exceed period
    sysfs_write(pwm_path + "/period", PWM_PERIOD_NS);
    sysfs_write(pwm_path + "/enable", 1);

    // direction pins
    try {
        gpiod::chip chip("/dev/gpiochip0");
        gpiod::line::offsets pins{static_cast<unsigned>(cfg.in1_pin),
                                  static_cast<unsigned>(cfg.in2_pin)};
        
        dir_request = std::make_unique<gpiod::line_request>(
            chip.prepare_request()
                .set_consumer("Wheel")
                .add_line_settings(pins, gpiod::line_settings()
                    .set_direction(gpiod::line::direction::OUTPUT)
                    .set_output_value(Val::INACTIVE))
                .do_request());

        if (!stby_request) {
            stby_request = std::make_unique<gpiod::line_request>(
                chip.prepare_request()
                    .set_consumer("stby")
                    .add_line_settings(STBY_PIN, gpiod::line_settings()
                        .set_direction(gpiod::line::direction::OUTPUT)
                        .set_output_value(Val::INACTIVE))     // starts low
                    .do_request());
        }

    } catch (const std::exception& e) {
        std::cerr << "cannot claim direction pins: " << e.what() << "\n";
        return false;
    }
    return true;
}

bool Wheel::init() {
    if (!encoder_init() || !driver_init()) return false;
    if (!read_raw_angle(i2c_fd, prev_raw)) {
        std::cerr << "no response from encoder on " << cfg.i2c_dev << "\n";
        return false;
    }
    history.fill({ticks, 0.0}); // fill with first reading
    return true;
}

void Wheel::set_duty(float duty) {
    if (!dir_request) return; // init() not done

    duty = -(std::clamp(duty, -1.0f, 1.0f));

    float magnitude = std::fabs(duty);
    if (magnitude > 0.0f)
        magnitude = pwm_deadband + magnitude * (1.0f - pwm_deadband);

    dir_request->set_value(cfg.in1_pin, duty > 0.0f ? Val::ACTIVE : Val::INACTIVE);
    dir_request->set_value(cfg.in2_pin, duty < 0.0f ? Val::ACTIVE : Val::INACTIVE);
    sysfs_write(pwm_path + "/duty_cycle", static_cast<long>(magnitude * PWM_PERIOD_NS));
}

void Wheel::encoder_update(float* dt) {
    int raw;
    if (!read_raw_angle(i2c_fd, raw)){
        return; // failure handling
    }

    // handle wraparound
    int delta = raw - prev_raw;
    if (delta > TICKS_PER_REV / 2)       delta -= TICKS_PER_REV;
    else if (delta < -TICKS_PER_REV / 2) delta += TICKS_PER_REV;

    if (cfg.invert_encoder) delta = -delta; //flip to other side
    ticks += delta;
    prev_raw = raw;

    const double meters_per_tick = 2.0 * M_PI * cfg.wheel_radius_m / TICKS_PER_REV;
    position = static_cast<float>(ticks * meters_per_tick);

    // slide the window (FIFO)
    elapsed += *dt/1000;
    std::copy(history.begin() + 1, history.end(), history.begin());
    history.back() = {ticks, elapsed};

    // speed = tick change across the window / time between its ends
    const double span = history.back().time - history.front().time;
    if (span <= 0.0) return;
    speed = static_cast<float>((history.back().ticks - history.front().ticks)* meters_per_tick / span);
}

void Wheel::enable()  {
    if (stby_request)
        stby_request->set_value(STBY_PIN, Val::ACTIVE);
}

void Wheel::disable() {
    if (stby_request)
        stby_request->set_value(STBY_PIN, Val::INACTIVE);
}

void Wheel::periodic(float* dt) {
    encoder_update(dt); 
}

float Wheel::get_speed() const {
    return speed;
}

float Wheel::get_position() const {
    return position;
}
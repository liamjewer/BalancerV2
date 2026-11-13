#pragma once

#include <cstdint>
#include <memory>
#include <string>
#include <array>

namespace gpiod { class line_request; }

struct WheelConfig {
    std::string i2c_dev; // AS5600 bus, e.g. "/dev/i2c-10"
    int pwm_channel = 0; // sysfs PWM channel (0 = GPIO12, 1 = GPIO13)
    int in1_pin = 0; // BCM GPIO numbers for the TB6612 direction pins
    int in2_pin = 0;
    float wheel_radius_m = 0.0f;
    bool invert_motor = false;  // mirrored wheels drive opposite ways
    bool invert_encoder = false; //count opposite too
};

class Wheel {
public:
    explicit Wheel(const WheelConfig& config);
    ~Wheel();
    Wheel(const Wheel&) = delete;
    Wheel& operator=(const Wheel&) = delete;

    // public in order to tune through HMI
    float pwm_deadband = 0.0f; // static friction

    bool init();                   
    void periodic(float* dt);

    void set_duty(float duty);
    float get_speed() const; // measured, filtered, m/s
    float get_position() const; // accumulated distance, m

private:
    WheelConfig cfg;

    float position = 0.0f;
    float speed = 0.0f;

    // encoder
    int i2c_fd = -1;
    int prev_raw = -1;
    int64_t ticks = 0;
    static constexpr int TICKS_PER_REV = 4096;
    
    static constexpr int SPEED_WINDOW = 5; // window for speed filtering
    struct Sample { int64_t ticks; double time; };
    std::array<Sample, SPEED_WINDOW + 1> history{};
    double elapsed = 0.0; // seconds since init

    // driver
    std::unique_ptr<gpiod::line_request> dir_request;
    std::string pwm_path;
    static constexpr long PWM_PERIOD_NS = 50000; // 20 kHz

    bool encoder_init();
    bool driver_init();
    void encoder_update(float* dt);
};
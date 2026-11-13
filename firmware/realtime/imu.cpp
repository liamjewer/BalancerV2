#include "imu.h"
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <chrono>
#include <thread>

namespace {
constexpr uint8_t REG_PWR_MGMT_1 = 0x6B;
constexpr uint8_t REG_WHO_AM_I = 0x75;
constexpr uint8_t REG_ACCEL_XOUT_H = 0x3B;
constexpr float ACCEL_LSB_PER_G = 16384.0f;
constexpr float GYRO_LSB_PER_DPS = 131.0f;

bool write_reg(int fd, uint8_t reg, uint8_t val) {
    uint8_t buf[2] = {reg, val};
    return write(fd, buf, 2) == 2;
}

bool read_regs(int fd, uint8_t reg, uint8_t* out, int len) {
    return write(fd, &reg, 1) == 1 && read(fd, out, len) == len;
}
}

Imu::~Imu() { if (fd_ >= 0) close(fd_); }

bool Imu::init(const char* dev, int addr) {
    fd_ = open(dev, O_RDWR);
    if (fd_ < 0 || ioctl(fd_, I2C_SLAVE, addr) < 0) {
        perror("imu i2c open");
        return false;
    }

    uint8_t id = 0;
    if (!read_regs(fd_, REG_WHO_AM_I, &id, 1) || id != 0x71) {
        printf("imu: unexpected WHO_AM_I 0x%02X\n", id);
        return false;
    }

    write_reg(fd_, REG_PWR_MGMT_1, 0x00);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    return true;
}

void Imu::update(float* dt) {
    uint8_t raw[14];
    if (!read_regs(fd_, REG_ACCEL_XOUT_H, raw, 14)) return;

    auto s16 = [&](int i) { return (int16_t)((raw[i] << 8) | raw[i + 1]); };

    float ax = s16(0) / ACCEL_LSB_PER_G;
    float ay = s16(2) / ACCEL_LSB_PER_G;
    float az = s16(4) / ACCEL_LSB_PER_G;
    float gy = s16(10) / GYRO_LSB_PER_DPS;

    float accel_pitch = std::atan2(-ax, std::sqrt(ay * ay + az * az)) * 180.0f / M_PI;

    if (first_) {
        pitch_ = accel_pitch;
        first_ = false;
        return;
    }
    pitch_ = alpha * (pitch_ + gy * (*dt/1000)) + (1.0f - alpha) * accel_pitch;
}
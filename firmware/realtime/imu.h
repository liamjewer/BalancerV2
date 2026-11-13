#pragma once

class Imu {
public:
    // public to enable remote tuning
    float alpha = 0.98f; // filter alpha

    ~Imu();
    bool  init(const char* dev = "/dev/i2c-1", int addr = 0x68);
    void  update(float* dt);
    float get_pitch() const { return pitch_; }

private:
    int   fd_ = -1;
    float pitch_ = 0.0f;
    bool  first_ = true;
};
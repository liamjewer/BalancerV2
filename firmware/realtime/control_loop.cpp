#include "control_loop.h"
#include "python_link.h"
#include "wheel.h"
#include "imu.h"

#include <iostream>
#include <chrono>
#include <thread>
#include <sched.h>
#include <sched.h>
#include <cstdio>
#include <nlohmann/json.hpp>

// constants
float Kp = 0.0;
float Ki = 0.0;
float Kd = 0.0;

constexpr int LOOP_HZ   = 200;
constexpr double PERIOD_MS = 1000.0 / LOOP_HZ;
constexpr auto   PERIOD    = std::chrono::duration_cast<std::chrono::steady_clock::duration>(std::chrono::duration<double, std::milli>(PERIOD_MS));

Imu imu;

PythonLink py;

const auto program_start = std::chrono::steady_clock::now();

// configure wheels

inline WheelConfig left_wheel_config() {
    WheelConfig c;
    c.i2c_dev = "/dev/i2c-1"; // primary bus
    c.pwm_channel = 1; // GPIO13 (PWMA)
    c.in1_pin = 23; // AIN1
    c.in2_pin = 24; // AIN2
    c.wheel_radius_m = 0.0335f;
    return c;
}

inline WheelConfig right_wheel_config() {
    WheelConfig c;
    c.i2c_dev = "/dev/i2c-0"; // secondary bus
    c.pwm_channel = 0; // GPIO12 (PWMB)
    c.in1_pin = 16; // BIN1
    c.in2_pin = 20; // BIN2
    c.wheel_radius_m = 0.0335f;
    c.invert_motor = true; // mirror right wheel
    c.invert_encoder = true;
    return c;
}

Wheel l_wheel(left_wheel_config());
Wheel r_wheel(right_wheel_config());

bool enabled = false;

int main() {
    //start python communication
    py.start();

    //force scheduler to "real time" on this core/thread (single core processor)
    sched_param param{};
    param.sched_priority = 80; 
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0)
        perror("could not schedule");   // scheduling failed


    auto last = std::chrono::steady_clock::now();
    auto next = last;
    int tick = 0;

    init();

    // runs every tick (behind the scenes)
    while(true){
        //calculate dt
        auto now = std::chrono::steady_clock::now();
        double dt = std::chrono::duration<double>(now - last).count()*1000; 
        last = now;

        // check for overruns
        if (dt > 1.5 * PERIOD_MS) {
            py.send("CTRL_OR", dt - PERIOD_MS);
            next = std::chrono::steady_clock::now();   // resync
        }

        // send the frequency to the hmi through python
        if(tick%(LOOP_HZ*2) == 0){ // every 2s
            py.send("ctrl_hz", 1000.0/dt);
        }
        

        periodic(dt, tick);

        
        tick++;
        next += PERIOD;
        std::this_thread::sleep_until(next);
    }

    return 0;
}

// set up (in front of the scenes)
void init(){
    imu.init();

    bool l_ok = l_wheel.init();
    bool r_ok = r_wheel.init();
    if (!l_ok || !r_ok) { //handle errors
        py.send("info", "wheel init failed");
    }
    //start at 0
    l_wheel.set_duty(0.0f);
    r_wheel.set_duty(0.0f);
}

// runs every tick (in front of the scenes)
void periodic(float dt, int current_tick){
    // check for messages from python
    while (auto msg = py.get_next_msg()) {
        auto& [type, value] = *msg;
        if(type == "ESTOP"){ // safety #1 priotity
            exit(EXIT_SUCCESS);
        }else if(type == "disable"){
            enabled = false;
            l_wheel.set_duty(0.0f);
            r_wheel.set_duty(0.0f);
        }else if(type == "enable"){
            enabled = true;
            l_wheel.enable(); //enables both (STBY high)
            py.send("None", "Enabling!");
        }
    }

    //update pitch
    imu.update(&dt);

    // call motor periodics
    l_wheel.periodic(&dt);
    r_wheel.periodic(&dt);

    if(enabled){
        // l_wheel.set_duty(0.3f);
        // r_wheel.set_duty(0.3f);
    }

    if (current_tick % 4 == 0) { // 50 Hz
        py.send("telemetry", {
            {"t", uptime_s()},
            {"tilt", imu.get_pitch()},
            {"rspeed", r_wheel.get_speed()},
            {"lspeed", l_wheel.get_speed()}
        });
    }

}

double uptime_s() {
    using namespace std::chrono;
    return duration<double>(steady_clock::now() - program_start).count();
}
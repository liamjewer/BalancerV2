#include "control_loop.h"
#include "python_link.h"

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

PythonLink py;
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
            py.send("loop_hz", 1000.0/dt);
        }
        

        periodic();

        
        tick++;
        next += PERIOD;
        std::this_thread::sleep_until(next);
    }

    return 0;
}

//runs every tick (in front of the scenes)
void periodic(){
    // check for messages from python
    while (auto msg = py.get_next_msg()) {
        auto& [type, value] = *msg;
        if(type == "ESTOP"){ // safety #1 priotity
            exit(EXIT_SUCCESS);
        }else if(type == "disable"){
            enabled = false;
        }else if(type == "enable"){
            enabled = true;
            py.send("None", "Enabling!");
        }
    }
}
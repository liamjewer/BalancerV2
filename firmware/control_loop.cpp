#include "control_loop.h"

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

constexpr double LOOP_HZ   = 200.0;
constexpr double PERIOD_MS = 1000.0 / LOOP_HZ;
constexpr auto   PERIOD    = std::chrono::duration_cast<std::chrono::steady_clock::duration>(std::chrono::duration<double, std::milli>(PERIOD_MS));

int main() {
    //force scheduler to "real time" on this core/thread (single core processor)
    sched_param param{};
    param.sched_priority = 80; 
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0)
        perror("could not schedule");   // scheduling failed


    auto last = std::chrono::steady_clock::now();
    auto next = last;
    int tick = 0;

    std::string line;
    if (std::getline(std::cin, line)) {
        nlohmann::json msg = nlohmann::json::parse(line);
        std::cerr << "got: " << msg.dump() << std::endl;
        py_print("10-4", msg["value"]);
    }

    /*while(true){
        //calculate dt
        auto now = std::chrono::steady_clock::now();
        double dt = std::chrono::duration<double>(now - last).count()*1000; 
        last = now;

         if (dt > 1.5 * PERIOD_MS) {
            std::cerr << "overrun: dt = " << dt << " ms\n";
            next = std::chrono::steady_clock::now();   // resync so it doesn't burst
        }

        if(tick%500 == 0) py_print("message", tick);
        

        tick++;
        next += PERIOD;
        std::this_thread::sleep_until(next);
    }*/

    return 0;
}

void py_print(std::string type, nlohmann::json value) {
    nlohmann::json msg = {{"type", type}, {"value", value}};
    std::cout << msg.dump() << std::endl;
}
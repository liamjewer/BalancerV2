#include <iostream>
#include <chrono>
#include <thread>

// constants
float Kp = 0.0;
float Ki = 0.0;
float Kd = 0.0;

constexpr double LOOP_HZ   = 200.0;
constexpr double PERIOD_MS = 1000.0 / LOOP_HZ;
constexpr auto   PERIOD    = std::chrono::duration_cast<std::chrono::steady_clock::duration>(std::chrono::duration<double, std::milli>(PERIOD_MS));

int main() {
    std::cout << "Control Loop Starting...\n";

    auto last = std::chrono::steady_clock::now();
    auto next = last;
    int tick = 0;

    while(true){
        //calculate dt
        auto now = std::chrono::steady_clock::now();
        double dt = std::chrono::duration<double>(now - last).count()*1000; 
        last = now;

         if (dt > 1.5 * PERIOD_MS) {
            std::cerr << "overrun: dt = " << dt << " ms\n";
            next = std::chrono::steady_clock::now();   // resync so it doesn't burst
        }


        std::cout << "control loop: " << tick++ << " ticks\n";
        

        next += PERIOD;
        std::this_thread::sleep_until(next);
    }

    return 0;
}
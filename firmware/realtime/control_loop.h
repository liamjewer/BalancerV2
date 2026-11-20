#pragma once
#include <string>

void init();
void periodic(float dt, int current_tick);
void shutdown();
float calculate_balance_PID(float dt);
double uptime_s();
bool save_tuning(const std::string& filepath = "hmi/config/tuning.json");
bool load_tuning(const std::string& filepath = "hmi/config/tuning.json");
#pragma once

void init();
void periodic(float dt, int current_tick);
void shutdown();
float calculate_balance_PID(float dt);
double uptime_s();
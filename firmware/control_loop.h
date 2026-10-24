#pragma once

#include <iostream>
#include <nlohmann/json.hpp>

void send_py(std::string,nlohmann::json);
void periodic();
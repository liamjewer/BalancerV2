#include "python_link.h"
#include <iostream>
#include <thread>

void PythonLink::start() {
    std::thread(&PythonLink::read, this).detach();
}

void PythonLink::read() {
    std::string line;
    while (std::getline(std::cin, line)) { // wait on this thread
        try {
            auto msg = nlohmann::json::parse(line);
            std::string type = msg.at("type").get<std::string>();

            if (type == "pyPing") {
                send("cppPong", true);
                continue;
            }

            std::lock_guard<std::mutex> lock(in_mutex);
            incoming.push({msg.at("type").get<std::string>(), msg.at("value")});
        } catch (...) {} // ignore bad JSON or missing keys
    }
    alive = false; // pipe is closed
}

void PythonLink::send(const std::string& type, const nlohmann::json& value) {
    nlohmann::json msg = {{"type", type}, {"value", value}};
    std::lock_guard<std::mutex> lock(out_mutex);
    std::cout << msg.dump() << std::endl; // endl flushes
}

std::optional<PythonLink::Msg> PythonLink::get_next_msg() {
    std::lock_guard<std::mutex> lock(in_mutex);
    if (incoming.empty()) return std::nullopt;
    Msg msg = std::move(incoming.front());
    incoming.pop();
    return msg;
}


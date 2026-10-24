#pragma once
#include <atomic>
#include <mutex>
#include <optional>
#include <queue>
#include <string>
#include <utility>
#include <nlohmann/json.hpp>

class PythonLink {
public:
    using Msg = std::pair<std::string, nlohmann::json>;// (type, value)

    void start();
    void send(const std::string& type, const nlohmann::json& value);
    std::optional<Msg> get_next_msg();// empty if nothing waiting
    bool connected() const { return alive; }

private:
    void read(); // runs on its own thread

    std::queue<Msg> incoming;
    std::mutex in_mutex;
    std::mutex out_mutex;
    std::atomic<bool> alive{true};
};
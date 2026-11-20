#!/bin/bash
set -e
cd "$(dirname "$0")"

mkdir -p build
g++ -std=c++17 firmware/realtime/*.cpp -o build/control_loop -lgpiodcxx -lgpiod
./firmware/venv/bin/python firmware/robot/main.py
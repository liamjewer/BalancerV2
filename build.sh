#!/bin/bash
set -e
cd "$(dirname "$0")"

mkdir -p build
g++ -std=c++17 -O2 -pthread firmware/realtime/*.cpp -o build/control_loop
./firmware/venv/bin/python firmware/robot/main.py
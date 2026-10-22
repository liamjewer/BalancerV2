cmake_minimum_required(VERSION 3.15)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
project(B-V2 CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Threads REQUIRED)
find_package(ixwebsocket CONFIG REQUIRED)

add_executable(B-V2 
    communication.cpp
)

target_link_libraries(B-V2 PRIVATE ixwebsocket::ixwebsocket)
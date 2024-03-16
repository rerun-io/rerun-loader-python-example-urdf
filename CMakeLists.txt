cmake_minimum_required(VERSION 3.16...3.27)

project(rerun_loader_sdk LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(NOT DEFINED CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

include(FetchContent)
FetchContent_Declare(rerun_sdk URL https://build.rerun.io/commit/dab0322/rerun_cpp_sdk.zip)
FetchContent_MakeAvailable(rerun_sdk)

add_executable(rerun_loader_sdk main.cpp)
target_link_libraries(rerun_loader_sdk PRIVATE rerun_sdk)

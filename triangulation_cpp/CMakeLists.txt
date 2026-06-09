cmake_minimum_required(VERSION 3.15)
project(delaunay_cpp)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -ffast-math")

find_package(pybind11 REQUIRED)

set(SOURCES
    src/main_module.cpp
    src/algorithms/incremental/triangulation.cpp
    src/algorithms/divide_and_conquer/triangulation.cpp
    src/algorithms/divide_and_conquer/quad_edge.cpp
    src/algorithms/divide_and_conquer/SlotMap.hpp
)

pybind11_add_module(delaunay_cpp ${SOURCES})

target_include_directories(delaunay_cpp PRIVATE src)
cmake_minimum_required(VERSION 3.15)
project(delaunay_cpp VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -ffast-math")

find_package(pybind11 REQUIRED)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

# Pliki źródłowe
set(SOURCES
        src/main_module.cpp
        src/algorithms/incremental/triangulation.cpp
        src/algorithms/divide_and_conquer/triangulation.cpp
)

# Nagłówki
set(HEADERS
        src/py_convert.hpp
        src/algorithms/divide_and_conquer/SlotMap.hpp
        src/algorithms/divide_and_conquer/quad_edge.hpp
)

# Tworzenie modułu
pybind11_add_module(delaunay_cpp ${SOURCES} ${HEADERS})

target_include_directories(delaunay_cpp PRIVATE src)

# Instalacja dla scikit-build
install(TARGETS delaunay_cpp DESTINATION .)

include(CheckIPOSupported)
check_ipo_supported(RESULT ipo_supported)
if(ipo_supported)
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
endif()
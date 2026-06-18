cmake_minimum_required(VERSION 3.15)
project(delaunay_cpp VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -ffast-math")

find_package(pybind11 REQUIRED)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

# Core library: algorithm .cpp files only. main_module.cpp stays out
# because its PYBIND11_MODULE must not be linked into the test executable.
add_library(triangulation_core STATIC
        src/algorithms/incremental/triangulation.cpp
        src/algorithms/divide_and_conquer/triangulation.cpp
)
target_include_directories(triangulation_core PUBLIC src)

# Python module
pybind11_add_module(delaunay_cpp
        src/main_module.cpp
        src/py_convert.hpp
        src/algorithms/divide_and_conquer/SlotMap.hpp
        src/algorithms/divide_and_conquer/quad_edge.hpp
)
target_link_libraries(delaunay_cpp PRIVATE triangulation_core)
target_include_directories(delaunay_cpp PRIVATE src)

# Unit tests (Boost.Test). Optional — only enabled if Boost is found, so
# scikit-build-core builds still succeed on machines without Boost installed.
find_package(Boost QUIET COMPONENTS unit_test_framework)
if(Boost_FOUND)
    enable_testing()
    add_executable(run_tests
            tests/test_point.cpp
            tests/test_triangle.cpp
            tests/test_geometry_functions.cpp
    )
    target_link_libraries(run_tests PRIVATE
            triangulation_core
            Boost::unit_test_framework
    )
    target_compile_definitions(run_tests PRIVATE BOOST_TEST_DYN_LINK)
    add_test(NAME triangulation_unit_tests COMMAND run_tests)
endif()

# Instalacja dla scikit-build
install(TARGETS delaunay_cpp DESTINATION .)

include(CheckIPOSupported)
check_ipo_supported(RESULT ipo_supported)
if(ipo_supported)
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
endif()
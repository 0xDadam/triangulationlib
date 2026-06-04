#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "py_convert.hpp"
#include "algorithms/incremental/triangulation.hpp"
#include "algorithms/divide_and_conquer/triangulation.hpp"

namespace py = pybind11;

std::vector<std::array<size_t, 3>> triangulate_points(py::array_t<double> points_array, bool use_triangle_walk = true) {
    auto points = py_convert::to_rust_point_vec(points_array);
    auto triangles = algorithms::incremental::triangulate(points, use_triangle_walk);
    
    return py_convert::to_py(triangles);
}

std::vector<std::array<size_t, 3>> triangulate_points_dnc(py::array_t<double> points_array) {
    auto points = py_convert::to_rust_point_vec(points_array);
    auto triangles = algorithms::divide_and_conquer::triangulate(points);
    
    return py_convert::to_py(triangles);
}

PYBIND11_MODULE(delaunay_cpp, m) {
    m.doc() = "Delaunay triangulation library written in C++";
    
    m.def("triangulate_points", &triangulate_points, 
          py::arg("points_array"), py::arg("use_triangle_walk") = true);
          
    m.def("triangulate_points_dnc", &triangulate_points_dnc, 
          py::arg("points_array"));
}
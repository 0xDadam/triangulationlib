#pragma once
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>
#include <array>
#include <stdexcept>
#include "geometry/point.hpp"
#include "geometry/triangle.hpp"

namespace py = pybind11;

namespace py_convert {

    inline std::vector<geometry::Point> to_rust_point_vec(const py::array_t<double>& points_array) {
        auto buf = points_array.request();
        const double* ptr = static_cast<double*>(buf.ptr);
        size_t num_points = buf.shape[0];
        
        std::vector<geometry::Point> points;
        points.reserve(num_points);
        for (size_t i = 0; i < num_points; ++i) {
            points.emplace_back(ptr[i * 2], ptr[i * 2 + 1]);
        }
        return points;
    }

    inline std::vector<std::array<size_t, 3>> to_py(const std::vector<geometry::Triangle>& triangles) {
        std::vector<std::array<size_t, 3>> result;
        result.reserve(triangles.size());
        for (const auto& tri : triangles) {
            result.push_back(tri.vertices);
        }
        return result;
    }

}
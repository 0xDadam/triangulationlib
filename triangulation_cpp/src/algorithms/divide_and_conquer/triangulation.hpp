#pragma once
#include <vector>
#include "geometry/point.hpp"
#include "geometry/triangle.hpp"

namespace algorithms::divide_and_conquer {
    std::vector<geometry::Triangle> triangulate(const std::vector<geometry::Point>& input_points);
}
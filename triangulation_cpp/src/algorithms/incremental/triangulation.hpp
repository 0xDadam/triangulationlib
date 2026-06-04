#pragma once
#include <vector>
#include "geometry/point.hpp"
#include "geometry/triangle.hpp"

namespace algorithms::incremental {
    std::vector<geometry::Triangle> triangulate(const std::vector<geometry::Point>& input_points, bool use_triangle_walk);
}
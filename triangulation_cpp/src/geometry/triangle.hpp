#pragma once
#include <array>

namespace geometry {
    struct Triangle {
        std::array<size_t, 3> vertices;
        
        Triangle(std::array<size_t, 3> v) : vertices(v) {}
    };
}
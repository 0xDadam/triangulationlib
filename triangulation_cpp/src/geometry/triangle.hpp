#pragma once
#include <array>

namespace geometry {
    struct Triangle {
        std::array<size_t, 3> vertices;

        Triangle(std::array<size_t, 3> v) : vertices(v) {}
        Triangle(const size_t a, const size_t b, const size_t c) : vertices(std::array<size_t, 3>{a, b, c}) {}
    };
}
#pragma once

namespace geometry {
    struct Point {
        double x;
        double y;
        
        Point(double x_val, double y_val) : x(x_val), y(y_val) {}
    };
}
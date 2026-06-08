#pragma once
#include "geometry/point.hpp"

namespace geometry {

    inline double ccw(const Point& a, const Point& b, const Point& c) {
        return ((b.x - a.x) * (c.y - a.y)) - ((b.y - a.y) * (c.x - a.x));
    }

    inline bool in_circle(const Point& a, const Point& b, const Point& c, const Point& d) {
        double adx = a.x - d.x;
        double ady = a.y - d.y;

        double bdx = b.x - d.x;
        double bdy = b.y - d.y;

        double cdx = c.x - d.x;
        double cdy = c.y - d.y;

        double alift = adx * adx + ady * ady;
        double blift = bdx * bdx + bdy * bdy;
        double clift = cdx * cdx + cdy * cdy;

        double det = alift * (bdx * cdy - cdx * bdy)
                   + blift * (cdx * ady - adx * cdy)
                   + clift * (adx * bdy - bdx * ady);

        return det > 0.0;
    }

}
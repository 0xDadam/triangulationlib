#include <boost/test/unit_test.hpp>
#include "geometry/functions.hpp"

using geometry::Point;

BOOST_AUTO_TEST_CASE(ccw_positive_for_left_turn) {
    Point a(0, 0), b(1, 0), c(0, 1);
    BOOST_CHECK_GT(geometry::ccw(a, b, c), 0.0);
}

BOOST_AUTO_TEST_CASE(ccw_negative_for_right_turn) {
    Point a(0, 0), b(1, 0), c(0, -1);
    BOOST_CHECK_LT(geometry::ccw(a, b, c), 0.0);
}

BOOST_AUTO_TEST_CASE(ccw_zero_for_collinear) {
    Point a(0, 0), b(1, 0), c(2, 0);
    BOOST_CHECK_SMALL(geometry::ccw(a, b, c), 1e-12);
}

BOOST_AUTO_TEST_CASE(in_circle_inside) {
    Point a(0, 0), b(1, 0), c(0, 1), d(0.2, 0.2);
    BOOST_CHECK(geometry::in_circle(a, b, c, d));
}

BOOST_AUTO_TEST_CASE(in_circle_outside) {
    Point a(0, 0), b(1, 0), c(0, 1), d(5, 5);
    BOOST_CHECK(!geometry::in_circle(a, b, c, d));
}

BOOST_AUTO_TEST_CASE(ccw_points_delegates) {
    std::vector<Point> pts = {{0, 0}, {1, 0}, {0, 1}};
    BOOST_CHECK_GT(geometry::ccw_points(0, 1, 2, pts), 0.0);
}

BOOST_AUTO_TEST_CASE(in_circle_points_delegates) {
    std::vector<Point> pts = {{0, 0}, {1, 0}, {0, 1}, {0.2, 0.2}};
    BOOST_CHECK(geometry::in_circle_points(0, 1, 2, 3, pts));
}
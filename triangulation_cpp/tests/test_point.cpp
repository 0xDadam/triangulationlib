#define BOOST_TEST_MODULE TriangulationTests
#include <boost/test/unit_test.hpp>
#include "geometry/point.hpp"

BOOST_AUTO_TEST_CASE(point_constructs_and_compares) {
    geometry::Point a(1.0, 2.0);
    geometry::Point b(1.0, 2.0);
    geometry::Point c(3.0, 4.0);

    BOOST_CHECK(a == b);
    BOOST_CHECK(a != c);
}

BOOST_AUTO_TEST_CASE(point_fields_accessible) {
    geometry::Point p(3.5, -1.5);
    BOOST_CHECK_EQUAL(p.x, 3.5);
    BOOST_CHECK_EQUAL(p.y, -1.5);
}
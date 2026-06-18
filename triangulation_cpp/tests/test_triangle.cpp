#include <boost/test/unit_test.hpp>
#include "geometry/triangle.hpp"

BOOST_AUTO_TEST_CASE(triangle_from_array) {
    geometry::Triangle t(std::array<size_t, 3>{0, 1, 2});
    BOOST_CHECK_EQUAL(t.vertices[0], 0u);
    BOOST_CHECK_EQUAL(t.vertices[1], 1u);
    BOOST_CHECK_EQUAL(t.vertices[2], 2u);
}

BOOST_AUTO_TEST_CASE(triangle_from_three_indices) {
    geometry::Triangle t(5, 10, 15);
    BOOST_CHECK_EQUAL(t.vertices[0], 5u);
    BOOST_CHECK_EQUAL(t.vertices[1], 10u);
    BOOST_CHECK_EQUAL(t.vertices[2], 15u);
}
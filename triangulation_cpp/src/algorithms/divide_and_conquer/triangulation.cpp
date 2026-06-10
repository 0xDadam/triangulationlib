#include "triangulation.hpp"
#include <algorithm>
#include <cassert>
#include <utility>

#include "quad_edge.hpp"
#include "geometry/functions.hpp"

namespace algorithms::divide_and_conquer {

    std::pair<EdgeEntry, EdgeEntry> build_triangulation(
        size_t start, size_t end,
        const std::vector<geometry::Point>& points,
        const std::shared_ptr<QuadEdgeGraph>& graph);

    std::pair<EdgeEntry, EdgeEntry> merge_triangulations(
        EdgeEntry ldo_left, EdgeEntry rdo_left,
        EdgeEntry ldo_right, EdgeEntry rdo_right,
        const std::vector<geometry::Point>& points,
        const std::shared_ptr<QuadEdgeGraph>& graph);

    // Helper for in_circle check with edge origins
    bool in_circle_points_unbox(
        size_t a, size_t b, size_t c, size_t d,
        const std::vector<geometry::Point>& points) {
        return in_circle_points(a, b, c, d, points);
    }

    bool to_left(size_t origin, size_t dest, size_t point,
                 const std::vector<geometry::Point>& points) {
        return ccw_points(origin, dest, point, points) > 0.0;
    }

    bool to_right(size_t origin, size_t dest, size_t point,
                  const std::vector<geometry::Point>& points) {
        return ccw_points(origin, dest, point, points) < 0.0;
    }

    std::vector<geometry::Triangle> triangulate(
        const std::vector<geometry::Point>& input_points) {

        // Create sorted indices
        std::vector<size_t> sorted_to_original(input_points.size());
        for (size_t i = 0; i < input_points.size(); ++i) {
            sorted_to_original[i] = i;
        }

        // Sort indices based on point comparison (lexicographic: x then y)
        std::sort(sorted_to_original.begin(), sorted_to_original.end(),
            [&input_points](size_t a, size_t b) {
                return input_points[a] < input_points[b];
            });

        // Create sorted points array
        std::vector<geometry::Point> sorted_points;
        sorted_points.reserve(input_points.size());
        for (size_t i : sorted_to_original) {
            sorted_points.push_back(input_points[i]);
        }

        // Build triangulation
        const auto graph = QuadEdgeGraph::create();
        build_triangulation(0, sorted_points.size(), sorted_points, graph);

        // Extract triangles
        return graph->extract_all_triangles(sorted_points, sorted_to_original);
    }


    std::pair<EdgeEntry, EdgeEntry> build_triangulation(
        size_t start, size_t end,
        const std::vector<geometry::Point>& points,
        const std::shared_ptr<QuadEdgeGraph>& graph) {

        size_t n = end - start;

        if (n == 2) {
            EdgeEntry a = graph->make_edge(start, start + 1);
            return {a, a.sym()};
        }

        if (n == 3) {
            EdgeEntry a = graph->make_edge(start, start + 1);
            EdgeEntry b = graph->make_edge(start + 1, start + 2);
            graph->splice(a.sym(), b);

            double c_val = ccw_points(start, start + 1, start + 2, points);

            if (c_val > 0.0) {
                // Counter-clockwise
                graph->connect(b, a);
                return {a, b.sym()};
            } else if (c_val < 0.0) {
                // Clockwise
                EdgeEntry c = graph->connect(b, a);
                return {c.sym(), c};
            } else {
                // Collinear
                return {a, b.sym()};
            }
        }

        // Divide and conquer
        const size_t mid = (start + end) / 2;
        auto [ldo_left, rdo_left] = build_triangulation(start, mid, points, graph);
        auto [ldo_right, rdo_right] = build_triangulation(mid, end, points, graph);

        return merge_triangulations(ldo_left, rdo_left, ldo_right, rdo_right, points, graph);
    }

    std::pair<EdgeEntry, EdgeEntry> merge_triangulations(
        EdgeEntry ldo_left, EdgeEntry rdo_left,
        EdgeEntry ldo_right, EdgeEntry rdo_right,
        const std::vector<geometry::Point>& points,
        const std::shared_ptr<QuadEdgeGraph>& graph) {

        // Find lower common tangent
        EdgeEntry ldo_inner = std::move(rdo_left);
        EdgeEntry rdo_inner = std::move(ldo_right);

        while (true) {
            if (to_left(ldo_inner.get_origin(), rdo_inner.get_origin(),
                        ldo_inner.get_dest(), points)) {
                ldo_inner = ldo_inner.lnext();
            } else if (to_right(rdo_inner.get_origin(), ldo_inner.get_origin(),
                               rdo_inner.get_dest(), points)) {
                rdo_inner = rdo_inner.rprev();
            } else {
                break;
            }
        }

        EdgeEntry base_lre = graph->connect(rdo_inner.sym(), ldo_inner);

        if (ldo_left.get_origin() == ldo_inner.get_origin()) {
            ldo_left = base_lre.sym();
        }
        if (rdo_right.get_origin() == rdo_inner.get_origin()) {
            rdo_right = base_lre;
        }

        // The zipper - merge triangulations
        while (true) {
            // Find left candidate
            EdgeEntry lcand = base_lre.sym().onext();
            if (to_right(base_lre.get_origin(), base_lre.get_dest(),
                        lcand.get_dest(), points)) {
                while (in_circle_points_unbox(
                    base_lre.get_dest(), base_lre.get_origin(),
                    lcand.get_dest(), lcand.onext().get_dest(), points)) {
                    EdgeEntry t = lcand.onext();
                    graph->delete_edge(lcand);
                    lcand = t;
                }
            }

            // Find right candidate
            EdgeEntry rcand = base_lre.oprev();
            if (to_right(base_lre.get_origin(), base_lre.get_dest(),
                        rcand.get_dest(), points)) {
                while (in_circle_points_unbox(
                    base_lre.get_dest(), base_lre.get_origin(),
                    rcand.get_dest(), rcand.oprev().get_dest(), points)) {
                    EdgeEntry t = rcand.oprev();
                    graph->delete_edge(rcand);
                    rcand = t;
                }
            }

            bool l_valid = to_right(base_lre.get_origin(), base_lre.get_dest(),
                                   lcand.get_dest(), points);
            bool r_valid = to_right(base_lre.get_origin(), base_lre.get_dest(),
                                   rcand.get_dest(), points);

            if (!l_valid && !r_valid) {
                break;
            }

            if (!l_valid || (r_valid && in_circle_points_unbox(
                lcand.get_dest(), lcand.get_origin(),
                rcand.get_origin(), rcand.get_dest(), points))) {
                base_lre = graph->connect(rcand, base_lre.sym());
            } else {
                base_lre = graph->connect(base_lre.sym(), lcand.sym());
            }
        }

        return {ldo_left, rdo_right};
    }

} // namespace algorithms::divide_and_conquer
#include "triangulation.hpp"
#include "geometry/functions.hpp"
#include <array>
#include <limits>
#include <cmath>
#include <algorithm>

namespace algorithms::incremental {

    const size_t NO_NEIGHBOR = std::numeric_limits<size_t>::max();
    const double EPS = 1e-12;

    struct WorkingTriangle {
        std::array<size_t, 3> vertices;
        std::array<size_t, 3> neighbors;
        bool active;

        WorkingTriangle(std::array<size_t, 3> v, std::array<size_t, 3> n) 
            : vertices(v), neighbors(n), active(true) {}
    };

    class DelaunayTriangulation {
    public:
        std::vector<geometry::Point> points;
        std::vector<WorkingTriangle> triangles;
        size_t last_added_tri = 0;

        DelaunayTriangulation(const std::vector<geometry::Point>& input_points) {
            points.reserve(input_points.size() + 3);
            points = input_points;

            double min_x = std::numeric_limits<double>::max();
            double min_y = std::numeric_limits<double>::max();
            double max_x = std::numeric_limits<double>::lowest();
            double max_y = std::numeric_limits<double>::lowest();

            for (const auto& p : points) {
                if (p.x < min_x) min_x = p.x;
                if (p.y < min_y) min_y = p.y;
                if (p.x > max_x) max_x = p.x;
                if (p.y > max_y) max_y = p.y;
            }

            double dx = max_x - min_x;
            double dy = max_y - min_y;
            double delta_max = std::max(dx, dy);
            double mid_x = (min_x + max_x) / 2.0;
            double mid_y = (min_y + max_y) / 2.0;

            geometry::Point p1(mid_x - 20.0 * delta_max, mid_y - delta_max);
            geometry::Point p2(mid_x + 20.0 * delta_max, mid_y - delta_max);
            geometry::Point p3(mid_x, mid_y + 20.0 * delta_max);

            size_t p1_idx = points.size();
            size_t p2_idx = points.size() + 1;
            size_t p3_idx = points.size() + 2;

            points.push_back(p1);
            points.push_back(p2);
            points.push_back(p3);

            triangles.reserve(points.size() * 2);
            triangles.emplace_back(std::array<size_t, 3>{p1_idx, p2_idx, p3_idx}, 
                                   std::array<size_t, 3>{NO_NEIGHBOR, NO_NEIGHBOR, NO_NEIGHBOR});
        }

        void add_point(size_t point_idx, bool use_triangle_walk) {
            const auto& p = points[point_idx];
            std::vector<size_t> bad_triangles;

            if (!use_triangle_walk) {
                for (size_t i = 0; i < triangles.size(); ++i) {
                    if (triangles[i].active) {
                        if (geometry::in_circle(points[triangles[i].vertices[0]], 
                                                points[triangles[i].vertices[1]], 
                                                points[triangles[i].vertices[2]], p)) {
                            bad_triangles.push_back(i);
                        }
                    }
                }
            } else {
                size_t curr = last_added_tri;
                if (!triangles[curr].active) {
                    for (size_t i = triangles.size(); i-- > 0;) {
                        if (triangles[i].active) { curr = i; break; }
                    }
                }

                size_t fallback_counter = 0;
                while (true) {
                    const auto& tri = triangles[curr];
                    bool moved = false;
                    for (size_t i = 0; i < 3; ++i) {
                        const auto& a = points[tri.vertices[i]];
                        const auto& b = points[tri.vertices[(i + 1) % 3]];
                        if (geometry::ccw(a, b, p) < -EPS) {
                            if (tri.neighbors[i] != NO_NEIGHBOR) {
                                curr = tri.neighbors[i];
                                moved = true;
                                break;
                            }
                        }
                    }
                    fallback_counter++;
                    if (!moved || fallback_counter > triangles.size()) break;
                }

                std::vector<size_t> stack = {curr};
                bad_triangles.push_back(curr);

                while (!stack.empty()) {
                    size_t t_idx = stack.back();
                    stack.pop_back();
                    
                    for (size_t n_idx : triangles[t_idx].neighbors) {
                        if (n_idx != NO_NEIGHBOR && triangles[n_idx].active && 
                            std::find(bad_triangles.begin(), bad_triangles.end(), n_idx) == bad_triangles.end()) {
                            
                            const auto& n_tri = triangles[n_idx];
                            if (geometry::in_circle(points[n_tri.vertices[0]], 
                                                    points[n_tri.vertices[1]], 
                                                    points[n_tri.vertices[2]], p)) {
                                bad_triangles.push_back(n_idx);
                                stack.push_back(n_idx);
                            }
                        }
                    }
                }
            }

            if (bad_triangles.empty()) return;

            struct Edge { size_t p1, p2, outer; };
            std::vector<Edge> boundary;

            for (size_t bad_idx : bad_triangles) {
                auto& tri = triangles[bad_idx];
                for (size_t i = 0; i < 3; ++i) {
                    size_t n_idx = tri.neighbors[i];
                    bool is_boundary = (n_idx == NO_NEIGHBOR) || 
                                       (std::find(bad_triangles.begin(), bad_triangles.end(), n_idx) == bad_triangles.end());
                    if (is_boundary) {
                        boundary.push_back({tri.vertices[i], tri.vertices[(i + 1) % 3], n_idx});
                    }
                }
                tri.active = false;
            }

            std::vector<size_t> new_triangles_indices;
            size_t base_idx = triangles.size();

            for (size_t j = 0; j < boundary.size(); ++j) {
                size_t new_tri_idx = base_idx + j;
                triangles.emplace_back(std::array<size_t, 3>{boundary[j].p1, boundary[j].p2, point_idx},
                                       std::array<size_t, 3>{boundary[j].outer, NO_NEIGHBOR, NO_NEIGHBOR});
                new_triangles_indices.push_back(new_tri_idx);
            }

            for (size_t j = 0; j < boundary.size(); ++j) {
                size_t p1 = boundary[j].p1;
                size_t p2 = boundary[j].p2;
                size_t new_tri_idx = base_idx + j;
                size_t n_idx = boundary[j].outer;

                if (n_idx != NO_NEIGHBOR) {
                    auto& n_tri = triangles[n_idx];
                    for (size_t k = 0; k < 3; ++k) {
                        if (n_tri.vertices[k] == p2 && n_tri.vertices[(k + 1) % 3] == p1) {
                            n_tri.neighbors[k] = new_tri_idx;
                            break;
                        }
                    }
                }
            }

            for (size_t t1_idx : new_triangles_indices) {
                for (size_t t2_idx : new_triangles_indices) {
                    if (t1_idx == t2_idx) continue;
                    size_t v1_1 = triangles[t1_idx].vertices[1];
                    size_t v1_0 = triangles[t1_idx].vertices[0];
                    size_t v2_0 = triangles[t2_idx].vertices[0];
                    size_t v2_1 = triangles[t2_idx].vertices[1];

                    if (v1_1 == v2_0) triangles[t1_idx].neighbors[1] = t2_idx;
                    if (v1_0 == v2_1) triangles[t1_idx].neighbors[2] = t2_idx;
                }
            }

            if (!new_triangles_indices.empty()) {
                last_added_tri = new_triangles_indices[0];
            }
        }
    };

    std::vector<geometry::Triangle> triangulate(const std::vector<geometry::Point>& input_points, bool use_triangle_walk) {
        if (input_points.size() < 3) return {};

        DelaunayTriangulation delaunay(input_points);

        for (size_t i = 0; i < input_points.size(); ++i) {
            delaunay.add_point(i, use_triangle_walk);
        }

        std::vector<geometry::Triangle> result;
        size_t super_p1 = input_points.size();
        size_t super_p2 = input_points.size() + 1;
        size_t super_p3 = input_points.size() + 2;

        for (const auto& tri : delaunay.triangles) {
            if (tri.active) {
                bool is_super = false;
                for (size_t v : tri.vertices) {
                    if (v == super_p1 || v == super_p2 || v == super_p3) { is_super = true; break; }
                }
                if (!is_super) {
                    result.push_back(geometry::Triangle(tri.vertices));
                }
            }
        }
        return result;
    }

}
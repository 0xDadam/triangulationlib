#pragma once
#include <array>
#include <cassert>
#include <map>
#include <memory>
#include <unordered_set>
#include <utility>
#include <vector>

#include "geometry/triangle.hpp"
#include "SlotMap.hpp"

namespace algorithms::divide_and_conquer {
    class QuadEdgeGraph;

    class EdgeEntry {
    private:
        QuadEdgeGraph* graph;
        Key qe_key;
        uint8_t index = 0;

    public:
        EdgeEntry(QuadEdgeGraph* g, const Key k, const uint8_t idx)
        : graph(g), qe_key(k), index(idx) {}

        [[nodiscard]] EdgeEntry rot() const {
            return {
                graph,
                qe_key,
                static_cast<uint8_t>((index + 1) % 4)
            };
        }

        [[nodiscard]] EdgeEntry sym() const {
            return {
                graph,
                qe_key,
                static_cast<uint8_t>((index + 2) % 4)
            };
        }

        [[nodiscard]] EdgeEntry rot_inv() const {
            return {
                graph,
                qe_key,
                static_cast<uint8_t>((index + 3) % 4)
            };
        }

        EdgeEntry &next();
        [[nodiscard]] const EdgeEntry &next() const;

        // These call the mesh inline to look up the next pointers
        [[nodiscard]] EdgeEntry onext() const { return next(); }
        [[nodiscard]] EdgeEntry oprev() const { return rot().onext().rot(); }
        [[nodiscard]] EdgeEntry lnext() const { return rot_inv().onext().rot(); }
        [[nodiscard]] EdgeEntry lprev() const { return onext().sym(); }
        [[nodiscard]] EdgeEntry rnext() const { return rot().onext().rot_inv(); }
        [[nodiscard]] EdgeEntry rprev() const { return sym().onext(); }
        [[nodiscard]] EdgeEntry dnext() const { return sym().onext().sym(); }
        [[nodiscard]] EdgeEntry dprev() const { return rot_inv().onext().rot_inv(); }

        // Data Getters / Setters
        [[nodiscard]] size_t get_origin() const;
        void set_origin(size_t value);

        [[nodiscard]] size_t get_dest() const { return sym().get_origin(); }
        void set_dest(const size_t value) { sym().set_origin(value); }

        [[nodiscard]] Key get_key() const {
            return qe_key;
        }

        bool operator==(const EdgeEntry & edge_entry) const {
            return (qe_key == edge_entry.qe_key && index == edge_entry.index);
        };
    };

    struct QuadEdge {
        std::array<size_t, 2> values;
        std::array<EdgeEntry, 4> nexts;

        QuadEdge(const size_t origin, const size_t dest, const Key key, QuadEdgeGraph* graph) :
            values ({origin, dest}),
            nexts({
                EdgeEntry{graph, key, 0},
                EdgeEntry{graph, key, 3},
                EdgeEntry{graph, key, 2},
                EdgeEntry{graph, key, 1}
            }) {}
    };

    class QuadEdgeGraph{
        friend class EdgeEntry;
        SlotMap<QuadEdge> quad_edge_map;

    public:
        EdgeEntry make_edge(size_t origin, size_t dest) {
            const auto key = quad_edge_map.insert_with_key(
                [origin, dest, this](const Key k) {
                    return QuadEdge{
                        origin, dest, k, this
                    };
                }
            );
            return EdgeEntry{this, key, 0};
        }

        void splice(EdgeEntry a, EdgeEntry b) {
            auto alpha = a.onext().rot();
            auto beta = b.onext().rot();

            std::swap(a.next(), b.next());
            std::swap(alpha.next(), beta.next());
        }

        EdgeEntry connect(const EdgeEntry& a, const EdgeEntry& b) {
            const auto e = make_edge(a.get_dest(), b.get_origin());
            splice(e, a.lnext());
            splice(e.sym(), b);
            return e;
        }

        void delete_edge(const EdgeEntry& edge) {
            splice(edge, edge.oprev());
            splice(edge.sym(), edge.sym().oprev());

            quad_edge_map.remove(edge.get_key());
        }

        std::vector<geometry::Triangle> extract_all_triangles(
            const std::vector<geometry::Point> & points,
            const std::vector<unsigned long> & sorted_to_original) {

            // Dedup key: the sorted vertex tuple of the *raw* traversal
            // (independent of edge direction). Value: the CCW vertex triple
            // so the final emitted triangles have consistent orientation.
            std::map<std::array<size_t, 3>, std::array<size_t, 3>> canonical;

            for (const auto& key : quad_edge_map.get_all_keys()) {
                for (uint8_t edge_index : {0, 2}) {
                    EdgeEntry e(this, key, edge_index);

                    auto lnext = e.lnext();
                    if (lnext.lnext().lnext() != e) {
                        continue;
                    }

                    size_t v1 = e.get_origin();
                    size_t v2 = e.get_dest();
                    size_t v3 = lnext.get_dest();

                    const auto& p1 = points[v1];
                    const auto& p2 = points[v2];
                    const auto& p3 = points[v3];

                    auto area = (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x);
                    std::array<size_t, 3> ccw_vertices;
                    if (area > 0) {
                        ccw_vertices = { v1, v2, v3 };
                    } else if (area < 0) {
                        ccw_vertices = { v1, v3, v2 };
                    } else {
                        ccw_vertices = { v1, v2, v3 };
                    }

                    std::array<size_t, 3> dedup_key = { v1, v2, v3 };
                    std::sort(dedup_key.begin(), dedup_key.end());
                    canonical.emplace(dedup_key, ccw_vertices);
                }
            }

            std::vector<geometry::Triangle> triangles;
            triangles.reserve(canonical.size());
            for (const auto& [_, ccw_vertices] : canonical) {
                triangles.emplace_back(
                    sorted_to_original[ccw_vertices[0]],
                    sorted_to_original[ccw_vertices[1]],
                    sorted_to_original[ccw_vertices[2]]
                );
            }

            return triangles;
        }

    };

    inline EdgeEntry &EdgeEntry::next() {
        return graph->quad_edge_map.get(qe_key).nexts[index];
    }

    inline const EdgeEntry& EdgeEntry::next() const {
        return graph->quad_edge_map.get(qe_key).nexts[index];
    }

    inline size_t EdgeEntry::get_origin() const {
        assert(index % 2 == 0 && "Trying to access dual edge data");
        return graph->quad_edge_map.get(qe_key).values[index / 2];
    }

    inline void EdgeEntry::set_origin(const size_t value) {
        assert(index % 2 == 0 && "Trying to access dual edge data");
        graph->quad_edge_map.get(qe_key).values[index] = value;
    }
}
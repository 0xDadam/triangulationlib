#include "quad_edge.hpp"

#include <array>
#include <vector>
#include <cstdint>


class QuadEdgeGraph;

class EdgeEntry {
private:
    QuadEdgeGraph* graph = nullptr;
    size_t qe_key = 0;
    uint8_t index = 0;

public:
    EdgeEntry(QuadEdgeGraph* g, const size_t k, const uint8_t idx) : graph(g), qe_key(k), index(idx) {}

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

    // These call the mesh inline to look up the next pointers
    [[nodiscard]] EdgeEntry onext() const;
    [[nodiscard]] EdgeEntry oprev() const { return rot().onext().rot(); }
    [[nodiscard]] EdgeEntry lnext() const { return rot_inv().onext().rot(); }
    [[nodiscard]] EdgeEntry lprev() const { return sym().onext(); }
    [[nodiscard]] EdgeEntry rnext() const { return rot().onext().rot_inv(); }
    [[nodiscard]] EdgeEntry rprev() const { return sym().onext(); }
    [[nodiscard]] EdgeEntry dnext() const { return sym().onext().sym(); }
    [[nodiscard]] EdgeEntry dprev() const { return rot_inv().onext().rot_inv(); }

    // Data Getters / Setters
    [[nodiscard]] int get_origin() const;
    void set_origin(int value);

    [[nodiscard]] int get_dest() const { return sym().get_origin(); }
    void set_dest(int value) const { sym().set_origin(value); }
};

struct QuadEdge {
    std::array<uint32_t, 2> values{};
    std::array<EdgeEntry, 4> nexts;
    bool valid = false;
};

class QuadEdgeGraph {
    std::vector<QuadEdge> edges_pool;
    std::vector<size_t> free_indexes;

public:
    EdgeEntry make_edge(int origin, int dest) {
        size_t new_index;
        if (free_indexes.empty()) {
            edges_pool.emplace_back()
        }
    }
};



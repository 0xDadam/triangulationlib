#pragma once
#include <cstdint>
#include <deque>
#include <vector>
#include <expected>

#include "quad_edge.hpp"

namespace algorithms::divide_and_conquer {
    struct Key { uint32_t index; uint32_t generation;

        bool operator==(const Key & key) const {
            return (index == key.index && generation == key.generation);
        };
    };

    template <typename T>
    struct Slot { T value; uint32_t generation; };

    template <typename T>
    class SlotMap {
    private:
        std::deque<Slot<T>> slots{};
        std::vector<uint32_t> free_slots{};

        //always requires inputting a key after
        Key get_next_key() {
            if (free_slots.empty()) {
                return {static_cast<uint32_t>(slots.size()), 0};
            }
            const uint32_t index = free_slots.back();
            free_slots.pop_back();
            return {index, slots[index].generation};
        }

        void insert_at(const Key key, T value) {
            if (key.index >= slots.size()) {
                slots.push_back( {value, key.generation} );
                return;
            }
            slots[key.index] = {value, key.generation};
        }

    public:
        template <typename F>
        requires std::invocable<F, Key>
        Key insert_with_key(F&& f) {
            const Key key = get_next_key();
            const T value = std::forward<F>(f)(key);
            insert_at(key, value);
            return key;
        }

        Key insert(T value) {
            const Key key = get_next_key();
            insert_at(key, value);
            return key;
        }

        T& get(const Key key) {
            if (key.index >= slots.size() || key.generation != slots[key.index].generation) {
                throw std::runtime_error("Trying to use an invalid or stale key.");
            }
            return slots[key.index].value;
        }

        void remove(const Key key) {
            if (key.index < slots.size() && slots[key.index].generation == key.generation) {
                ++slots[key.index].generation;
                free_slots.push_back(key.index);
            }
        }

        [[nodiscard]] std::vector<Key> get_all_keys() const {
            std::vector<Key> keys;
            for (size_t i = 0; i < slots.size(); ++i) {
                // Skip free slots if you track them separately
                if (std::ranges::count(free_slots, static_cast<uint32_t>(i)) > 0) {
                    continue;
                }
                keys.push_back({static_cast<uint32_t>(i), slots[i].generation});
            }
            return keys;
        }
    };
}

#pragma once
#include <cstdint>
#include <vector>
#include <expected>

struct Key { uint32_t index; uint32_t generation; };

template <typename T>
struct Slot { T value; uint32_t generation; };

template <typename T>
class SlotMap {
private:
    std::vector<Slot<T>> slots{};
    std::vector<uint32_t> free_slots{};

    //always requires inputting a key after
    Key get_next_key() {
        if (free_slots.empty()) {
            return {slots.size(), 0};
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

    void erase(const Key key) {
        if (key.index < slots.size() && slots[key.index].generation == key.generation) {
            ++slots[key.index].generation;
            free_slots.push_back(key.index);
        }
    }
};

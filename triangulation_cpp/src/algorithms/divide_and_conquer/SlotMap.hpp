//
// Created by Hubert on 09/06/2026.
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
        return {index, slots[index].generation + 1};
    }
public:
    template <typename F>
    requires std::invocable<F, Key>
    Key insert_with_key(F&& f) {
        Key key = get_next_key();
        T value = std::forward<F>(f)(key);
        return insert(key, value);
    }

    Key insert(Key key, T value) {
        slots[key.index] = {value, key.generation};
        return key;
    }

    T get(Key key) {
        if (key.index >= slots.size() || key.generation != slots[key.index].generation) {
            throw std::runtime_error("Trying to access an invalid key. Has the entry been removed?");
        }
        return slots[key.index].value;
    }
};

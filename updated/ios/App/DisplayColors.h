#pragma once
#include <cstdint>
#include <vector>

namespace updated_display {
// SceneKit display input only. Keep the recovered/exported byte RGBA untouched.
inline std::vector<float> normalizedRGBA(const std::vector<uint8_t>& bytes) {
    std::vector<float> result(bytes.size());
    for (std::size_t i = 0; i < bytes.size(); ++i)
        result[i] = static_cast<float>(bytes[i]) / 255.0f;
    return result;
}
}

#include "DisplayColors.h"
#include <cmath>
#include <iostream>
#include <stdexcept>

int main() {
    std::vector<uint8_t> bytes;
    for (int value = 0; value < 256; ++value)
        for (int channel = 0; channel < 4; ++channel)
            bytes.push_back(static_cast<uint8_t>(value));
    const auto original = bytes;
    const auto floats = updated_display::normalizedRGBA(bytes);
    if (bytes != original || floats.size() != bytes.size())
        throw std::runtime_error("Display conversion modified saved source/length");
    for (std::size_t i = 0; i < floats.size(); ++i) {
        const double expected = static_cast<double>(bytes[i]) / 255.0;
        if (!std::isfinite(floats[i]) || floats[i] < 0 || floats[i] > 1 ||
            std::abs(floats[i] - expected) > 6e-8)
            throw std::runtime_error("RGBA channel is not normalized correctly");
    }
    const auto teal = updated_display::normalizedRGBA({50, 215, 206, 255});
    if (!(teal[0] < teal[2] && teal[2] < teal[1]) || teal[3] != 1.0f)
        throw std::runtime_error("Known Volume display color lost channel/alpha order");
    if (!updated_display::normalizedRGBA({}).empty())
        throw std::runtime_error("Empty array conversion changed length");
    std::cout << "PASS: 256 byte values in every RGBA channel, range/error, source preservation, teal/alpha and empty input\n";
}

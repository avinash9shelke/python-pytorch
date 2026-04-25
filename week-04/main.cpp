#include <cstdio>
#include <chrono>
#include <cstdint>

static inline double calculate_optimized(uint32_t iterations) {
    double result = 1.0;
    double d1 = 3.0;  // 4*i - 1 starting at i=1
    double d2 = 5.0;  // 4*i + 1 starting at i=1

    uint32_t i = 0;
    uint32_t n = iterations;
    uint32_t limit = n & ~15u; // multiple of 16

    for (; i < limit; i += 16) {
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;

        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;

        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;

        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
        result -= 1.0 / d1; result += 1.0 / d2; d1 += 4.0; d2 += 4.0;
    }

    for (; i < n; ++i) {
        result -= 1.0 / d1;
        result += 1.0 / d2;
        d1 += 4.0;
        d2 += 4.0;
    }

    return result;
}

int main() {
    const uint32_t iterations = 200000000u;
    const int param1 = 4;
    const int param2 = 1;

    auto start_time = std::chrono::steady_clock::now();
    double result = calculate_optimized(iterations) * 4.0;
    auto end_time = std::chrono::steady_clock::now();

    double elapsed = std::chrono::duration<double>(end_time - start_time).count();

    std::printf("Result: %.12f\n", result);
    std::printf("Execution Time: %.6f seconds\n", elapsed);
    return 0;
}
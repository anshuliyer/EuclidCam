#ifndef KODAK_35MM_H
#define KODAK_35MM_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Apply a Kodak 35mm film filter with:
 * - Faded/matte shadows (black point 0.05)
 * - Softened whites (white point 0.95)
 * - Mid-tone contrast boost (gamma 1.1-1.2)
 * - Punchier saturation (1.1x)
 * - Subtle 35mm film grain (1px)
 */
void apply_kodak_35mm_filter(unsigned char* data, int width, int height, int channels);

#ifdef __cplusplus
}
#endif

#endif // KODAK_35MM_H

#include "hdrs/kodak_35mm.h"
#include "hdrs/stb_image.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// Kodak 35mm film emulation parameters
#define BLACK_POINT 0.05f           // Faded/matte shadows
#define WHITE_POINT 0.95f           // Softened, non-piercing whites
#define GAMMA_VALUE 1.15f           // Mid-tone contrast boost (1.1-1.2 range)
#define SATURATION_BOOST 1.1f       // Punchier reds/yellows (film saturation)
#define GRAIN_AMOUNT 0.008f         // Subtle 35mm film grain
#define GRAIN_SIZE 1                // 1 pixel grain size (35mm, not 16mm)
#define COLOR_CAST_WARMTH 1.03f     // Slight warm color cast
#define COLOR_CAST_BLUE 0.97f       // Slight blue reduction
#define HIGHLIGHT_BLOOM 0.08f       // Slight highlight bloom
#define FADE_AMOUNT 0.03f           // Film fade/exposure compensation

static float clamp(float x, float min, float max) {
    return x < min ? min : (x > max ? max : x);
}

// Apply black/white point compression (faded, matte look)
static void apply_point_compression(unsigned char* data, int width, int height, int channels) {
    for (int i = 0; i < width * height * channels; i++) {
        float pixel = data[i] / 255.0f;
        
        // Black point: compress shadows
        if (pixel < BLACK_POINT) {
            pixel = pixel / BLACK_POINT * BLACK_POINT;
        }
        
        // White point: compress highlights
        if (pixel > WHITE_POINT) {
            pixel = WHITE_POINT + (pixel - WHITE_POINT) * (1.0f - WHITE_POINT);
        }
        
        data[i] = (unsigned char)(clamp(pixel, 0.0f, 1.0f) * 255.0f);
    }
}

// Apply gamma correction for mid-tone boost
static void apply_gamma_correction(unsigned char* data, int width, int height, int channels) {
    float inv_gamma = 1.0f / GAMMA_VALUE;
    
    for (int i = 0; i < width * height * channels; i++) {
        float pixel = data[i] / 255.0f;
        pixel = powf(pixel, inv_gamma);
        data[i] = (unsigned char)(clamp(pixel, 0.0f, 1.0f) * 255.0f);
    }
}

// RGB to HSL color space conversion
static void rgb_to_hsl(float r, float g, float b, float* h, float* s, float* l) {
    float max = fmaxf(fmaxf(r, g), b);
    float min = fminf(fminf(r, g), b);
    *l = (max + min) * 0.5f;

    if (max == min) {
        *h = *s = 0.0f;
    } else {
        float d = max - min;
        *s = *l > 0.5f ? d / (2.0f - max - min) : d / (max + min);
        
        if (max == r) {
            *h = (g - b) / d + (g < b ? 6.0f : 0.0f);
        } else if (max == g) {
            *h = (b - r) / d + 2.0f;
        } else {
            *h = (r - g) / d + 4.0f;
        }
        *h /= 6.0f;
    }
}

// HSL to RGB color space conversion
static float hue_to_rgb(float p, float q, float t) {
    if (t < 0.0f) t += 1.0f;
    if (t > 1.0f) t -= 1.0f;
    if (t < 1.0f/6.0f) return p + (q - p) * 6.0f * t;
    if (t < 1.0f/2.0f) return q;
    if (t < 2.0f/3.0f) return p + (q - p) * (2.0f/3.0f - t) * 6.0f;
    return p;
}

static void hsl_to_rgb(float h, float s, float l, float* r, float* g, float* b) {
    if (s == 0.0f) {
        *r = *g = *b = l;
    } else {
        float q = l < 0.5f ? l * (1.0f + s) : l + s - l * s;
        float p = 2.0f * l - q;
        *r = hue_to_rgb(p, q, h + 1.0f/3.0f);
        *g = hue_to_rgb(p, q, h);
        *b = hue_to_rgb(p, q, h - 1.0f/3.0f);
    }
}

// Boost saturation for punchier film look
static void apply_saturation_boost(unsigned char* data, int width, int height, int channels) {
    if (channels < 3) return;
    
    for (int i = 0; i < width * height; i++) {
        int idx = i * channels;
        float r = data[idx] / 255.0f;
        float g = data[idx + 1] / 255.0f;
        float b = data[idx + 2] / 255.0f;
        
        float h, s, l;
        rgb_to_hsl(r, g, b, &h, &s, &l);
        
        // Boost saturation
        s = clamp(s * SATURATION_BOOST, 0.0f, 1.0f);
        
        hsl_to_rgb(h, s, l, &r, &g, &b);
        
        data[idx] = (unsigned char)(clamp(r, 0.0f, 1.0f) * 255.0f);
        data[idx + 1] = (unsigned char)(clamp(g, 0.0f, 1.0f) * 255.0f);
        data[idx + 2] = (unsigned char)(clamp(b, 0.0f, 1.0f) * 255.0f);
    }
}

// Apply warm color cast (slight warmth typical of Kodak 35mm film)
static void apply_color_cast(unsigned char* data, int width, int height, int channels) {
    if (channels < 3) return;
    
    for (int i = 0; i < width * height; i++) {
        int idx = i * channels;
        
        // Add warmth (increase red, maintain green, reduce blue)
        float r = (data[idx] / 255.0f) * COLOR_CAST_WARMTH;
        float g = data[idx + 1] / 255.0f;
        float b = (data[idx + 2] / 255.0f) * COLOR_CAST_BLUE;
        
        data[idx] = (unsigned char)(clamp(r, 0.0f, 1.0f) * 255.0f);
        data[idx + 1] = (unsigned char)(clamp(g, 0.0f, 1.0f) * 255.0f);
        data[idx + 2] = (unsigned char)(clamp(b, 0.0f, 1.0f) * 255.0f);
    }
}

// Add subtle film grain
static void add_film_grain(unsigned char* data, int width, int height, int channels) {
    srand(time(NULL));
    
    for (int y = 0; y < height; y += GRAIN_SIZE) {
        for (int x = 0; x < width; x += GRAIN_SIZE) {
            // Generate single grain value per grain block
            float grain = (rand() / (float)RAND_MAX - 0.5f) * 2.0f * GRAIN_AMOUNT;
            
            // Apply grain to block
            for (int dy = 0; dy < GRAIN_SIZE && (y + dy) < height; dy++) {
                for (int dx = 0; dx < GRAIN_SIZE && (x + dx) < width; dx++) {
                    int idx = ((y + dy) * width + (x + dx)) * channels;
                    
                    for (int c = 0; c < channels; c++) {
                        float pixel = data[idx + c] / 255.0f + grain;
                        data[idx + c] = (unsigned char)(clamp(pixel, 0.0f, 1.0f) * 255.0f);
                    }
                }
            }
        }
    }
}

// Apply subtle highlight bloom (characteristic of film)
static void apply_highlight_bloom(unsigned char* data, int width, int height, int channels) {
    for (int i = 0; i < width * height * channels; i++) {
        float pixel = data[i] / 255.0f;
        
        // Only bloom bright pixels
        if (pixel > 0.8f) {
            float bloom = (pixel - 0.8f) * HIGHLIGHT_BLOOM / 0.2f;
            pixel = clamp(pixel + bloom, 0.0f, 1.0f);
        }
        
        data[i] = (unsigned char)(pixel * 255.0f);
    }
}

// Apply film fade (slight desaturation and contrast reduction)
static void apply_film_fade(unsigned char* data, int width, int height, int channels) {
    for (int i = 0; i < width * height * channels; i++) {
        float pixel = data[i] / 255.0f;
        // Add slight fade by moving toward middle gray
        pixel = clamp(pixel + (0.5f - pixel) * FADE_AMOUNT, 0.0f, 1.0f);
        data[i] = (unsigned char)(pixel * 255.0f);
    }
}

// Main filter function
void apply_kodak_35mm_filter(unsigned char* data, int width, int height, int channels) {
    if (!data || width <= 0 || height <= 0 || channels < 3) {
        return;
    }

    // Apply filters in order:
    // 1. Point compression (black/white point crushing for matte look)
    apply_point_compression(data, width, height, channels);
    
    // 2. Gamma correction (mid-tone contrast boost)
    apply_gamma_correction(data, width, height, channels);
    
    // 3. Saturation boost (punchier film colors)
    apply_saturation_boost(data, width, height, channels);
    
    // 4. Color cast (warm Kodak film tone)
    apply_color_cast(data, width, height, channels);
    
    // 5. Film fade (characteristic of aged film)
    apply_film_fade(data, width, height, channels);
    
    // 6. Highlight bloom (characteristic film blooming)
    apply_highlight_bloom(data, width, height, channels);
    
    // 7. Film grain (35mm grain size)
    add_film_grain(data, width, height, channels);
}

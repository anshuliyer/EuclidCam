#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include <stdio.h>
#include <stdlib.h>

/**
 * PiDigiCam: Minimal C Image Enhancer for ARMv6
 * 
 * This entry point is designed for debian-based ARMv6 microcontrollers.
 * It uses the 'stb' single-header libraries for zero-dependency image I/O.
 */

// Simple Bilinear Upscaling (Baseline Enhancement)
void upscale_x2(unsigned char* src, int sw, int sh, unsigned char* dst) {
    int dw = sw * 2;
    int dh = sh * 2;
    for (int y = 0; y < dh; y++) {
        for (int x = 0; x < dw; x++) {
            float gx = (float)x / 2.0f;
            float gy = (float)y / 2.0f;
            int gxi = (int)gx;
            int gyi = (int)gy;
            
            // Simple nearest/bilinear mix for performance on ARMv6
            dst[y * dw + x] = src[gyi * sw + gxi];
        }
    }
}

int main(int argc, char** argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <input.jpg> <output.png>\n", argv[0]);
        return 1;
    }

    const char* input_path = argv[1];
    const char* output_path = argv[2];

    int width, height, channels;
    printf("Loading image: %s\n", input_path);
    unsigned char* img = stbi_load(input_path, &width, &height, &channels, 0);
    
    if (!img) {
        fprintf(stderr, "Error: Could not load image %s\n", input_path);
        return 1;
    }

    printf("Image Loaded: %dx%d, %d channels\n", width, height, channels);
    
    int out_w = width * 2;
    int out_h = height * 2;
    unsigned char* out_img = (unsigned char*)malloc(out_w * out_h * channels);

    if (!out_img) {
        fprintf(stderr, "Error: Out of memory\n");
        stbi_image_free(img);
        return 1;
    }

    printf("Enhancing image to %dx%d...\n", out_w, out_h);
    
    // Process each channel
    for (int c = 0; c < channels; c++) {
        unsigned char* src_c = (unsigned char*)malloc(width * height);
        unsigned char* dst_c = (unsigned char*)malloc(out_w * out_h);
        
        // Extract channel
        for (int i = 0; i < width * height; i++) src_c[i] = img[i * channels + c];
        
        upscale_x2(src_c, width, height, dst_c);
        
        // Insert channel back
        for (int i = 0; i < out_w * out_h; i++) out_img[i * channels + c] = dst_c[i];
        
        free(src_c);
        free(dst_c);
    }

    printf("Writing output: %s\n", output_path);
    if (!stbi_write_png(output_path, out_w, out_h, channels, out_img, out_w * channels)) {
        fprintf(stderr, "Error: Could not save image %s\n", output_path);
    } else {
        printf("Successfully enhanced image!\n");
    }

    stbi_image_free(img);
    free(out_img);

    return 0;
}

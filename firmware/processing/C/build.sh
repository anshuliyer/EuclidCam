#!/bin/bash
# Simple build script for ARMv6 Debian
gcc -O3 -Wall -Wextra main.c -lm -o enhance
echo "Build complete. Run with: ./enhance <input.jpg> <output.png>"

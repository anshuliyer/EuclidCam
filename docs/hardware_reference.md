# EuclidCam Core Reference
This document outlines the core dependencies, execution commands, and hardware initialization steps for the EuclidCam firmware. You can use this as a reference for integrating the camera engine and touch UI into other SDK projects.

## Fresh OS Setup (From Scratch)

If you are starting from a completely blank, freshly flashed Raspberry Pi OS memory card, run these exact shell commands in order over SSH or a connected keyboard:

```bash
# 1. Update the system package lists
sudo apt-get update -y
sudo apt-get upgrade -y

# 2. Enable SPI and I2C interfaces (Required for Display and Hardware Sensors)
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

# 3. Clone the EuclidCam repository
git clone https://github.com/anshuliyer/EuclidCam.git
cd EuclidCam

# 4. Install all hardware and python dependencies via the Makefile
make install

# 5. Enable the EuclidCam systemd service to start automatically on boot
make service-install

# 6. Reboot the system to apply SPI/I2C changes and start the camera!
sudo reboot
```

## Hardware Wiring Guide

To ensure the firmware seamlessly communicates with the hardware, follow this pinout configuration.

### 1. ILI9341 Display (SPI)
- **MOSI / MISO / SCLK:** Standard Raspberry Pi SPI0 pins (GPIO 10, 9, 11)
- **CS (Chip Select):** GPIO 8 (CE0)
- **DC (Data/Command):** GPIO 24
- **RST (Reset):** GPIO 25
- **BL (Backlight):** Connect to 3.3V or 5V (depending on your module)

### 2. XPT2046 Touch Digitizer (SPI)
The touch controller shares the same SPI bus as the display, but uses a different Chip Select pin.
- **MOSI / MISO / SCLK:** Share with the Display
- **CS (Chip Select):** GPIO 7 (CE1)
- **IRQ (Pen Interrupt):** GPIO 17

### 3. Physical Shutter Button
- Wire a tactile button between **GPIO 21** and **GND**. The firmware uses an internal pull-up resistor, so it reads active-low when pressed.

### 4. Camera Module
- Connect a compatible camera module (e.g., Raspberry Pi Camera V2 or HQ Camera) via the CSI ribbon cable port. The libcamera backend will automatically detect the sensor type upon boot.
## Core Dependencies

To run the camera engine, display, and touch drivers, the following dependencies are required.

### 1. System Packages (APT)
On a Raspberry Pi, it is heavily recommended to install the hardware-linked Python packages via `apt` to avoid complex wheel compilation for the ARM architecture (especially for `numpy` and `picamera2`).
```bash
sudo apt-get update
sudo apt-get install -y python3-picamera2 python3-numpy python3-pil python3-flask python3-evdev python3-qrcode python3-requests python3-adafruit-blinka python3-adafruit-circuitpython-rgb-display libcap-dev libcamera-apps
```

### 2. Python Packages (PIP)
If you are setting up an isolated virtual environment, you can use `pip`:
```text
Pillow>=9.0.0
numpy>=1.21.0
Flask>=2.0.0
qrcode>=7.0
adafruit-circuitpython-rgb-display>=3.0.0
Adafruit-Blinka>=8.0.0
evdev>=1.6.0
```

---

## Execution Commands

### Running the Camera (Standard Mode)
Boots the camera engine, rendering the UI and camera feed directly to the ILI9341 SPI display.
```bash
# Using the Makefile wrapper:
make run

# Running directly from the Python layer:
cd firmware/python
python3 main.py
```

### Running the Camera (Benchmark Mode)
Boots the camera engine while drawing a live uptime timer to the screen. It also spawns a background daemon thread that queries the Raspberry Pi's `vcgencmd get_throttled` state every 60 seconds and logs the results to a local CSV file to test battery life.
```bash
# Using the Makefile wrapper:
make benchmark

# Running directly from the Python layer:
cd firmware/python
python3 main.py --benchmark
```

---

## Touch Screen Integration

The touch interface utilizes the resistive touchscreen digitizer (typically an XPT2046 or ADS7846) over SPI. 

### 1. Touch digitizer logic
Because the graphical UI (Pillow) and the hardware display (`ili9341`) handle rotations differently, the raw coordinates from the touch digitizer must be mapped to the actual screen geometry.

**Hardware Driver:** `evdev` is used to capture `ABS_X` and `ABS_Y` touch events in `calibrate_touch.py`.
**Firmware Parsing:** In `touch_interface.py`, the firmware directly speaks to the SPI hardware bus at `1MHz` to bypass OS-level touch noise and read stable ADC voltages.

### 2. Touch Calibration
Before the UI can accurately determine button presses, the raw touch digitizer bounds must be mapped. 
Run the following interactive calibration script and tap the four corners of the screen when prompted:
```bash
cd firmware/python
python3 calibrate_touch.py
```
This generates a `touch_settings.json` file containing the `x_min`, `x_max`, `y_min`, and `y_max` mappings used by the UI engine.

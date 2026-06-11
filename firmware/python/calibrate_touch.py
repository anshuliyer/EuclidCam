import time
import os
import json
import board
import digitalio

def get_stable_touch(spi, cs):
    """Polls SPI until a stable touch is detected and released."""
    print("Waiting for touch... ", end="", flush=True)
    
    # Wait for initial touch
    while True:
        while not spi.try_lock():
            pass
        try:
            spi.configure(baudrate=2000000)
            cs.value = False
            buf = bytearray(3)
            spi.write_readinto(bytearray([0xD0, 0x00, 0x00]), buf)
            x = (buf[1] << 5) | (buf[2] >> 3)
            spi.write_readinto(bytearray([0x90, 0x00, 0x00]), buf)
            y = (buf[1] << 5) | (buf[2] >> 3)
            cs.value = True
        finally:
            spi.unlock()
            
        if 100 < x < 4000 and 100 < y < 4000:
            break
        time.sleep(0.05)
        
    print("Detected! Hold still... ", end="", flush=True)
    
    # Collect samples
    xs, ys = [], []
    for _ in range(10):
        while not spi.try_lock():
            pass
        try:
            cs.value = False
            buf = bytearray(3)
            spi.write_readinto(bytearray([0xD0, 0x00, 0x00]), buf)
            xs.append((buf[1] << 5) | (buf[2] >> 3))
            spi.write_readinto(bytearray([0x90, 0x00, 0x00]), buf)
            ys.append((buf[1] << 5) | (buf[2] >> 3))
            cs.value = True
        finally:
            spi.unlock()
        time.sleep(0.02)
        
    xs.sort()
    ys.sort()
    final_x = xs[5]
    final_y = ys[5]
    
    print("Got it! Please lift your finger.")
    
    # Wait for release
    while True:
        while not spi.try_lock():
            pass
        try:
            cs.value = False
            buf = bytearray(3)
            spi.write_readinto(bytearray([0xD0, 0x00, 0x00]), buf)
            x = (buf[1] << 5) | (buf[2] >> 3)
            spi.write_readinto(bytearray([0x90, 0x00, 0x00]), buf)
            y = (buf[1] << 5) | (buf[2] >> 3)
            cs.value = True
        finally:
            spi.unlock()
            
        if not (100 < x < 4000 and 100 < y < 4000):
            break
        time.sleep(0.1)
        
    print(f"Recorded -> RAW X: {final_x}, RAW Y: {final_y}\n")
    return final_x, final_y

def main():
    print("--- INTERACTIVE SMART CALIBRATION ---")
    print("If your left edge is dead, just tap AS FAR LEFT as your screen still works.")
    print("We will calibrate the camera to only use the working area of your screen!\n")
    
    try:
        spi = board.SPI()
        cs = digitalio.DigitalInOut(board.D7) # CS1
        cs.direction = digitalio.Direction.OUTPUT
        cs.value = True
    except Exception as e:
        print(f"Hardware error: {e}")
        return
        
    print("\n[STEP 1/3] Tap the TOP-LEFT corner of the screen.")
    x1, y1 = get_stable_touch(spi, cs)
    
    time.sleep(1)
    print("[STEP 2/3] Tap the BOTTOM-RIGHT corner of the screen.")
    x2, y2 = get_stable_touch(spi, cs)
    
    time.sleep(1)
    print("[STEP 3/3] Tap the TOP-RIGHT corner of the screen.")
    x3, y3 = get_stable_touch(spi, cs)
    
    print("Calculating perfect calibration matrix...")
    
    # Determine axes by seeing which one changed the most between Top-Left and Top-Right
    x_change = abs(x3 - x1)
    y_change = abs(y3 - y1)
    
    swap_xy = y_change > x_change
    
    if not swap_xy:
        # X is horizontal, Y is vertical
        x_min = min(x1, x2, x3) - 50 # Add a tiny 50px buffer so edges are easy to hit
        x_max = max(x1, x2, x3) + 50
        y_min = min(y1, y2, y3) - 50
        y_max = max(y1, y2, y3) + 50
        
        # Left is P1, Right is P3
        invert_x = x1 > x3
        # Top is P1, Bottom is P2
        invert_y = y1 > y2
    else:
        # Y is horizontal, X is vertical
        x_min = min(y1, y2, y3) - 50
        x_max = max(y1, y2, y3) + 50
        y_min = min(x1, x2, x3) - 50
        y_max = max(x1, x2, x3) + 50
        
        # Left is P1, Right is P3 (but using raw Y)
        invert_x = y1 > y3
        # Top is P1, Bottom is P2 (but using raw X)
        invert_y = x1 > x2
        
    # Clamp bounds to 0-4095
    x_min, x_max = max(0, x_min), min(4095, x_max)
    y_min, y_max = max(0, y_min), min(4095, y_max)
    
    config = {
        "x_min": x_min,
        "x_max": x_max,
        "y_min": y_min,
        "y_max": y_max,
        "swap_xy": swap_xy,
        "invert_x": invert_x,
        "invert_y": invert_y
    }
    
    print("\n--- RESULTS ---")
    print(json.dumps(config, indent=2))
    
    path = os.path.join(os.path.dirname(__file__), "UI/touch_settings.json")
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
        
    print(f"\nCalibration saved to {path}!")
    print("You can now run 'python3 main.py'.")

if __name__ == "__main__":
    main()

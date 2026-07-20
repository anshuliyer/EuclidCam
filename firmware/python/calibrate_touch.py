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
        
    print("\n[STEP 1/4] Tap the TOP-LEFT corner of the screen.")
    tl_x, tl_y = get_stable_touch(spi, cs)
    
    time.sleep(1)
    print("[STEP 2/4] Tap the TOP-RIGHT corner of the screen.")
    tr_x, tr_y = get_stable_touch(spi, cs)
    
    time.sleep(1)
    print("[STEP 3/4] Tap the BOTTOM-LEFT corner of the screen.")
    bl_x, bl_y = get_stable_touch(spi, cs)
    
    time.sleep(1)
    print("[STEP 4/4] Tap the BOTTOM-RIGHT corner of the screen.")
    br_x, br_y = get_stable_touch(spi, cs)
    
    print("Calculating perfect calibration matrix using 4-point averaging...")
    
    # Determine axes by seeing which one changes most when moving horizontally
    dx_horiz = abs(tr_x - tl_x) + abs(br_x - bl_x)
    dy_horiz = abs(tr_y - tl_y) + abs(br_y - bl_y)
    
    swap_xy = dy_horiz > dx_horiz
    
    if swap_xy:
        # Horizontal (Screen X) is mapped to Raw Y
        left_val = (tl_y + bl_y) / 2
        right_val = (tr_y + br_y) / 2
        x_min = min(left_val, right_val)
        x_max = max(left_val, right_val)
        invert_x = left_val > right_val
        
        # Vertical (Screen Y) is mapped to Raw X
        top_val = (tl_x + tr_x) / 2
        bottom_val = (bl_x + br_x) / 2
        y_min = min(top_val, bottom_val)
        y_max = max(top_val, bottom_val)
        invert_y = top_val > bottom_val
    else:
        # Horizontal (Screen X) is mapped to Raw X
        left_val = (tl_x + bl_x) / 2
        right_val = (tr_x + br_x) / 2
        x_min = min(left_val, right_val)
        x_max = max(left_val, right_val)
        invert_x = left_val > right_val
        
        # Vertical (Screen Y) is mapped to Raw Y
        top_val = (tl_y + tr_y) / 2
        bottom_val = (bl_y + br_y) / 2
        y_min = min(top_val, bottom_val)
        y_max = max(top_val, bottom_val)
        invert_y = top_val > bottom_val
        
    # Clamp bounds to 0-4095 and cast to int
    x_min, x_max = int(max(0, x_min)), int(min(4095, x_max))
    y_min, y_max = int(max(0, y_min)), int(min(4095, y_max))
    
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

import time
import os
import json
import board
import digitalio

def read_touch(spi, cs):
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
        return x, y
    finally:
        spi.unlock()

def wait_for_touch(spi, cs):
    print("\nWaiting for a touch... (Press anywhere on the screen)")
    while True:
        x, y = read_touch(spi, cs)
        if 100 < x < 4000 and 100 < y < 4000:
            break
        time.sleep(0.05)
        
    print("Touch detected! Hold still...")
    
    # Take a few samples
    xs, ys = [], []
    for _ in range(10):
        x, y = read_touch(spi, cs)
        xs.append(x)
        ys.append(y)
        time.sleep(0.02)
        
    xs.sort()
    ys.sort()
    final_x = xs[5]
    final_y = ys[5]
    
    print("Got it! Lift your finger.")
    while True:
        x, y = read_touch(spi, cs)
        if not (100 < x < 4000 and 100 < y < 4000):
            break
        time.sleep(0.05)
        
    print(f"-> RAW X: {final_x}, RAW Y: {final_y}")
    return final_x, final_y

def main():
    print("--- MANUAL TOUCH CALIBRATOR ---")
    
    try:
        spi = board.SPI()
        cs = digitalio.DigitalInOut(board.D7) # CS1
        cs.direction = digitalio.Direction.OUTPUT
        cs.value = True
    except Exception as e:
        print(f"Hardware error: {e}")
        return

    pts = {}
    
    while True:
        x, y = wait_for_touch(spi, cs)
        ans = input("What corner/edge did you just touch? (Type TL, TR, BL, BR, or 'done' to finish): ").strip().upper()
        
        if ans == 'DONE':
            if len(pts) < 3:
                print("Please provide at least 3 points (e.g. TL, TR, BR) so we can figure out the axes!")
                continue
            break
        elif ans in ['TL', 'TR', 'BL', 'BR']:
            pts[ans] = (x, y)
            print(f"Saved {ans} as ({x}, {y})")
        else:
            print("Invalid input. Ignoring touch.")

    print("\nCalculating calibration...")
    
    all_x = [p[0] for p in pts.values()]
    all_y = [p[1] for p in pts.values()]
    
    swap_xy = False
    invert_x = False
    invert_y = False
    
    # Determine SWAP_XY
    if 'TL' in pts and 'TR' in pts:
        swap_xy = abs(pts['TL'][1] - pts['TR'][1]) > abs(pts['TL'][0] - pts['TR'][0])
    elif 'BL' in pts and 'BR' in pts:
        swap_xy = abs(pts['BL'][1] - pts['BR'][1]) > abs(pts['BL'][0] - pts['BR'][0])
    elif 'TL' in pts and 'BL' in pts:
        swap_xy = abs(pts['TL'][0] - pts['BL'][0]) > abs(pts['TL'][1] - pts['BL'][1])

    # Determine INVERT based on horizontal/vertical axes
    if not swap_xy:
        if 'TL' in pts and 'TR' in pts: invert_x = pts['TL'][0] > pts['TR'][0]
        elif 'BL' in pts and 'BR' in pts: invert_x = pts['BL'][0] > pts['BR'][0]
            
        if 'TL' in pts and 'BL' in pts: invert_y = pts['TL'][1] > pts['BL'][1]
        elif 'TR' in pts and 'BR' in pts: invert_y = pts['TR'][1] > pts['BR'][1]
    else:
        if 'TL' in pts and 'TR' in pts: invert_x = pts['TL'][1] > pts['TR'][1]
        elif 'BL' in pts and 'BR' in pts: invert_x = pts['BL'][1] > pts['BR'][1]
            
        if 'TL' in pts and 'BL' in pts: invert_y = pts['TL'][0] > pts['BL'][0]
        elif 'TR' in pts and 'BR' in pts: invert_y = pts['TR'][0] > pts['BR'][0]

    x_min = max(0, min(all_x) - 50)
    x_max = min(4095, max(all_x) + 50)
    y_min = max(0, min(all_y) - 50)
    y_max = min(4095, max(all_y) + 50)
    
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

if __name__ == "__main__":
    main()

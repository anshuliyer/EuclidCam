import time
import os
import json
import board
import digitalio

def load_config():
    path = os.path.join(os.path.dirname(__file__), "UI/touch_settings.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None

def map_to_screen(raw_x, raw_y, config):
    if not config: return None, None
    c = config
    if c.get("swap_xy"): raw_x, raw_y = raw_y, raw_x
    
    x_range = (c["x_max"] - c["x_min"]) or 1
    y_range = (c["y_max"] - c["y_min"]) or 1
    
    x_norm = (raw_x - c["x_min"]) / x_range
    y_norm = (raw_y - c["y_min"]) / y_range
    
    if c.get("invert_x"): x_norm = 1.0 - x_norm
    if c.get("invert_y"): y_norm = 1.0 - y_norm
    
    x = x_norm * 320
    y = y_norm * 240
    return int(x), int(y)

def main():
    print("Initializing pure-Python Touch Calibration...")
    config = load_config()
    if config:
        print(f"Loaded existing mapping: {config}")
    else:
        print("No UI/touch_settings.json found. Showing RAW values only.")
    
    try:
        spi = board.SPI()
        cs = digitalio.DigitalInOut(board.D7) # CS1
        cs.direction = digitalio.Direction.OUTPUT
        cs.value = True
        
        irq = digitalio.DigitalInOut(board.D17) # penirq
        irq.direction = digitalio.Direction.INPUT
        irq.pull = digitalio.Pull.UP
    except Exception as e:
        print(f"Failed to initialize hardware: {e}")
        return

    print("Hardware initialized successfully!")
    print("\n--- TOUCH CALIBRATION ---")
    print("Please touch the corners of your screen (Top-Left, Top-Right, etc).")
    print("Press Ctrl+C to exit.\n")

    try:
        touch_active = False
        last_x, last_y = 0, 0
        
        while True:
            is_touched = not irq.value # Active Low
            
            if is_touched:
                while not spi.try_lock():
                    pass
                try:
                    spi.configure(baudrate=2000000)
                    
                    xs, ys = [], []
                    buf = bytearray(3)
                    for _ in range(5):
                        cs.value = False
                        
                        # Read X (0xD0)
                        spi.write_readinto(bytearray([0xD0, 0x00, 0x00]), buf)
                        x = (buf[1] << 5) | (buf[2] >> 3)
                        
                        # Read Y (0x90)
                        spi.write_readinto(bytearray([0x90, 0x00, 0x00]), buf)
                        y = (buf[1] << 5) | (buf[2] >> 3)
                        
                        cs.value = True
                        xs.append(x)
                        ys.append(y)
                        
                    xs.sort()
                    ys.sort()
                    x_med, y_med = xs[2], ys[2]
                    
                    last_x, last_y = x_med, y_med
                    touch_active = True
                finally:
                    spi.unlock()
            else:
                if touch_active:
                    pixel_x, pixel_y = map_to_screen(last_x, last_y, config)
                    if pixel_x is not None:
                        print(f"Touch released! -> RAW(x:{last_x:4d}, y:{last_y:4d}) | MAPPED PIXEL(x:{pixel_x:3d}, y:{pixel_y:3d})")
                        
                        # Simple guide to help tell what corner they hit
                        corner_x = "Left" if pixel_x < 160 else "Right"
                        corner_y = "Top" if pixel_y < 120 else "Bottom"
                        print(f"  -> Looks like you touched the {corner_y}-{corner_x} corner!")
                    else:
                        print(f"Touch released at RAW X: {last_x}, RAW Y: {last_y}")
                        
                    touch_active = False
                    
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nCalibration finished.")

if __name__ == "__main__":
    main()

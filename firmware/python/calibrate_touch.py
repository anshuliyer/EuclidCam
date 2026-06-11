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

def main():
    print("Initializing POLLING Touch Calibration (Ignoring IRQ Pin)...")
    config = load_config()
    
    try:
        spi = board.SPI()
        cs = digitalio.DigitalInOut(board.D7) # CS1
        cs.direction = digitalio.Direction.OUTPUT
        cs.value = True
    except Exception as e:
        print(f"Failed to initialize hardware: {e}")
        return

    print("Hardware initialized successfully!")
    print("\n--- TOUCH CALIBRATION (POLLING MODE) ---")
    print("Please touch the left side of your screen.")
    print("Press Ctrl+C to exit.\n")

    try:
        while True:
            while not spi.try_lock():
                pass
            try:
                spi.configure(baudrate=2000000)
                
                cs.value = False
                buf = bytearray(3)
                # Read X (0xD0)
                spi.write_readinto(bytearray([0xD0, 0x00, 0x00]), buf)
                x = (buf[1] << 5) | (buf[2] >> 3)
                
                # Read Y (0x90)
                spi.write_readinto(bytearray([0x90, 0x00, 0x00]), buf)
                y = (buf[1] << 5) | (buf[2] >> 3)
                cs.value = True
                
                # 4095 or 0 usually means not touched
                if 100 < x < 4000 and 100 < y < 4000:
                    print(f"Touch Detected! RAW X: {x}, RAW Y: {y}")
            finally:
                spi.unlock()
                
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nCalibration finished.")

if __name__ == "__main__":
    main()

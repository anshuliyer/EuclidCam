import time
try:
    import evdev
    from evdev import ecodes
except ImportError:
    print("Please install evdev first: sudo apt install python3-evdev")
    exit(1)

def find_touch_device():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for dev in devices:
        if "touchscreen" in dev.name.lower() or "ads7846" in dev.name.lower():
            return dev
    return None

def main():
    dev = find_touch_device()
    if not dev:
        print("No touchscreen found in /dev/input/! Please make sure the driver is loaded.")
        return

    print(f"Found touch device: {dev.name} at {dev.path}")
    print("\n--- TOUCH CALIBRATION ---")
    print("Please touch the corners of your screen and note the raw X and Y values.")
    print("Press Ctrl+C to exit.\n")

    try:
        last_x = 0
        last_y = 0
        for event in dev.read_loop():
            if event.type == ecodes.EV_ABS:
                if event.code == ecodes.ABS_X:
                    last_x = event.value
                elif event.code == ecodes.ABS_Y:
                    last_y = event.value
            elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
                if event.value == 0:  # Touch release
                    print(f"Touch released at RAW X: {last_x}, RAW Y: {last_y}")
    except KeyboardInterrupt:
        print("\nCalibration finished.")

if __name__ == "__main__":
    main()

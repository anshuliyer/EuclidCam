import main

# UI Configuration
CONFIG = {
    "flash": True,      # Flash switchable (ON right now)
    "battery": None,    # Placeholder
    "wifi": None,       # Placeholder
    "photo_dir": "../../Captured"
}

def start_camera():
    """
    Entry point to start the EuclidCam camera logic.
    """
    print("[SYSTEM] Starting EuclidCam Camera...")
    main.run(CONFIG)

if __name__ == "__main__":
    start_camera()

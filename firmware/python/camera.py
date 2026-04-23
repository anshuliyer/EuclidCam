import main

# UI Configuration
CONFIG = {
    "flash": True,      # Flash switchable (ON right now)
    "battery": None,    # Placeholder
    "wifi": None,       # Placeholder
    "photo_dir": "../../Captured",
    "ui_rotation": 0,    # Rotation in degrees (0, 90, 180, 270)
    "ui_padding": 20     # Padding from edges
}

def start_camera():
    """
    Entry point to start the EuclidCam camera logic.
    """
    print("[SYSTEM] Starting EuclidCam Camera...")
    main.run(CONFIG)

if __name__ == "__main__":
    start_camera()

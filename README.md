# EuclidCam

Custom embedded camera firmware for a Raspberry Pi point-and-shoot. Runs headlessly on a 480×320 SPI display with a capacitive touch panel.

```
euclidcam/
├── firmware/python/       # On-device runtime
│   ├── main.py            # System entry point, event loop, all subsystems
│   ├── filters/           # PIL colour-grading modules
│   ├── UI/                # Framebuffer renderer, touch controller, themes
│   ├── settings/          # Composition grid
│   ├── connectivity/      # Flask server + WiFi helpers
│   └── IO/                # GPIO / evdev stubs
├── assets/                # Unified visual assets, fonts, and boot animations
├── Webapp/                # Remote gallery UI and mockups
├── Captured/              # Photo output (on-device)
├── requirements.txt       # Python dependencies
└── LICENSE                # MIT License
```

## Setup

This software is production-ready and shippable. Hardware dependencies (`picamera2`) are assumed to be available via the Raspberry Pi OS `apt` repositories. Python dependencies are strictly pinned.

```bash
make install          # installs apt dependencies and pip requirements.txt
make run              # foreground launch
make service-install  # register systemd unit
```

## Dev

```bash
make check   # syntax-check all .py files
make lint    # flake8
make clean   # remove __pycache__, temp.jpg
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

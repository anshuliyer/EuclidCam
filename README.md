# EuclidCam

Custom embedded camera firmware for a Raspberry Pi point-and-shoot. Runs headlessly on a 480×320 SPI display with a capacitive touch panel.

```
euclidcam/
├── firmware/python/       # On-device firmware runtime engine
│   ├── main.py            # Main entry point and orchestration loop
│   ├── filters/           # Custom PIL photo filters (Glam, 35mm, Summer, etc.)
│   ├── UI/                # Display renderer, touch digitizer driver, and themes
│   ├── settings/          # Viewfinder composition grids (3x3, Golden Ratio)
│   ├── connectivity/      # Flask remote control server & Wi-Fi configuration
│   └── IO/                # Hardware GPIO flash & battery management
├── docs/                  # Technical documentation & hardware reference manual
├── scripts/               # Bootstrapping & asset utility scripts
├── assets/                # Core visual media, logos, and typography fonts
├── tests/                 # Firmware test suite
├── Captured/              # Photo output (on-device)
├── Makefile               # Installation, deployment, and service targets
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
This project is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)** — see the [LICENSE](LICENSE) file for details.

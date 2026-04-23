import time
import sys
import select
import numpy as np
import mmap
from picamera2 import Picamera2
from PIL import Image, ImageDraw

# Config
FB_DEVICE = "/dev/fb1" 
SCREEN_RES = (480, 320)
FPS_CAP = 3  # Keeps SPI bus stable
MAUVE = (224, 176, 255)

picam2 = Picamera2()
 
def overlay_ui(frame, config):
    """
    Overlays UI indicators on the camera frame.
    """
    if config is None:
        return frame
        
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    
    # Top Panel Indicators
    x_offset = SCREEN_RES[0] - 30
    y_offset = 20
    
    # Flash Icon (Thunderbolt)
    if config.get("flash"):
        # Draw a simple bolt shape
        points = [
            (x_offset, y_offset), (x_offset - 10, y_offset + 10),
            (x_offset - 5, y_offset + 10), (x_offset - 15, y_offset + 25),
            (x_offset - 5, y_offset + 15), (x_offset - 10, y_offset + 15),
            (x_offset, y_offset)
        ]
        draw.polygon(points, fill=MAUVE)
    
    # Battery Placeholder
    x_offset -= 30
    draw.rectangle([x_offset, y_offset, x_offset + 20, y_offset + 10], outline=MAUVE, width=2)
    draw.rectangle([x_offset + 20, y_offset + 3, x_offset + 22, y_offset + 7], fill=MAUVE)
    
    # WiFi Placeholder
    x_offset -= 30
    for i in range(1, 4):
        draw.arc([x_offset - i*5, y_offset - i*5, x_offset + 20 + i*5, y_offset + 20 + i*5], 225, 315, fill=MAUVE, width=2)

    return np.array(img)


def start_preview():
    config = picam2.create_video_configuration(main={"size": SCREEN_RES, "format": "RGB888"})
    picam2.configure(config)
    picam2.start()

def display_to_map(data_array, fb_map):
    # Convert RGB888 to RGB565 (Little Endian for tft35a)
    r = data_array[:, :, 0].astype(np.uint16)
    g = data_array[:, :, 1].astype(np.uint16)
    b = data_array[:, :, 2].astype(np.uint16)
    
    # Swap R and B if colors look blue/red inverted
    rgb565 = ((b >> 3) << 11) | ((g >> 2) << 5) | (r >> 3)
    
    fb_map.seek(0)
    fb_map.write(rgb565.tobytes())

def take_photo(fb_map):
    print("\n[SHUTTER] Capturing...")
    picam2.stop()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start()
    
    time.sleep(1)
    filename = f"capture_{int(time.time())}.jpg"
    picam2.capture_file(filename)
    
    # Review
    img = Image.open(filename).convert("RGB").resize(SCREEN_RES)
    display_to_map(np.array(img), fb_map)
    time.sleep(2.0)
    
    picam2.stop()
    start_preview()

def run(config=None):
    # Main Loop
    start_preview()
    try:
        with open(FB_DEVICE, "r+b") as f:
            map_size = SCREEN_RES[0] * SCREEN_RES[1] * 2
            with mmap.mmap(f.fileno(), map_size) as fb_map:
                while True:
                    loop_start = time.time()
                    frame = picam2.capture_array()
                    if frame is not None:
                        frame = overlay_ui(frame, config)
                        display_to_map(frame, fb_map)
                    
                    if select.select([sys.stdin], [], [], 0)[0]:
                        sys.stdin.readline()
                        take_photo(fb_map)
                    
                    time.sleep(max(0, (1.0 / FPS_CAP) - (time.time() - loop_start)))
    except KeyboardInterrupt:
        picam2.stop()

if __name__ == "__main__":
    run()

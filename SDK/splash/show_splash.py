import sys
import os
import board
import digitalio
from PIL import Image
import adafruit_rgb_display.ili9341 as ili9341

def main():
    # Allow user to pass an image, or default to the blueprint logo in the repo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_img = os.path.abspath(os.path.join(script_dir, "..", "..", "assets", "IMG_4712-Photoroom.png"))
    img_path = sys.argv[1] if len(sys.argv) > 1 else default_img

    print("Initializing SPI and GPIO...")
    spi = board.SPI()
    cs_pin = digitalio.DigitalInOut(board.D8)
    dc_pin = digitalio.DigitalInOut(board.D24)
    rst_pin = digitalio.DigitalInOut(board.D25)

    print("Waking up ILI9341 Display...")
    disp = ili9341.ILI9341(
        spi, 
        cs=cs_pin, 
        dc=dc_pin, 
        rst=rst_pin, 
        rotation=90, 
        baudrate=24000000
    )

    print(f"Loading image: {img_path}...")
    try:
        image = Image.open(img_path).convert('RGB')
    except Exception as e:
        print(f"Error loading image! Make sure the path is correct. Details: {e}")
        sys.exit(1)

    # Resize to fit the exact hardware bounds
    print("Resizing image to 320x240...")
    image = image.resize((320, 240))
    
    print("Flashing image to screen...")
    disp.image(image)
    
    print("Success! Image is on the screen.")

if __name__ == "__main__":
    main()

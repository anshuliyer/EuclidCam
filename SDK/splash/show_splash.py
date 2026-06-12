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

    # Fix aspect ratio and apply very low opacity
    print("Applying low opacity and fixing aspect ratio...")
    
    # 1. Lower opacity by blending with a solid black background
    black_bg = Image.new('RGB', image.size, (0, 0, 0))
    image = Image.blend(black_bg, image, alpha=0.15) # 15% opacity
    
    # 2. Maintain aspect ratio while scaling to fit within 320x240
    image.thumbnail((320, 240), Image.Resampling.LANCZOS)
    
    # 3. Create a clean 320x240 black canvas and center the image on it
    canvas = Image.new('RGB', (320, 240), (0, 0, 0))
    paste_x = (320 - image.width) // 2
    paste_y = (240 - image.height) // 2
    canvas.paste(image, (paste_x, paste_y))
    
    print("Flashing image to screen...")
    disp.image(canvas)
    
    print("Success! Image is on the screen.")

if __name__ == "__main__":
    main()

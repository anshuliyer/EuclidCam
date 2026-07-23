import sys
import os
import time
import argparse
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341

def get_tail_lines(filepath, n=15):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            return [l.strip()[:45] for l in lines[-n:]]
    except Exception:
        return []

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_img = os.path.abspath(os.path.join(script_dir, "../assets/camera_blueprint.png"))
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--img", default=default_img)
    parser.add_argument("--log", default=None)
    args = parser.parse_args()

    img_path = args.img

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
    base_canvas = Image.new('RGB', (320, 240), (0, 0, 0))
    paste_x = (320 - image.width) // 2
    paste_y = (240 - image.height) // 2
    base_canvas.paste(image, (paste_x, paste_y))
    
    print("Flashing base image to screen...")
    disp.image(base_canvas)
    
    if args.log:
        print(f"Tailing logs from {args.log}...")
        font = ImageFont.load_default()
        last_lines = []
        
        while not os.path.exists("install.done"):
            lines = get_tail_lines(args.log, 15)
            if lines != last_lines:
                frame = base_canvas.copy()
                draw = ImageDraw.Draw(frame)
                
                y = 10
                for line in lines:
                    # Beige color
                    draw.text((10, y), line, font=font, fill=(245, 245, 220))
                    y += 14
                    
                disp.image(frame)
                last_lines = lines
                
            time.sleep(0.2)
            
        # Final update to show completion
        frame = base_canvas.copy()
        draw = ImageDraw.Draw(frame)
        draw.text((10, 10), "INSTALLATION COMPLETE!", font=font, fill=(0, 255, 0))
        disp.image(frame)
        
    print("Success! Operation finished.")

if __name__ == "__main__":
    main()

import os
from PIL import Image

def generate_iphone_boot(filename, width=320, height=240):
    bg_color = (17, 17, 17)
    
    # Load Logo
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../connectivity/static/euclid_construction.gif"))
    logo_gif = Image.open(logo_path)
    # Get last frame to use as the static logo
    logo_gif.seek(logo_gif.n_frames - 1)
    rgba = logo_gif.convert("RGBA")
    
    scale = min(width / rgba.width, height / rgba.height) * 0.7
    nw, nh = int(rgba.width * scale), int(rgba.height * scale)
    logo_resized = rgba.resize((nw, nh), Image.LANCZOS)
    
    base_logo = Image.new("RGB", (width, height), bg_color)
    base_logo.paste(logo_resized, ((width - nw)//2, (height - nh)//2))
    
    frames = []
    
    fade_in_frames = 20
    hold_frames = 50
    fade_out_frames = 15
    
    # Phase 1: Smooth Fade In
    for f in range(fade_in_frames):
        # Cubic ease-in-out for premium fade
        t = f / float(fade_in_frames)
        opacity = t * t * (3.0 - 2.0 * t)
        img = Image.new("RGB", (width, height), bg_color)
        img = Image.blend(img, base_logo, opacity)
        frames.append(img)
        
    # Phase 2: Hold (Static, pure minimalism)
    for f in range(hold_frames):
        frames.append(base_logo)
        
    # Phase 3: Smooth Fade Out
    for f in range(fade_out_frames):
        t = 1.0 - (f / float(fade_out_frames))
        opacity = t * t * (3.0 - 2.0 * t)
        img = Image.new("RGB", (width, height), bg_color)
        img = Image.blend(img, base_logo, opacity)
        frames.append(img)
        
    # Black screen transition buffer
    for f in range(5):
        frames.append(Image.new("RGB", (width, height), bg_color))
        
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=40, loop=0)
    print(f"Generated {filename}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "iphone_boot.gif")
    generate_iphone_boot(out_path)

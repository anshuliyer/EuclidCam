import math
import os
from PIL import Image, ImageDraw, ImageChops

def generate_explosion_gif(filename, width=320, height=240):
    golden_angle = math.pi * (3 - math.sqrt(5))
    num_particles = 300
    
    bg_color = (17, 17, 17)
    dot_color = (250, 214, 165)
    
    # Load the logo GIF
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../connectivity/static/euclid_construction.gif"))
    logo_gif = Image.open(logo_path)
    logo_frames = []
    
    for i in range(logo_gif.n_frames):
        logo_gif.seek(i)
        rgba = logo_gif.convert("RGBA")
        # Scale to fit 320x240
        lw, lh = rgba.size
        scale = min(width / lw, height / lh)
        nw, nh = int(lw * scale), int(lh * scale)
        resized = rgba.resize((nw, nh), Image.LANCZOS)
        
        # Center on a black background
        frame_bg = Image.new("RGB", (width, height), bg_color)
        frame_bg.paste(resized, ((width - nw)//2, (height - nh)//2), resized if 'A' in resized.getbands() else None)
        logo_frames.append(frame_bg)
        
    logo_frame_count = len(logo_frames)
    explosion_frames = 25
    total_frames = logo_frame_count + explosion_frames
    
    particles = []
    c = 10
    for i in range(1, num_particles + 1):
        r = c * math.sqrt(i)
        theta = i * golden_angle
        size = max(0.8, 2.5 - (r / 60))
        particles.append({"r": r, "theta": theta, "size": size})
        
    frames = []
    
    for f in range(total_frames):
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        if f < logo_frame_count:
            # Phase 1: Logo is animating, dots rotate slowly
            expansion = 1.0
            rotation = f * 0.02
            dot_opacity = 0.35  # High transparency for background dots
            logo_opacity = 1.0
            current_logo = logo_frames[f]
        else:
            # Phase 2: Explosion
            progress = (f - logo_frame_count) / float(explosion_frames)
            expansion = 1.0 + (progress ** 3) * 25
            rotation = logo_frame_count * 0.02 + progress * 0.2
            dot_opacity = max(0, 0.35 - progress * 1.5)
            logo_opacity = max(0, 1.0 - progress * 1.5)
            current_logo = logo_frames[-1]
            
        # Draw Dots
        for p in particles:
            r = p["r"] * expansion
            theta = p["theta"] + rotation
            x = width / 2 + r * math.cos(theta)
            y = height / 2 + r * math.sin(theta)
            s = p["size"]
            
            if -10 < x < width + 10 and -10 < y < height + 10:
                c_val = tuple(int(bg_color[i] + (dot_color[i] - bg_color[i]) * dot_opacity) for i in range(3))
                draw.ellipse([x-s, y-s, x+s, y+s], fill=c_val)
                
        # Composite Logo on top
        if logo_opacity > 0:
            if logo_opacity < 1.0:
                # Fade out logo
                logo_faded = current_logo.copy()
                logo_pixels = logo_faded.load()
                for y in range(height):
                    for x in range(width):
                        cp = logo_pixels[x, y]
                        logo_pixels[x, y] = tuple(int(bg_color[i] + (cp[i] - bg_color[i]) * logo_opacity) for i in range(3))
                img = ImageChops.lighter(img, logo_faded)
            else:
                img = ImageChops.lighter(img, current_logo)
                
        frames.append(img)
        
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=40, loop=0)
    print(f"Generated {filename}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "explosion_splash.gif")
    generate_explosion_gif(out_path)

import math
import os
from PIL import Image, ImageDraw, ImageChops, ImageFont

def generate_explosion_gif(filename, width=320, height=240):
    # Core Mathematical Constants
    phi = (1 + math.sqrt(5)) / 2.0  # Golden Ratio: ~1.6180339
    golden_angle = math.pi * (3 - math.sqrt(5))
    
    # Fibonacci numbers for organic structuring
    num_particles = 377  # 14th Fibonacci number
    
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
        # Scale slightly smaller (0.7) for the minimal iPhone aesthetic they liked
        scale = min(width / lw, height / lh) * 0.7
        nw, nh = int(lw * scale), int(lh * scale)
        resized = rgba.resize((nw, nh), Image.LANCZOS)
        
        # Center on a black background
        frame_bg = Image.new("RGB", (width, height), bg_color)
        frame_bg.paste(resized, ((width - nw)//2, (height - nh)//2), resized if 'A' in resized.getbands() else None)
        logo_frames.append(frame_bg)
        
    logo_frame_count = len(logo_frames)
    hold_frames = 89  # Fibonacci (approx 3.5 seconds)
    explosion_frames = 34  # Fibonacci
    total_frames = logo_frame_count + hold_frames + explosion_frames
    
    # Load Font
    try:
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../connectivity/static/fonts/JetBrainsMono-Bold.ttf"))
        font = ImageFont.truetype(font_path, 18)
    except:
        font = ImageFont.load_default()
    
    particles = []
    # Spacing factor correlated perfectly to the golden ratio
    c = 10 * (phi - 0.5) 
    
    for i in range(1, num_particles + 1):
        r = c * math.sqrt(i)
        theta = i * golden_angle
        # Size falls off based on golden ratio division
        size = max(0.5, 2.5 - (r / (60 * phi)))
        particles.append({"r": r, "theta": theta, "size": size})
        
    frames = []
    
    for f in range(total_frames):
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        if f < logo_frame_count:
            # Phase 1: Logo is animating, dots rotate slowly based on phi
            rotation = f * (0.01 * phi)
            dot_opacity = 0.15 # Extremely high transparency (faint watermark)
            logo_opacity = 1.0
            text_opacity = 0.0
            current_logo = logo_frames[f]
            exp_progress = 0.0
        elif f < logo_frame_count + hold_frames:
            # Phase 2: Hold, text fades in purely
            rotation = f * (0.01 * phi)
            dot_opacity = 0.15
            logo_opacity = 1.0
            
            hold_progress = (f - logo_frame_count) / float(hold_frames)
            # Simple fade in
            text_opacity = min(1.0, hold_progress * 4.0)
            
            current_logo = logo_frames[-1]
            exp_progress = 0.0
        else:
            # Phase 3: Explosion
            exp_f = f - (logo_frame_count + hold_frames)
            exp_progress = exp_f / float(explosion_frames)
            # Smooth fade out governed by phi
            fade_out = max(0, 1.0 - exp_progress * phi)
            dot_opacity = 0.15 * fade_out
            logo_opacity = fade_out
            text_opacity = fade_out
            current_logo = logo_frames[-1]
            
        # Draw Dots
        for i, p in enumerate(particles):
            if exp_progress == 0.0:
                r = p["r"]
                theta = p["theta"] + rotation
            else:
                # Travel exactly along the Golden Spiral (cleanly, no depth variance)
                # Expansion acceleration scaled by the golden ratio
                index_boost = (exp_progress ** 3) * (377 * phi)
                
                n_new = (i + 1) + index_boost
                r = c * math.sqrt(n_new)
                
                base_rotation = (logo_frame_count + hold_frames) * (0.01 * phi)
                theta = n_new * golden_angle + base_rotation
                
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
                
        # Draw Text (Draw AFTER logo to guarantee visibility)
        if text_opacity > 0:
            text1 = "EuclidCam"
            
            # Aligned with the base of the curve
            # The curve's bounding box is roughly the resized logo dimensions (nw, nh) centered
            # x = center_x - nw//2 + 16
            # y = center_y + nh//2 - 25 (relative to curve base)
            tx1 = (width - nw) // 2 + 16
            ty1 = (height + nh) // 2 - 25 - 18 # 18 is font size approx
            
            # Use ImageDraw on the newly composited image
            final_draw = ImageDraw.Draw(img)
            c_val = tuple(int(bg_color[i] + (dot_color[i] - bg_color[i]) * text_opacity) for i in range(3))
            final_draw.text((tx1, ty1), text1, font=font, fill=c_val)
                
        frames.append(img)
        
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=40, loop=0)
    print(f"Generated {filename}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "explosion_splash.gif")
    generate_explosion_gif(out_path)

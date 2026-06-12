import math
import os
from PIL import Image, ImageDraw

def generate_explosion_gif(filename, width=320, height=240, frames_count=45):
    golden_angle = math.pi * (3 - math.sqrt(5))
    num_particles = 300
    
    bg_color = (17, 17, 17)
    dot_color = (250, 214, 165) # Warm golden beige
    
    frames = []
    
    particles = []
    c = 10 # Spacing factor for small screen
    
    for i in range(1, num_particles + 1):
        r = c * math.sqrt(i)
        theta = i * golden_angle
        # Points closer to center are slightly larger
        size = max(0.8, 2.5 - (r / 60))
        particles.append({"r": r, "theta": theta, "size": size})
        
    for f in range(frames_count):
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Frame 0 to 20: Slow rotation
        # Frame 20 to 45: Exponential explosion
        if f < 20:
            expansion = 1.0
            rotation = f * 0.05
            opacity_factor = 1.0
        else:
            progress = (f - 20) / (frames_count - 20)
            # Cubic explosion curve
            expansion = 1.0 + (progress ** 3) * 25
            rotation = 20 * 0.05 + progress * 0.2
            # Fade out particles as they explode to reveal camera
            opacity_factor = max(0, 1.0 - progress)
            
        for p in particles:
            r = p["r"] * expansion
            theta = p["theta"] + rotation
            
            x = width / 2 + r * math.cos(theta)
            y = height / 2 + r * math.sin(theta)
            
            s = p["size"]
            
            # Simple boundary check to avoid drawing offscreen waste
            if -10 < x < width + 10 and -10 < y < height + 10:
                # Calculate color with fade out
                c_val = tuple(int(bg_color[i] + (dot_color[i] - bg_color[i]) * opacity_factor) for i in range(3))
                draw.ellipse([x-s, y-s, x+s, y+s], fill=c_val)
                
        frames.append(img)
        
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=40, loop=0)
    print(f"Generated {filename}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "explosion_splash.gif")
    generate_explosion_gif(out_path)

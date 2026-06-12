import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops

def generate_creative_boot(filename, width=320, height=240):
    bg_color = (17, 17, 17)
    fg_color = (250, 214, 165)
    faint_color = tuple(int(bg_color[i] + (fg_color[i] - bg_color[i]) * 0.2) for i in range(3))
    
    # Load Logo
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../connectivity/static/euclid_construction.gif"))
    logo_gif = Image.open(logo_path)
    logo_frames = []
    for i in range(logo_gif.n_frames):
        logo_gif.seek(i)
        rgba = logo_gif.convert("RGBA")
        lw, lh = rgba.size
        # scale slightly smaller to leave room for viewfinder UI
        scale = min(width / lw, height / lh) * 0.75 
        nw, nh = int(lw * scale), int(lh * scale)
        resized = rgba.resize((nw, nh), Image.LANCZOS)
        logo_frames.append(resized)
        
    logo_frame_count = len(logo_frames)
    
    # Fonts
    try:
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../connectivity/static/fonts/JetBrainsMono-Bold.ttf"))
        font_sm = ImageFont.truetype(font_path, 10)
        font_lg = ImageFont.truetype(font_path, 16)
    except:
        font_sm = ImageFont.load_default()
        font_lg = ImageFont.load_default()
        
    frames = []
    
    # Phase 1: Viewfinder active, drawing logo, brackets locking in
    for f in range(logo_frame_count):
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw background tracking grid (+ marks)
        for x in range(20, width, 40):
            for y in range(20, height, 40):
                draw.line([(x-2, y), (x+2, y)], fill=faint_color, width=1)
                draw.line([(x, y-2), (x, y+2)], fill=faint_color, width=1)
                
        # Draw text overlays
        draw.text((10, 10), "SYS.BOOT", font=font_sm, fill=fg_color)
        
        # Simulating random hex addresses or focal length
        flen = 18 + int((f / logo_frame_count) * 32)
        draw.text((width - 50, 10), f"{flen}mm", font=font_sm, fill=fg_color)
        
        draw.text((10, height - 20), "v1.0.0", font=font_sm, fill=faint_color)
        draw.text((width - 60, height - 20), "AF-S", font=font_sm, fill=fg_color)
        
        # Brackets contract to lock focus
        progress = f / float(logo_frame_count)
        # Easing curve for snap
        ease = 1.0 - (1.0 - progress) ** 3
        margin = int(50 - 20 * ease)
        blen = 15
        bw = 2
        
        # Top-Left
        draw.line([(margin, margin), (margin+blen, margin)], fill=fg_color, width=bw)
        draw.line([(margin, margin), (margin, margin+blen)], fill=fg_color, width=bw)
        # Top-Right
        draw.line([(width-margin, margin), (width-margin-blen, margin)], fill=fg_color, width=bw)
        draw.line([(width-margin, margin), (width-margin, margin+blen)], fill=fg_color, width=bw)
        # Bottom-Left
        draw.line([(margin, height-margin), (margin+blen, height-margin)], fill=fg_color, width=bw)
        draw.line([(margin, height-margin), (margin, height-margin-blen)], fill=fg_color, width=bw)
        # Bottom-Right
        draw.line([(width-margin, height-margin), (width-margin-blen, height-margin)], fill=fg_color, width=bw)
        draw.line([(width-margin, height-margin), (width-margin, height-margin-blen)], fill=fg_color, width=bw)
        
        # Paste Logo
        lframe = logo_frames[f].convert("RGB")
        
        # Center the logo frame onto a blank image
        temp_img = Image.new("RGB", (width, height), bg_color)
        temp_img.paste(lframe, ((width - lframe.width)//2, (height - lframe.height)//2))
        
        # Use lighter to blend the white/beige arcs over the background grid, ignoring the charcoal background
        img = ImageChops.lighter(img, temp_img)
        
        frames.append(img)
        
    # Phase 2: Focus locked, AF box blinks green (or beige in our theme)
    hold_frames = 20
    base_hold_img = frames[-1].copy()
    
    for f in range(hold_frames):
        img = base_hold_img.copy()
        draw = ImageDraw.Draw(img)
        
        # Blink center AF box
        if (f // 4) % 2 == 0:
            cx, cy = width//2, height//2
            draw.rectangle([(cx-40, cy-40), (cx+40, cy+40)], outline=fg_color, width=1)
            # Add a 'LOCKED' text
            tw = 40
            draw.text((cx - tw//2, cy + 45), "LOCKED", font=font_sm, fill=fg_color)
            
        frames.append(img)
        
    # Phase 3: Shutter Snap Close
    snap_frames = 4
    for f in range(1, snap_frames + 1):
        img = base_hold_img.copy()
        draw = ImageDraw.Draw(img)
        # Top and bottom black/charcoal rectangles close in
        h = int((height / 2) * (f / snap_frames))
        draw.rectangle([(0, 0), (width, h)], fill=bg_color)
        draw.rectangle([(0, height - h), (width, height)], fill=bg_color)
        frames.append(img)
        
    # Phase 4: Shutter Snap Open (Revealing pure black for camera view transition)
    open_frames = 4
    for f in range(1, open_frames + 1):
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        h = int((height / 2) * (1.0 - (f / open_frames)))
        # The shutter leaves pure black behind it
        if h > 0:
            draw.rectangle([(0, 0), (width, h)], fill=bg_color)
            draw.rectangle([(0, height - h), (width, height)], fill=bg_color)
        frames.append(img)
        
    # Hold pure black for 2 frames
    frames.append(Image.new("RGB", (width, height), bg_color))
    frames.append(Image.new("RGB", (width, height), bg_color))

    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=40, loop=0)
    print(f"Generated {filename}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "creative_boot.gif")
    generate_creative_boot(out_path)

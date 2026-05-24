from PIL import Image, ImageDraw
import math
import random

def get_theme_colors(theme):
    if theme == "light":
        return {
            "bg": (253, 252, 251),           # #FDFCFB Off-white
            "light_accent": (197, 179, 154), # #C5B39A Beige
            "dark_accent": (140, 120, 95),   # Darker Beige
            "dotted": (210, 205, 195)        # Light grey/beige for dots
        }
    else: # dark
        return {
            "bg": (17, 17, 17),              # #111111 Black
            "light_accent": (197, 179, 154), # #C5B39A Beige
            "dark_accent": (255, 255, 255),  # #FFFFFF White
            "dotted": (60, 60, 60)           # #333333 Dark grey for dots
        }

def draw_dotted_line(draw, x1, y1, x2, y2, color, dash, gap, width, chalk=False):
    dx, dy = x2 - x1, y2 - y1
    dist = math.sqrt(dx**2 + dy**2)
    if dist == 0: return
    ux, uy = dx / dist, dy / dist
    curr = 0
    while curr < dist:
        end_dist = min(curr + dash, dist)
        if chalk:
            draw_chalky_line(draw, x1 + ux*curr, y1 + uy*curr, x1 + ux*end_dist, y1 + uy*end_dist, color, width)
        else:
            draw.line([(x1 + ux * curr, y1 + uy * curr), (x1 + ux * end_dist, y1 + uy * end_dist)], fill=color, width=width)
        curr += dash + gap

def draw_chalky_line(draw, x1, y1, x2, y2, color, width):
    draw.line([x1, y1, x2, y2], fill=color, width=width)
    length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    steps = int(length * 2)
    for s in range(steps):
        t = s / steps
        px = x1 + (x2-x1)*t
        py = y1 + (y2-y1)*t
        for _ in range(3):
            off_x = random.uniform(-width, width)
            off_y = random.uniform(-width, width)
            opacity_var = random.randint(-50, 50)
            p_color = tuple(max(0, min(255, c + opacity_var)) for c in color)
            draw.point((px + off_x, py + off_y), fill=p_color)

def draw_dotted_rect(draw, x, y, size_w, size_h, color, dash, gap, width, chalk=False):
    draw_dotted_line(draw, x, y, x + size_w, y, color, dash, gap, width, chalk)
    draw_dotted_line(draw, x + size_w, y, x + size_w, y + size_h, color, dash, gap, width, chalk)
    draw_dotted_line(draw, x + size_w, y + size_h, x, y + size_h, color, dash, gap, width, chalk)
    draw_dotted_line(draw, x, y + size_h, x, y, color, dash, gap, width, chalk)

def interpolate_color(c1, c2, factor):
    return tuple(int(c1[j] + (c2[j] - c1[j]) * factor) for j in range(3))

def draw_smooth_arc(draw, center_x, center_y, radius, start_deg, end_deg, color, width, chalk=False):
    steps = 400 if chalk else 150
    points = []
    for i in range(steps + 1):
        angle = math.radians(start_deg + (end_deg - start_deg) * i / steps)
        px = center_x + radius * math.cos(angle)
        py = center_y + radius * math.sin(angle)
        if chalk:
            px += random.uniform(-0.5, 0.5)
            py += random.uniform(-0.5, 0.5)
        points.append((px, py))
    if len(points) > 1:
        if chalk:
            for i in range(len(points) - 1):
                p1, p2 = points[i], points[i+1]
                draw_chalky_line(draw, p1[0], p1[1], p2[0], p2[1], color, width)
        else:
            draw.line(points, fill=color, width=width, joint="curve")

def generate_euclid_design(width, height, filename, theme="light", is_logo=False, transparent=False):
    colors = get_theme_colors(theme)
    bg = (0, 0, 0, 0) if transparent else colors["bg"]
    img = Image.new('RGBA' if transparent else 'RGB', (width, height), bg)
    draw = ImageDraw.Draw(img)
    scale = min(width / 320, height / 240)
    max_w, max_h = 300 * scale, 220 * scale
    container_x, container_y = (width - max_w) // 2, (height - max_h) // 2
    main_dash, main_gap, pen_width = int(3 * scale), int(7 * scale), max(1, int(scale))
    
    phi = (1 + 5**0.5) / 2
    curr_x, curr_y = container_x, container_y + (max_h - (max_w / phi)) / 2
    curr_w, curr_h = max_w, max_w / phi
    
    for i in range(12):
        s = min(curr_w, curr_h)
        mode, factor = i % 4, i / 11.0
        color = interpolate_color(colors["dark_accent"], colors["light_accent"], factor)
        arc_width = int(max(int(scale), int((4 - i//3) * scale)) * (1.5 if is_logo else 1))
        draw_dotted_rect(draw, curr_x, curr_y, s, s, colors["dotted"], main_dash, main_gap, pen_width, chalk=is_logo)
        
        if mode == 0: 
            draw_smooth_arc(draw, curr_x + s, curr_y + s, s, 180, 270, color, arc_width, chalk=is_logo)
            curr_x += s; curr_w -= s
        elif mode == 1:
            draw_smooth_arc(draw, curr_x, curr_y + s, s, 270, 360, color, arc_width, chalk=is_logo)
            curr_y += s; curr_h -= s
        elif mode == 2:
            draw_smooth_arc(draw, curr_x + curr_w - s, curr_y, s, 0, 90, color, arc_width, chalk=is_logo)
            curr_w -= s
        elif mode == 3:
            draw_smooth_arc(draw, curr_x + s, curr_y + curr_h - s, s, 90, 180, color, arc_width, chalk=is_logo)
            curr_h -= s
    
    text_x, text_y = container_x + 10 * scale, container_y + max_h - 40 * scale
    draw_chalky_text(draw, text_x, text_y - 18 * scale, "EC", colors["light_accent"], 32, scale)
    
    img.save(filename, "JPEG", quality=95) if filename.endswith(".jpeg") else img.save(filename)
    print(f"Generated: {filename}")

def draw_chalky_text(draw, x, y, text, color, size, scale, center=False, font_name="JetBrainsMono-Bold.ttf", anchor=None):
    try:
        from PIL import ImageFont
        import os
        font_path = os.path.join(os.path.dirname(__file__), f"../Webapp/assets/fonts/{font_name}")
        font = ImageFont.truetype(font_path, int(size * scale))
    except Exception:
        font = ImageFont.load_default()
    
    if center:
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = x - w / 2
            y = y - h / 2
        except AttributeError:
            w, h = draw.textsize(text, font=font)
            x = x - w / 2
            y = y - h / 2

    import random
    import json
    
    multi_stroke = 3
    jitter = [-1, 1]
    try:
        with open(os.path.join(os.path.dirname(__file__), "chalk_settings.json")) as f:
            settings = json.load(f)
            multi_stroke = settings.get("chalk_effect", {}).get("multi_stroke", 3)
            jitter = settings.get("chalk_effect", {}).get("jitter_range", [-1, 1])
    except Exception:
        pass

    for _ in range(multi_stroke):
        jx = x + random.uniform(jitter[0], jitter[1])
        jy = y + random.uniform(jitter[0], jitter[1])
        
        if anchor:
            try:
                draw.text((jx, jy), text, fill=color, font=font, anchor=anchor)
                continue
            except TypeError:
                pass
        
        draw.text((jx, jy), text, fill=color, font=font)

def generate_construction_gif(width, height, filename, theme="light", duration=150):
    colors = get_theme_colors(theme)
    frames = []
    img = Image.new('RGB', (width, height), colors["bg"])
    draw = ImageDraw.Draw(img)
    scale = min(width / 320, height / 240)
    max_w, max_h = 300 * scale, 220 * scale
    container_x, container_y = (width - max_w) // 2, (height - max_h) // 2
    main_dash, main_gap, pen_width = int(3 * scale), int(7 * scale), max(1, int(scale))
    
    frames.append(img.copy())

    phi = (1 + 5**0.5) / 2
    curr_x, curr_y = container_x, container_y + (max_h - (max_w / phi)) / 2
    curr_w, curr_h = max_w, max_w / phi
    
    radii = []
    text_x, text_y = container_x + 10 * scale, container_y + max_h - 40 * scale
    
    for i in range(12):
        s = min(curr_w, curr_h)
        radii.append(int(s/scale)) 
        
        mode, factor = i % 4, i / 11.0
        color = interpolate_color(colors["dark_accent"], colors["light_accent"], factor)
        arc_width = int(max(int(scale), int((4 - i//3) * scale)))
        
        if i == 0:
            equation = f"R0 = {radii[0]}"
        elif i == 1:
            equation = f"R1 = {radii[1]}"
        else:
            equation = f"R{i} = R{i-1} + R{i-2} = {radii[i]}"
            
        draw_dotted_rect(draw, curr_x, curr_y, s, s, colors["dotted"], main_dash, main_gap, pen_width)
        
        temp_img = img.copy()
        temp_draw = ImageDraw.Draw(temp_img)
        draw_chalky_text(temp_draw, text_x, text_y, equation, colors["light_accent"], 14, scale)
        frames.append(temp_img)
        
        if mode == 0: 
            draw_smooth_arc(draw, curr_x + s, curr_y + s, s, 180, 270, color, arc_width)
            curr_x += s; curr_w -= s
        elif mode == 1:
            draw_smooth_arc(draw, curr_x, curr_y + s, s, 270, 360, color, arc_width)
            curr_y += s; curr_h -= s
        elif mode == 2:
            draw_smooth_arc(draw, curr_x + curr_w - s, curr_y, s, 0, 90, color, arc_width)
            curr_w -= s
        elif mode == 3:
            draw_smooth_arc(draw, curr_x + s, curr_y + curr_h - s, s, 90, 180, color, arc_width)
            curr_h -= s
            
        temp_img = img.copy()
        temp_draw = ImageDraw.Draw(temp_img)
        draw_chalky_text(temp_draw, text_x, text_y, equation, color, 14, scale)
        frames.append(temp_img)
    
    for _ in range(30):
        temp_img = img.copy()
        temp_draw = ImageDraw.Draw(temp_img)
        # Shift up by exactly the difference in font size (32 - 14 = 18) to match the baseline!
        draw_chalky_text(temp_draw, text_x, text_y - 18 * scale, "EC", colors["light_accent"], 32, scale)
        frames.append(temp_img)
        
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=duration, loop=0)
    print(f"Generated: {filename} (Animated GIF)")

if __name__ == "__main__":
    # Light Mode Assets
    generate_euclid_design(320, 240, "euclid_splash_light.png", theme="light")
    generate_euclid_design(1024, 1024, "euclid_logo_light.jpeg", theme="light", is_logo=True)
    generate_euclid_design(1024, 1024, "transparent_logo_light.png", theme="light", is_logo=True, transparent=True)
    generate_construction_gif(640, 480, "euclid_construction_light.gif", theme="light")
    
    # Dark Mode Assets
    generate_euclid_design(320, 240, "euclid_splash_dark.png", theme="dark")
    generate_euclid_design(1024, 1024, "euclid_logo_dark.jpeg", theme="dark", is_logo=True)
    generate_euclid_design(1024, 1024, "transparent_logo_dark.png", theme="dark", is_logo=True, transparent=True)
    generate_construction_gif(640, 480, "euclid_construction_dark.gif", theme="dark")
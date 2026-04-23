import numpy as np
from PIL import Image, ImageDraw

MAUVE = (224, 176, 255)

def overlay_ui(frame, config, screen_res):
    """
    Overlays UI indicators on the camera frame with rotation and padding support.
    Now abstracted into its own module.
    """
    if config is None:
        return frame
        
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    
    rotation = config.get("ui_rotation", 0)
    padding = config.get("ui_padding", 20)
    
    # Use screen_res passed from caller
    w, h = screen_res
    
    # Calculate base positions based on rotation
    if rotation == 0:
        x_base, y_base = w - padding, padding
    elif rotation == 90:
        x_base, y_base = w - padding, h - padding
    elif rotation == 180:
        x_base, y_base = padding, h - padding
    else: # 270
        x_base, y_base = padding, padding

    # Vertical alignment center
    y_row = y_base + 5
    
    # Flash Icon (Thunderbolt) - Moved up slightly
    if config.get("flash"):
        x, y = x_base - 15, y_row - 14
        points = [
            (x, y), (x - 8, y + 8),
            (x - 4, y + 8), (x - 12, y + 20),
            (x - 4, y + 12), (x - 8, y + 12),
            (x, y)
        ]
        draw.polygon(points, fill=MAUVE)
    
    # Battery Placeholder - Centered on y_row
    x_batt = x_base - 75
    y_batt = y_row - 10
    draw.rectangle([x_batt, y_batt, x_batt + 20, y_batt + 10], outline=MAUVE, width=2)
    draw.rectangle([x_batt + 20, y_batt + 3, x_batt + 22, y_batt + 7], fill=MAUVE)
    
    # WiFi Placeholder - Centered on y_row
    x_wifi = x_base - 115
    y_wifi = y_row - 10
    for i in range(1, 4):
        # Draw small arcs for wifi
        r = i * 4
        bbox = [x_wifi + 10 - r, y_wifi + 10 - r, x_wifi + 10 + r, y_wifi + 10 + r]
        draw.arc(bbox, 225, 315, fill=MAUVE, width=2)

    return np.array(img)

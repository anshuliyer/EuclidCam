import json

def _map_to_command(raw_x, raw_y, ui_state, config, screen_res):
    c = config
    if c.get("swap_xy"): raw_x, raw_y = raw_y, raw_x
    
    x_norm = (raw_x - c["x_min"]) / (c["x_max"] - c["x_min"])
    y_norm = (raw_y - c["y_min"]) / (c["y_max"] - c["y_min"])
    if c.get("invert_x"): x_norm = 1.0 - x_norm
    if c.get("invert_y"): y_norm = 1.0 - y_norm
    
    if ui_state.get("ui_rotation") == 180:
        x_norm = 1.0 - x_norm
        y_norm = 1.0 - y_norm
    
    x = x_norm * screen_res[0]
    y = y_norm * screen_res[1]
    w, h = screen_res

    # ... skipping top layers for this test since we know they are false ...
    
    if x < 120 and y > h - 120:
        return "GALLERY", x, y
        
    if x > w - 120 and y > h - 120:
        return "SPACE", x, y
        
    if 80 < x < w - 80 and 80 < y < h - 80: 
        return "ENTER", x, y

    return None, x, y

config = {
  "x_min": 700,
  "x_max": 3850,
  "y_min": 850,
  "y_max": 3600,
  "swap_xy": True,
  "invert_x": False,
  "invert_y": True
}
ui_state = {}
print(_map_to_command(848, 3328, ui_state, config, (320, 240)))

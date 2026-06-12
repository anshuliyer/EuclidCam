import os
import json
import board
import digitalio

class TouchInterface:
    def __init__(self, config_path, screen_res):
        self.config = self._load_config(config_path)
        self.screen_res = screen_res
        self.last_x = 0
        self.last_y = 0
        self.touch_active = False
        
        # Setup pure Python XPT2046 over SPI
        try:
            self.spi = board.SPI()
            self.cs = digitalio.DigitalInOut(board.D7) # CS1
            self.cs.direction = digitalio.Direction.OUTPUT
            self.cs.value = True
            
            self.irq = digitalio.DigitalInOut(board.D17) # penirq
            self.irq.direction = digitalio.Direction.INPUT
            self.irq.pull = digitalio.Pull.UP
            self.hardware_ok = True
        except Exception as e:
            print(f"[TOUCH] Hardware init failed: {e}")
            self.hardware_ok = False

    def _load_config(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return None

    def _read_raw(self):
        if not self.hardware_ok or self.irq.value: # Active low
            return None, None, False
            
        while not self.spi.try_lock():
            pass
            
        try:
            # Lowering baudrate to 1MHz significantly increases ADC stability on jumper wires
            self.spi.configure(baudrate=1000000)
            
            xs, ys = [], []
            buf = bytearray(3)
            
            self.cs.value = False
            
            # Read X (0xD0) consecutively to allow physical RC layers to settle
            self.spi.write_readinto(bytearray([0xD0, 0x00, 0x00]), buf) # Dummy read to settle voltage
            for _ in range(15):
                self.spi.write_readinto(bytearray([0xD0, 0x00, 0x00]), buf)
                x = (buf[1] << 5) | (buf[2] >> 3)
                xs.append(x)
                
            # Read Y (0x90) consecutively
            self.spi.write_readinto(bytearray([0x90, 0x00, 0x00]), buf) # Dummy read to settle voltage
            for _ in range(15):
                self.spi.write_readinto(bytearray([0x90, 0x00, 0x00]), buf)
                y = (buf[1] << 5) | (buf[2] >> 3)
                ys.append(y)
                
            self.cs.value = True
                
            xs.sort()
            ys.sort()
            
            # Slice the middle 5 samples (throw away 5 highest and 5 lowest outliers)
            mid_xs = xs[5:10]
            mid_ys = ys[5:10]
            
            # Fat finger / Smudge rejection
            # Relaxed the spread from 150 to 300 to accept lighter, less-stable touches (increases perceived sensitivity)
            if (mid_xs[-1] - mid_xs[0]) > 300 or (mid_ys[-1] - mid_ys[0]) > 300:
                return None, None, True # Touching, but too noisy to use
                
            return mid_xs[2], mid_ys[2], True # Return median of stable touch
        finally:
            self.spi.unlock()

    def get_touch_command(self, ui_state):
        if not self.config: return None
        
        x, y, is_touching = self._read_raw()
        
        if is_touching:
            # Finger is on the screen
            if x is not None and y is not None:
                # Touch is stable, record the coordinate
                self.touch_active = True
                self.last_x, self.last_y = x, y
        else:
            # Finger has physically left the screen
            if self.touch_active:
                self.touch_active = False
                cmd, mapped_x, mapped_y = self._map_to_command(self.last_x, self.last_y, ui_state)
                if cmd:
                    print(f"[TOUCH] {cmd} at ({int(mapped_x)}, {int(mapped_y)})")
                return cmd
                
        return None

    def _map_to_command(self, raw_x, raw_y, ui_state):
        c = self.config
        if c.get("swap_xy"): raw_x, raw_y = raw_y, raw_x
        
        x_norm = (raw_x - c["x_min"]) / (c["x_max"] - c["x_min"])
        y_norm = (raw_y - c["y_min"]) / (c["y_max"] - c["y_min"])
        if c.get("invert_x"): x_norm = 1.0 - x_norm
        if c.get("invert_y"): y_norm = 1.0 - y_norm
        
        # Apply orientation flip if set to 180
        if ui_state.get("ui_rotation") == 180:
            x_norm = 1.0 - x_norm
            y_norm = 1.0 - y_norm
        
        x = x_norm * self.screen_res[0]
        y = y_norm * self.screen_res[1]
        w, h = self.screen_res

        # --- Layer 1: High Priority Overlays (Gallery/Connection) ---
        if ui_state.get("show_connection_view"):
            overlay_w, overlay_h = 300, 240
            ox, oy = (w - overlay_w) // 2, (h - overlay_h) // 2
            # Close Button exact drawn bounds: [ox + overlay_w - 70, oy + 10, ox + overlay_w - 10, oy + 70]
            if ox + overlay_w - 70 <= x <= ox + overlay_w - 10 and oy + 10 <= y <= oy + 70:
                return "BACK", x, y
            # Block fallthrough: if they tapped inside the connection overlay but missed the cross
            return None, x, y

        if ui_state.get("show_gallery"):
            # 1. Delete Button (Top Left): _draw_bin_icon exact bounds [12, 12, 52, 52]
            if 12 <= x <= 52 and 12 <= y <= 52: 
                return "DOWN", x, y
            
            # 2. BT Send Button (Top Right next to Close): _draw_bt_icon exact bounds [w - 100, 12, w - 60, 52]
            if ui_state.get("bluetooth_on"):
                if w - 100 <= x <= w - 60 and 12 <= y <= 52: 
                    return "BT_SEND", x, y
                
            # 3. Close Button (Top Right extreme): _draw_gallery_view exact bounds [w - 52, 12, w - 12, 52]
            if w - 52 <= x <= w - 12 and 12 <= y <= 52: 
                return "BACK", x, y
            
            # 4. Left Navigation Arrow: exact bounds [25, h // 2 - 25, 50, h // 2 + 25]
            if 10 <= x <= 65 and (h // 2 - 35) <= y <= (h // 2 + 35):
                return "LEFT", x, y
                
            # 5. Right Navigation Arrow: exact bounds [w - 50, h // 2 - 25, w - 25, h // 2 + 25]
            if w - 65 <= x <= w - 10 and (h // 2 - 35) <= y <= (h // 2 + 35):
                return "RIGHT", x, y
                
            # Ignore random touches in the gallery that don't hit a button
            return None, x, y

        # --- Layer 2: Menu System (Grid + Header) ---
        if ui_state.get("show_menu"):
            # Menu Close Button (Top Right): _draw_menu exact bounds [w - 45, 5, w - 10, 40]
            if w - 55 <= x <= w and 0 <= y <= 50: 
                return "BACK", x, y
            
            # Grid Detection (Prioritize this over edge-back)
            sub = ui_state.get("current_submenu")
            is_sub = ui_state.get("show_submenu")
            
            if is_sub and sub == "Modes": 
                max_items, cols, rows = 4, 2, 2
                
                # Pagination arrows at the bottom
                if y > h - 50:
                    if x < w // 2: return "LEFT", x, y
                    else: return "RIGHT", x, y
                    
            elif is_sub and sub == "Grid": max_items, cols, rows = 3, 2, 2
            elif is_sub and sub == "Connect": max_items, cols, rows = 4, 2, 2
            else: max_items, cols, rows = 4, 2, 2
            
            grid_m_x, grid_m_y, header_h, gap = 15, 5, 45, 8
            avail_w = w - (grid_m_x * 2)
            avail_h = h - header_h - (grid_m_y * 2)
            if is_sub and sub == "Modes":
                avail_h -= 40 # Pagination space
                
            btn_w = (avail_w - (gap * (cols - 1))) // cols
            btn_h = (avail_h - (gap * (rows - 1))) // rows
            
            rel_x = x - grid_m_x
            rel_y = y - (header_h + grid_m_y)
            
            col = int(rel_x // (btn_w + gap))
            row = int(rel_y // (btn_h + gap))
            
            if 0 <= col < cols and 0 <= row < rows:
                lx, ly = rel_x % (btn_w + gap), rel_y % (btn_h + gap)
                if lx < btn_w and ly < btn_h:
                    idx = row * cols + col
                    if idx < max_items:
                        ui_state["touch_menu_idx"] = idx
                        return "TOUCH_SELECT", x, y
            
            # If in menu area but not on a button, check for edge close (Strict)
            if x < 10 or x > w - 10 or y > h - 10:
                return "BACK", x, y

        # --- Layer 3: Main UI State ---
        padding = ui_state.get("ui_padding", 20)
        
        # Gear (Settings): _draw_gear exact bounds [w - padding - 42, h - padding - 42, w - padding + 2, h - padding + 2]
        gx, gy = w - padding - 20, h - padding - 20
        if gx - 25 <= x <= gx + 25 and gy - 25 <= y <= gy + 25: 
            return "SPACE", x, y
            
        # Gallery (Bottom Left): _draw_gallery_icon exact bounds [padding + 5, h - padding - 35, padding + 45, h - padding - 5]
        gal_x, gal_y = padding + 5, h - padding - 35
        if gal_x - 10 <= x <= gal_x + 50 and gal_y - 10 <= y <= gal_y + 40: 
            return "GALLERY", x, y
        # Capture (Center)
        if not ui_state.get("show_menu") and not ui_state.get("show_gallery"):
            if 80 < x < w - 80 and 80 < y < h - 80: return "ENTER", x, y

        return None, x, y

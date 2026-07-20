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
            # Increased the spread from 300 to 800 to accept much lighter, noisier touches
            if (mid_xs[-1] - mid_xs[0]) > 800 or (mid_ys[-1] - mid_ys[0]) > 800:
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
                print(f"[DEBUG TOUCH] RAW: ({self.last_x}, {self.last_y}) -> MAPPED: ({int(mapped_x)}, {int(mapped_y)}) -> CMD: {cmd}")
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

        # --- Layer 1: High Priority Overlays (Connection) ---
        if ui_state.get("show_connection_view"):
            # Close button (Top Right): Huge 120x120 hit box
            if x > w - 120 and y < 120:
                return "BACK", x, y
            return None, x, y

        # --- Layer 2: Gallery ---
        if ui_state.get("show_gallery"):
            # Top Left (Delete): 100x100 box
            if x < 100 and y < 100:
                return "DOWN", x, y
                
            # Top Right (Close): 80x100 box at extreme right
            if x > w - 80 and y < 100:
                return "BACK", x, y
                
            # Top Right (BT Send): 80x100 box next to close
            if ui_state.get("bluetooth_on") and w - 160 < x <= w - 80 and y < 100:
                return "BT_SEND", x, y
                
            # Left Nav: Entire left edge below top 100px
            if x < 100 and y >= 100:
                return "LEFT", x, y
                
            # Right Nav: Entire right edge below top 100px
            if x > w - 100 and y >= 100:
                return "RIGHT", x, y
                
            return None, x, y

        # --- Layer 3: Menu System ---
        if ui_state.get("show_menu"):
            # Menu Close Button (Top Right): Huge 100x100 hit box
            if x > w - 100 and y < 100:
                return "BACK", x, y
            
            sub = ui_state.get("current_submenu")
            is_sub = ui_state.get("show_submenu")
            
            if is_sub and sub == "Modes": 
                max_items, cols, rows = 4, 2, 2
                # Pagination arrows: Bottom 80px
                if y > h - 80:
                    if x < w // 2: return "LEFT", x, y
                    else: return "RIGHT", x, y
                    
            elif is_sub and sub == "Grid": max_items, cols, rows = 3, 2, 2
            elif is_sub and sub == "Connect": max_items, cols, rows = 4, 2, 2
            else: max_items, cols, rows = 4, 2, 2
            
            header_h = 45
            avail_w = w
            avail_h = h - header_h
            if is_sub and sub == "Modes":
                avail_h -= 80 # Reserve pagination space
                
            # Only process grid if below header
            if y > header_h and y < (header_h + avail_h):
                rel_x = x
                rel_y = y - header_h
                
                col = int(rel_x / (avail_w / cols))
                row = int(rel_y / (avail_h / rows))
                
                if 0 <= col < cols and 0 <= row < rows:
                    idx = row * cols + col
                    if idx < max_items:
                        ui_state["touch_menu_idx"] = idx
                        return "TOUCH_SELECT", x, y
            
            return None, x, y

        # --- Layer 4: Main Viewfinder UI ---
        # Bottom Left corner (Gallery): 120x120 hit box
        if x < 120 and y > h - 120:
            return "GALLERY", x, y
            
        # Bottom Right corner (Settings): 120x120 hit box
        if x > w - 120 and y > h - 120:
            return "SPACE", x, y
            
        # Capture: Anything else that is roughly in the center
        if 80 < x < w - 80 and 80 < y < h - 80: 
            return "ENTER", x, y

        return None, x, y

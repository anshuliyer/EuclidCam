import numpy as np
from PIL import Image, ImageDraw

class CompositionGrid:
    """
    Handles drawing compositional grids (3x3, Golden Ratio/Euclid) on PIL images.
    """
    OFF = "OFF"
    GRID_3x3 = "3x3"
    EUCLID = "Euclid"

    def __init__(self, color=(60, 60, 60), width=1):
        self.color = color
        self.width = width

    def apply(self, pil_img, mode):
        """
        Applies the selected grid mode to the PIL image.
        """
        if mode == self.OFF or not mode:
            return pil_img
        
        draw = ImageDraw.Draw(pil_img)
        w, h = pil_img.size

        if mode == self.GRID_3x3:
            # Rule of Thirds
            # Vertical
            draw.line([(w // 3, 0), (w // 3, h)], fill=self.color, width=self.width)
            draw.line([(2 * w // 3, 0), (2 * w // 3, h)], fill=self.color, width=self.width)
            # Horizontal
            draw.line([(0, h // 3), (w, h // 3)], fill=self.color, width=self.width)
            draw.line([(0, 2 * h // 3), (w, 2 * h // 3)], fill=self.color, width=self.width)
        
        elif mode == self.EUCLID:
            # True Golden Spiral (Fibonacci recursive squares and arcs)
            phi = 1.61803398875
            
            # Center a perfect Golden Rectangle in the screen
            if w / h > phi:
                # Screen is wider than GR, center horizontally
                gr_h = h
                gr_w = int(h * phi)
                x0 = (w - gr_w) // 2
                y0 = 0
            else:
                # Screen is taller than GR, center vertically
                gr_w = w
                gr_h = int(w / phi)
                x0 = 0
                y0 = (h - gr_h) // 2

            rx, ry, rw, rh = x0, y0, gr_w, gr_h
            
            # Direction of the cut: 0: right, 1: top, 2: left, 3: bottom
            direction = 0
            for i in range(8): # 8 iterations is visually perfect
                if rw < 2 or rh < 2: break
                
                sq = min(rw, rh)
                
                if direction == 0: # Right
                    sx, sy = rx + rw - sq, ry
                    rw -= sq
                    cx, cy = sx, sy + sq
                    start, end = 270, 360
                elif direction == 1: # Top
                    sx, sy = rx, ry
                    ry += sq
                    rh -= sq
                    cx, cy = sx + sq, sy + sq
                    start, end = 180, 270
                elif direction == 2: # Left
                    sx, sy = rx, ry
                    rx += sq
                    rw -= sq
                    cx, cy = sx + sq, sy
                    start, end = 90, 180
                else: # Bottom
                    sx, sy = rx, ry + rh - sq
                    rh -= sq
                    cx, cy = sx, sy
                    start, end = 0, 90
                    
                # Draw the bounding square
                draw.rectangle([sx, sy, sx + sq, sy + sq], outline=self.color, width=self.width)
                
                # Draw the golden arc
                draw.arc([cx - sq, cy - sq, cx + sq, cy + sq], start, end, fill=self.color, width=max(1, self.width))
                
                direction = (direction + 1) % 4
                
        return pil_img

if __name__ == "__main__":
    # Simple standalone verification (Mocks FB/Camera if needed, but here just testing PIL)
    print("CompositionGrid Class test...")
    test_img = Image.new('RGB', (480, 320), color=(255, 255, 255))
    grid = CompositionGrid()
    
    # Test Euclid
    res = grid.apply(test_img.copy(), CompositionGrid.EUCLID)
    res.save("test_euclid.png")
    print("Saved test_euclid.png")
    
    # Test 3x3
    res = grid.apply(test_img.copy(), CompositionGrid.GRID_3x3)
    res.save("test_3x3.png")
    print("Saved test_3x3.png")

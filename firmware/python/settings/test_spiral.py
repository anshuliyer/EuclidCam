from PIL import Image, ImageDraw

def test_spiral():
    w, h = 320, 240
    pil_img = Image.new("RGB", (w, h), (0, 0, 0))
    draw = ImageDraw.Draw(pil_img)
    
    phi = 1.61803398875
    gr_w = w
    gr_h = int(w / phi)
    x0 = 0
    y0 = (h - gr_h) // 2
    
    rx, ry, rw, rh = x0, y0, gr_w, gr_h
    
    dir = 0
    for i in range(8):
        if rw < 2 or rh < 2: break
        sq = min(rw, rh)
        
        if dir == 0: # Right
            sx, sy = rx + rw - sq, ry
            rw -= sq
            cx, cy = sx, sy + sq
            start, end = 270, 360
        elif dir == 1: # Top
            sx, sy = rx, ry
            ry += sq
            rh -= sq
            cx, cy = sx + sq, sy + sq
            start, end = 180, 270
        elif dir == 2: # Left
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
            
        draw.rectangle([sx, sy, sx + sq, sy + sq], outline=(100,100,100), width=1)
        draw.arc([cx - sq, cy - sq, cx + sq, cy + sq], start, end, fill=(250,214,165), width=2)
        
        dir = (dir + 1) % 4
        
    pil_img.save("spiral_test.png")

if __name__ == "__main__":
    test_spiral()

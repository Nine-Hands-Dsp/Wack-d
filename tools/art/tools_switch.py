import cv2, numpy as np
from PIL import Image, ImageDraw
W, H, R = 556, 192, 9          # fente commune (px photo)
def slot(src, cx, cy):
    im = Image.open(src).convert('RGBA')
    c = im.crop((int(cx - W / 2), int(cy - H / 2), int(cx + W / 2), int(cy + H / 2)))
    ss = 4
    m = Image.new('L', (W * ss, H * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, W * ss - 1, H * ss - 1), radius=R * ss, fill=255)
    a = np.asarray(c).copy()
    a[..., 3] = (np.asarray(m.resize((W, H), Image.LANCZOS)).astype(np.float32) * a[..., 3] / 255).astype(np.uint8)
    return Image.fromarray(a)
slot('in/sw_off.png', 622.5, 646.0).save('parts/slide_left.png')
slot('in/sw_on.png', 625.0, 647.0).save('parts/slide_right.png')

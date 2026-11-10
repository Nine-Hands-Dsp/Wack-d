import numpy as np, cv2, colorsys
from PIL import Image
a = np.asarray(Image.open('in/led.png').convert('RGBA')).astype(np.float32) / 255
rgb, al = a[..., :3], a[..., 3]
hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)          # H 0..360, S 0..1, V 0..1
lens = ((hsv[..., 1] > 0.35) & (al > 0.5)).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(lens, 8)
b = 1 + np.argmax(st[1:, 4]); lens = (lab == b).astype(np.uint8)
cnt, _ = cv2.findContours(lens, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
(cx, cy), rad = cv2.minEnclosingCircle(max(cnt, key=cv2.contourArea))
print('lentille', round(cx, 1), round(cy, 1), round(rad, 1))
yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(np.float32)
r = np.hypot(xx - cx, yy - cy)
m = np.clip((rad + 1.5 - r) / 3.0, 0, 1)            # disque de la lentille, bord doux
V = hsv[..., 2]
def recolor(hue, sat_scale, core_white):
    h = np.full_like(V, hue)
    s = np.clip(hsv[..., 1] * sat_scale * (1 - core_white * np.clip((V - 0.75) / 0.25, 0, 1)), 0, 1)
    v = np.clip(V * 1.0, 0, 1)
    out = cv2.cvtColor(np.dstack([h, s, v]).astype(np.float32), cv2.COLOR_HSV2RGB)
    return rgb * (1 - m[..., None]) + out * m[..., None]
blue = recolor(196.0, 0.80, 0.55)
amber = recolor(36.0, 0.95, 0.45)
# eteinte : lentille sombre, legere teinte, alveoles visibles
gray = V
off_rgb = np.dstack([gray * 0.20, gray * 0.22, gray * 0.25]) + 0.02
off = rgb * (1 - m[..., None]) + off_rgb * m[..., None]
# halo optique : on renforce un peu la luminance du centre allume (pas de disque flou)
for name, img in (('blue', blue), ('amber', amber), ('off', off)):
    Image.fromarray((np.dstack([np.clip(img, 0, 1), al]) * 255).astype(np.uint8)).save(f'parts/led_{name}.png')
np.save('parts/led_geom.npy', np.array([cx, cy, rad]))

import cv2, numpy as np
from PIL import Image
a = np.asarray(Image.open('in/knob_round.png').convert('RGBA')).astype(np.float32)
rgb, al = a[..., :3], a[..., 3] / 255
H, W = al.shape
ys, xs = np.where(al > 0.5)
cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.hypot(xx - cx, yy - cy); th = np.arctan2(yy - cy, xx - cx)
L = rgb.mean(2); sat = rgb.max(2) - rgb.min(2)
mk = ((L > 120) & (r < 330)).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(mk, 8)
b = 1 + np.argmax(st[1:, 4]); mk = (lab == b).astype(np.uint8)
mx, my, mw, mh = st[b, :4]
print('centre', cx, cy, 'marker', mx, my, mw, mh, 'marker cx', mx + mw / 2)
mkd = cv2.dilate(mk, np.ones((17, 17), np.uint8))
# marqueur : pixels du trait + bord doux
mmask = cv2.GaussianBlur(cv2.dilate(mk, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 0.8)
marker = np.dstack([rgb, np.clip(mmask, 0, 1) * 255])
M = np.float32([[1, 0, -5], [0, 1, 0]])
marker = cv2.warpAffine(marker, M, (W, H), flags=cv2.INTER_CUBIC)
# chapeau sans marqueur : on remplace la zone par le meme rayon pris 25 deg plus loin
ang = np.radians(25)
mapx = (cx + r * np.cos(th + ang)).astype(np.float32); mapy = (cy + r * np.sin(th + ang)).astype(np.float32)
rot = np.dstack([cv2.remap(rgb[..., c], mapx, mapy, cv2.INTER_CUBIC) for c in range(3)])
w = cv2.GaussianBlur(mkd.astype(np.float32), (0, 0), 2)[..., None]
body = rgb * (1 - w) + rot * w
# centre : moyenne locale + grain (evite la trace en eventail)
cmask = np.clip((60 - r) / 20, 0, 1)[..., None]
avg = cv2.GaussianBlur(body, (0, 0), 25)
grain = body - cv2.GaussianBlur(body, (0, 0), 2)
body = body * (1 - cmask) + (avg + grain) * cmask
# aplatir l'eclairage tournant : gain angulaire basse frequence (cap et couronne separes)
Lb = body.mean(2)
out = body.copy()
for r0, r1 in ((305, 360),):
    ring = (r >= r0) & (r < r1) & (al > 0.9)
    bins = np.linspace(-np.pi, np.pi, 73)
    idx = np.digitize(th, bins) - 1
    prof = np.array([Lb[ring & (idx == k)].mean() if np.any(ring & (idx == k)) else np.nan for k in range(72)])
    prof = np.nan_to_num(prof, nan=np.nanmean(prof))
    prof = np.convolve(np.r_[prof[-6:], prof, prof[:6]], np.ones(9) / 9, 'same')[6:-6]
    g = np.nanmean(prof) / np.maximum(prof, 1)
    gain = g[np.clip(idx, 0, 71)]
    sel = (r >= r0) & (r < r1)
    out[sel] = body[sel] * gain[sel][:, None]
    print('ring', r0, 'eclairage min/max', prof.min().round(1), prof.max().round(1))
crowncap = np.dstack([out, al * 255])
# ombre : alpha floute, centree
sh = cv2.GaussianBlur(al, (0, 0), 14) * 0.85
shadow = np.dstack([np.zeros_like(rgb), sh * 255])
# reflets fixes (haut-gauche 45 deg) : liseré sur la couronne + leger voile sur le chapeau
R = 346.0
d = np.cos(th - np.radians(-135))                       # 1 cote lumiere
rim = np.exp(-((r - (R - 8)) / 9) ** 2) * np.clip(d, 0, 1) ** 2 * 0.55
lin = ((cx - xx) + (cy - yy)) / (np.sqrt(2) * 300)          # +1 en haut a gauche, -1 en bas a droite
capg = np.clip(lin, 0, 1) * 0.09 * np.clip((300 - r) / 8, 0, 1)
shade = np.exp(-((r - (R - 10)) / 14) ** 2) * np.clip(-d, 0, 1) ** 1.5 * 0.45 \
      + np.clip(-lin, 0, 1) * 0.10 * np.clip((300 - r) / 8, 0, 1)
hl = np.clip(rim + capg, 0, 1) * al
sd = np.clip(shade, 0, 1) * al
alpha = np.clip(hl + sd, 0, 1)
col = np.where((hl >= sd)[..., None], 255.0, 0.0) * np.ones_like(rgb)
highlight = np.dstack([col, alpha * 255])
# recadrage carre centre sur l'axe
S = 760
def sq(img):
    out = np.zeros((S, S, 4), np.float32)
    x0, y0 = int(round(cx - S / 2)), int(round(cy - S / 2))
    sx0, sy0 = max(0, x0), max(0, y0); sx1, sy1 = min(W, x0 + S), min(H, y0 + S)
    out[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = img[sy0:sy1, sx0:sx1]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))
for n, img in (('shadow', shadow), ('crowncap', crowncap), ('marker', marker), ('highlight', highlight)):
    sq(img).save(f'parts/knob_{n}.png')

import numpy as np, cv2
from PIL import Image
a = np.asarray(Image.open('in/knob.png').convert('RGBA')).astype(np.float32)
H, W = a.shape[:2]; al = a[..., 3] / 255
# centre : ellipse ajustee sur le contour
m = (al > 0.5).astype(np.uint8)
cnt = max(cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea)
(ecx, ecy), (ea, eb), eang = cv2.fitEllipse(cnt)
print('ellipse', round(ecx, 1), round(ecy, 1), round(ea, 1), round(eb, 1), round(eang, 1))
# rayon du bord par angle (pointes des crans), lisse sur ~12 deg
NT = 720
ts = np.linspace(-np.pi, np.pi, NT, endpoint=False)
rs = np.arange(250, 420, 0.5)
edge = np.zeros(NT)
for i, t in enumerate(ts):
    xs = ecx + rs * np.cos(t); ys = ecy + rs * np.sin(t)
    v = cv2.remap(al, xs.astype(np.float32)[None], ys.astype(np.float32)[None], cv2.INTER_LINEAR)[0]
    idx = np.where(v > 0.5)[0]
    edge[i] = rs[idx.max()] if len(idx) else rs[0]
k = 24
ext = np.r_[edge[-k:], edge, edge[:k]]
ker = np.hanning(2 * k + 1); ker /= ker.sum()
sm = np.convolve(ext, ker, 'same')[k:-k]
R = float(np.median(sm))
print('rayon bord min/max', sm.min().round(1), sm.max().round(1), '-> cible', round(R, 1))
# remap radial : r_src = r * edge(t) / R  (centre recale au milieu de l'image)
S = 800
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
cx = cy = (S - 1) / 2
r = np.hypot(xx - cx, yy - cy); th = np.arctan2(yy - cy, xx - cx)
ti = ((th + np.pi) / (2 * np.pi) * NT) % NT
e = np.interp(ti, np.arange(NT + 1), np.r_[sm, sm[0]])
rsrc = r * e / R
mx = (ecx + rsrc * np.cos(th)).astype(np.float32); my = (ecy + rsrc * np.sin(th)).astype(np.float32)
pm = a.copy(); pm[..., :3] *= al[..., None]
out = np.dstack([cv2.remap(pm[..., c], mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT) for c in range(4)])
oa = np.clip(out[..., 3], 0, 255)
out[..., :3] = np.where(oa[..., None] > 0, out[..., :3] / np.maximum(oa[..., None] / 255, 1e-4), 0)
out[..., 3] = oa
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save('in/knob_round.png')
# controle
b = (oa > 127).astype(np.uint8)
c2 = max(cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea)
print('apres', cv2.fitEllipse(c2)[1])

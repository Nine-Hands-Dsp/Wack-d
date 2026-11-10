"""WACK'D v2 (NINE HANDS | DSP) : genere le visuel du plugin a partir des pieces photo de tools/art.

Sorties (racine du depot) :
  background.png            1230 x 1800 px, pedale plein cadre (transparence seulement autour des jacks),
                            LED eteinte, barres eteintes, fentes des inverseurs, footswitch, voile papier sous
                            les inscriptions (les inscriptions elles-memes sont vectorielles, dessinees par l'editeur)
  led_blue.png / led_amber.png      LED allumee (source, jamais dosee)
  bars_blue.png / bars_amber.png    les 9 barres allumees (zone bars dans Layout.h)
  halo_blue.png / halo_amber.png    halos sur la facade, 10 calques empiles (LED puis barres 1 a 9), doses par Glow
  slide_left.png / slide_right.png  fente + selecteur des inverseurs
  knob_shadow/crown/marker/highlight.png  calques du potard (nh::Knob)
  Layout.h + tools/layout.json      reperes en unites du plugin (image / 2 : 615 x 900)
Usage : python3 tools/make_art.py
"""
import os, json, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, 'tools', 'art')
def art(n): return os.path.join(ART, n)
def out(n): return os.path.join(ROOT, n)

H = 1800
coque = Image.open(art('coque.png')).convert('RGBA')
k = H / coque.height
BW = coque.width * k
JL = 160.0
JS = JL / 512.0
P = 108 * JS
W = int(round(BW + 2 * P))
X0 = (W - BW) / 2
def fx(f): return X0 + f * BW
def fy(f): return f * H

L = {
    'W': W, 'H': H, 'bodyX0': X0, 'bodyW': BW,
    'knobs': [[fx(f), fy(0.134)] for f in (0.1254, 0.3746, 0.6246, 0.8754)],
    'knobR': 114.0,
    'mode': [fx(0.2202), fy(0.3453)], 'krazy': [fx(0.7816), fy(0.3453)],
    'slotW': 200.0, 'slotH': 200.0 * 192 / 556,
    'led': [fx(0.4991), fy(0.3420)], 'ledR': 80.0,
    'bars': {'x0': fx(0.4070), 'step': 24.5, 'w': 17.0, 'bottom': 778.0, 'topEdge': 712.0, 'topMid': 742.0},
    'pill': [W / 2, fy(0.595), 800.0, 76.0],
    'jacks': {'out1': fy(0.495), 'out2': fy(0.595) + 100.0, 'in': fy(0.495)},   # OUT2 descendue de 100 px (demande nov. 2026)
    'title': [W / 2, 1290.0], 'sub': [W / 2, 1395.0],
    'foot': [W / 2, fy(0.869)], 'footW': 194.0,
    'logo': [W / 2, 1718.0, 430.0],
}
INK = (36, 35, 29, 255)
PAPER = (236, 226, 204)
COL = {'blue': (120, 210, 245), 'amber': (255, 176, 70)}
FONTS = {'Medium': 'Poppins-Medium.ttf', 'SemiBold': 'Poppins-SemiBold.ttf', 'Bold': 'Poppins-Bold.ttf'}
FONT_ID = {'Medium': 0, 'SemiBold': 1, 'Bold': 2}
def font(name, size): return ImageFont.truetype(out(FONTS[name]), size)

def paste_center(dst, im, cx, cy):
    dst.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))

# ---------------------------------------------------------------------------------------------
# Inscriptions : decrites une fois, dessinees ici (pour le voile papier) et par l'editeur (vectoriel)
TEXTS, TICKS, TRIS = [], [], []
def T(s, fnt, size, x, y, align=0): TEXTS.append((s, fnt, size, x, y, align))
R = L['knobR']
for (cx, cy), n in zip(L['knobs'], ('SPEED', 'DEPTH', 'DELAY TIME', 'REGEN.')):
    for i in range(11):
        t = np.radians(-135 + 27 * i)
        r0, r1 = R + 9, R + (22 if i in (0, 5, 10) else 17)
        TICKS.append((cx + r0 * np.sin(t), cy - r0 * np.cos(t), cx + r1 * np.sin(t), cy - r1 * np.cos(t), 3.0))
    for v, t in (('0', -135), ('10', 135)):
        tr = np.radians(t); rr = R + 40
        T(v, 'Medium', 24, cx + rr * np.sin(tr), cy - rr * np.cos(tr) + 4)
    T(n, 'SemiBold', 41, cx, cy + R + 62)
for (cx, cy), (l, r), n in ((L['mode'], ('CHORUS', 'FLANGER'), 'MODE'), (L['krazy'], ('NORMAL', "WACK'D"), 'KRAZY')):
    sh = L['slotH']
    T(l, 'SemiBold', 28, cx - 14, cy - sh / 2 - 27, 2)
    T(r, 'SemiBold', 28, cx + 14, cy - sh / 2 - 27, 1)
    T(n, 'SemiBold', 38, cx, cy + sh / 2 + 37)
def tri(x, y, s=9, left=True):
    TRIS.append([(x, y), (x + s * 1.6, y - s), (x + s * 1.6, y + s)] if left else [(x + s * 1.6, y), (x, y - s), (x, y + s)])
J = L['jacks']
tri(X0 + 14, J['out1']); T('OUT1', 'SemiBold', 30, X0 + 34, J['out1'], 1)
T('INV.', 'SemiBold', 30, X0 + 34, J['out2'] - 19, 1)
tri(X0 + 14, J['out2'] + 19); T('OUT2', 'SemiBold', 30, X0 + 34, J['out2'] + 19, 1)
T('IN', 'SemiBold', 30, X0 + BW - 40, J['in'], 2); tri(X0 + BW - 30, J['in'])
T("Wack'd", 'Bold', 190, *L['title'])
T('flangerus', 'SemiBold', 72, *L['sub'])

def draw_texts(d):
    for s, f, size, x, y, a in TEXTS:
        d.text((x, y), s, font=font(f, size), fill=INK, anchor={0: 'mm', 1: 'lm', 2: 'rm'}[a])
    for x0, y0, x1, y1, w in TICKS:
        d.line((x0, y0, x1, y1), fill=INK, width=int(w))
    for p in TRIS:
        d.polygon(p, fill=INK)

# ---------------------------------------------------------------------------------------------
def bar_box(i):
    B = L['bars']; x = B['x0'] + i * B['step']
    top = B['topEdge'] + (B['topMid'] - B['topEdge']) * (1 - abs(i - 4) / 4)
    return (x, top, x + B['w'], B['bottom'])

def bars_layer(color):
    """barres : toutes eteintes (color None) ou toutes allumees"""
    SS = 4
    lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); bd = ImageDraw.Draw(lay)
    def rr(box, r, fill): bd.rounded_rectangle([v * SS for v in box], radius=r * SS, fill=fill)
    for i in range(9):
        box = bar_box(i); rad = L['bars']['w'] / 2
        rr((box[0] + 0.8, box[1] + 0.8, box[2] + 0.8, box[3] + 0.8), rad, (255, 250, 236, 120))
        rr((box[0] - 0.6, box[1] - 0.6, box[2] + 0.2, box[3] + 0.2), rad, (30, 30, 28, 170))
        rr(box, rad, (16, 20, 24, 255))
        inner = (box[0] + 1.6, box[1] + 1.6, box[2] - 1.6, box[3] - 1.6); ir = rad - 1.6
        if color:
            col = COL[color]
            rr(inner, ir, tuple(int(v * 0.55) for v in col) + (255,))
            rr((inner[0] + 1.5, inner[1] + 1.5, inner[2] - 1.5, inner[3] - 1.5), ir - 1.5,
               tuple(min(255, int(v + (255 - v) * 0.35)) for v in col) + (255,))
            hot = (inner[0] + 4.2, inner[1] + 4, inner[2] - 4.2, inner[3] - 4)
            rr(hot, max(1, ir - 4.2), (240, 250, 255, 200) if color == 'blue' else (255, 246, 228, 200))
        else:
            rr(inner, ir, (34, 40, 46, 255))
            rr((inner[0] + 1.5, inner[1] + 1.5, inner[0] + 4, inner[3] - 6), 1.2, (90, 100, 110, 90))
    return lay.resize((W, H), Image.LANCZOS)

def led_sprite(name):
    led = Image.open(art(f'led_{name}_thin.png'))
    ls = 2 * L['ledR'] / 450.0
    return led.resize((int(led.width * ls), int(led.height * ls)), Image.LANCZOS)

# ---------------------------------------------------------------------------------------------
def background():
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    img.alpha_composite(coque.resize((int(round(BW)), H), Image.LANCZOS), (int(round(X0)), 0))
    # jacks (photo du kit, quart de tour, jamais de miroir)
    jk = Image.open(art('jack.png')).convert('RGBA').crop((46, 80, 558, 188))
    jk = jk.resize((int(round(512 * JS)), int(round(108 * JS))), Image.LANCZOS)
    def grad(im, top, bot):
        a = np.asarray(im).astype(np.float32); g = np.linspace(top, bot, a.shape[0])[:, None, None]
        a[..., :3] = np.clip(a[..., :3] * g, 0, 255); return Image.fromarray(a.astype(np.uint8))
    jr = grad(jk.rotate(-90, expand=True), 1.08, 0.86)
    jl = grad(jk.rotate(90, expand=True), 1.08, 0.86)
    img.alpha_composite(jr, (int(round(X0 + BW - 2)), int(round(J['in'] - jr.height / 2))))
    for y in (J['out1'], J['out2'] + 19):          # centre du jack OUT2 aligne sur sa fleche (OUT2), pas sur le bloc INV. / OUT2
        img.alpha_composite(jl, (int(round(X0 - jl.width + 2)), int(round(y - jl.height / 2))))
    # voile papier sous les inscriptions
    tl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); draw_texts(ImageDraw.Draw(tl))
    ta = np.asarray(tl)[..., 3]
    veil = cv2.GaussianBlur(cv2.dilate(ta, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 5) / 255.0
    body_a = np.asarray(img)[..., 3] / 255.0
    v = np.zeros((H, W, 4), np.uint8); v[..., :3] = PAPER; v[..., 3] = (np.clip(veil * 0.62, 0, 1) * body_a * 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(v))
    # voile sous le logo
    lg = Image.open(art('logo_Black.png')); lw = L['logo'][2]
    lg = lg.resize((int(lw), int(lw * lg.height / lg.width)), Image.LANCZOS)
    la = np.asarray(lg)[..., 3]; pad = 30
    big = np.zeros((la.shape[0] + 2 * pad, la.shape[1] + 2 * pad), np.uint8); big[pad:-pad, pad:-pad] = la
    veil = cv2.GaussianBlur(cv2.dilate(big, np.ones((15, 15), np.uint8)).astype(np.float32), (0, 0), 7) / 255.0
    v = np.zeros(veil.shape + (4,), np.uint8); v[..., :3] = PAPER; v[..., 3] = (np.clip(veil * 0.8, 0, 1) * 255).astype(np.uint8)
    paste_center(img, Image.fromarray(v), L['logo'][0], L['logo'][1])
    # aretes des fentes des inverseurs + selecteur a gauche (l'editeur redessine la fente)
    for cx, cy in (L['mode'], L['krazy']):
        sw, sh = L['slotW'], L['slotH']
        rim = Image.new('RGBA', (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(rim)
        bx = (cx - sw / 2 - 2, cy - sh / 2 - 2, cx + sw / 2 + 2, cy + sh / 2 + 2)
        rd.rounded_rectangle([bx[0] + 1.5, bx[1] + 1.5, bx[2] + 1.5, bx[3] + 1.5], radius=6, fill=(255, 250, 238, 150))
        rd.rounded_rectangle(bx, radius=6, fill=(20, 22, 22, 230))
        img.alpha_composite(rim)
        paste_center(img, slide('left'), cx, cy)
    # LED eteinte + ombre de sa bague
    lx, ly = L['led']; ro = L['ledR'] * 190.2 / 225.0
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((lx - ro + 4, ly - ro + 4, lx + ro + 4, ly + ro + 4), fill=(0, 0, 0, 110))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    paste_center(img, led_sprite('off'), lx, ly)
    img.alpha_composite(bars_layer(None))
    # footswitch (photo) + ombre
    fs = Image.open(art('foot.png')).crop((180, 220, 1074, 1014))
    sc = L['footW'] / 813.0
    fs = fs.resize((int(fs.width * sc), int(fs.height * sc)), Image.LANCZOS)
    a = np.asarray(fs)[..., 3]
    shd = Image.new('RGBA', fs.size, (0, 0, 0, 0)); shd.putalpha(Image.fromarray((a * 0.55).astype(np.uint8)))
    paste_center(img, shd.filter(ImageFilter.GaussianBlur(7)), L['foot'][0] + 7, L['foot'][1] + 9)
    paste_center(img, fs, *L['foot'])
    return img

def slide(side):
    return Image.open(art(f'slide_{side}_b.png')).resize((int(round(L['slotW'])), int(round(L['slotH']))), Image.LANCZOS)

# ---------------------------------------------------------------------------------------------
def light_masks():
    """masques des 10 sources (LED, barres 1 a 9) en flottant"""
    ms = []
    m = np.zeros((H, W), np.float32); lx, ly = L['led']
    cv2.circle(m, (int(lx), int(ly)), int(L['ledR'] * 0.68), 1.0, -1); ms.append(m)
    for i in range(9):
        b = bar_box(i); m = np.zeros((H, W), np.float32)
        cv2.rectangle(m, (int(b[0] + 1.6), int(b[1] + 1.6)), (int(b[2] - 1.6), int(b[3] - 1.6)), 1.0, -1); ms.append(m)
    return ms

def main():
    bg = background()
    bg.save(out('background.png'), optimize=True)
    base = np.asarray(bg).astype(np.float32)
    # zone des halos (et des barres)
    Es = [cv2.GaussianBlur(m, (0, 0), 14) * 0.9 + cv2.GaussianBlur(m, (0, 0), 40) * 0.5 for m in light_masks()]
    tot = np.max(Es, axis=0) * (base[..., 3] / 255.0)
    ys, xs = np.where(tot > 1.5 / 255)
    hx0, hy0, hx1, hy1 = int(xs.min()) & ~1, int(ys.min()) & ~1, (int(xs.max()) + 2) & ~1, (int(ys.max()) + 2) & ~1
    hw, hh = hx1 - hx0, hy1 - hy0
    halo_rect = [hx0, hy0, hw, hh]
    b0 = bar_box(0); b8 = bar_box(8)
    bx0, by0 = int(np.floor(b0[0] - 2)) & ~1, int(np.floor(min(bar_box(i)[1] for i in range(9)) - 2)) & ~1
    bx1, by1 = (int(np.ceil(b8[2] + 3)) + 1) & ~1, (int(np.ceil(b0[3] + 3)) + 1) & ~1
    bars_rect = [bx0, by0, bx1 - bx0, by1 - by0]
    ba = base[..., 3:4] / 255.0
    for name, col in COL.items():
        c = np.array(col, np.float32) / 255.0
        strip = np.zeros((hh * 10, hw, 4), np.uint8)
        C = np.clip(base[..., :3] * (1 + 0.9 * c), 0, 255)
        for j, E in enumerate(Es):
            o = np.zeros((hh, hw, 4), np.float32)
            o[..., :3] = C[hy0:hy1, hx0:hx1]
            o[..., 3] = np.clip(E[hy0:hy1, hx0:hx1], 0, 1) * ba[hy0:hy1, hx0:hx1, 0] * 255
            strip[j * hh:(j + 1) * hh] = o.astype(np.uint8)
        Image.fromarray(strip).save(out(f'halo_{name}.png'), optimize=True)
        # bloom (effet glow) : lueur serree par-dessus les barres et la LED allumees, qui deborde sur les fentes et la bague ;
        # couleur de la lumiere eclaircie, moins dense au coeur pour laisser voir la source ; dose par Glow comme le halo
        bloom = np.zeros((hh * 10, hw, 4), np.uint8)
        lc = np.clip(np.array(col, np.float32) * 0.75 + 255 * 0.25, 0, 255)
        for j, m in enumerate(light_masks()):
            if j == 0:      # LED : lueur autour de la lentille, sur la bague
                m = np.zeros_like(m); cv2.circle(m, (int(L['led'][0]), int(L['led'][1])), int(L['ledR'] * 0.62), 1.0, -1)
            g = cv2.GaussianBlur(m, (0, 0), 3.0) * 1.0 + cv2.GaussianBlur(m, (0, 0), 8.0) * 1.0 + cv2.GaussianBlur(m, (0, 0), 18.0) * 0.6 + cv2.GaussianBlur(m, (0, 0), 34.0) * (0.45 if j == 0 else 0.0)
            core = cv2.GaussianBlur(m, (0, 0), 2.0)
            a = np.clip(g, 0, 1) * (1 - 0.6 * core)
            o = np.zeros((hh, hw, 4), np.float32)
            o[..., :3] = lc
            o[..., 3] = np.clip(a[hy0:hy1, hx0:hx1], 0, 1) * ba[hy0:hy1, hx0:hx1, 0] * 255
            bloom[j * hh:(j + 1) * hh] = o.astype(np.uint8)
        Image.fromarray(bloom).save(out(f'bloom_{name}.png'), optimize=True)
        bars_layer(name).crop((bx0, by0, bx1, by1)).save(out(f'bars_{name}.png'), optimize=True)
        # LED allumee : la lentille recoit sa propre lumiere (comme l'apercu valide), detouree sur la bague
        ls = led_sprite(name); lx, ly = L['led']
        reg = Image.new('RGBA', (W, H), (0, 0, 0, 0)); reg.alpha_composite(bg); paste_center(reg, ls, lx, ly)
        r = np.asarray(reg).astype(np.float32)
        r[..., :3] = np.clip(r[..., :3] * (1 + Es[0][..., None] * c[None, None, :] * 0.9), 0, 255)
        reg = Image.fromarray(r.astype(np.uint8)); paste_center(reg, ls, lx, ly)
        x0, y0 = int(round(lx - ls.width / 2)), int(round(ly - ls.height / 2))
        crop = np.asarray(reg.crop((x0, y0, x0 + ls.width, y0 + ls.height))).copy()
        crop[..., 3] = np.asarray(ls)[..., 3]
        Image.fromarray(crop).save(out(f'led_{name}.png'), optimize=True)
    for side in ('left', 'right'):
        Image.open(art(f'slide_{side}_b.png')).save(out(f'slide_{side}.png'), optimize=True)
    for n, src in (('shadow', 'shadow'), ('crown', 'crowncap'), ('marker', 'marker'), ('highlight', 'highlight')):
        Image.open(art(f'knob_{src}.png')).save(out(f'knob_{n}.png'), optimize=True)

    # ------------------------------------------------------------------ Layout.h (unites = px / 2)
    u = lambda v: v / 2.0
    ls = led_sprite('blue')
    knobS = 760 * R / 346.0
    lines = ['// genere par tools/make_art.py - ne pas modifier a la main (repere 615 x 900 = fond 1230 x 1800 px / 2)',
             '#pragma once', '#include <juce_graphics/juce_graphics.h>', 'namespace layout', '{',
             f'    constexpr float frameW = {u(W):.2f}f, frameH = {u(H):.2f}f;',
             f'    const juce::Point<float> knobPos[4] = {{ ' + ', '.join(f'{{ {u(x):.2f}f, {u(y):.2f}f }}' for x, y in L['knobs']) + ' };',
             f'    const float knobR = {u(R):.2f}f, knobS = {u(knobS):.2f}f;   // rayon du potard, cote du composant nh::Knob',
             f'    const juce::Point<float> modePos {{ {u(L["mode"][0]):.2f}f, {u(L["mode"][1]):.2f}f }}, krazyPos {{ {u(L["krazy"][0]):.2f}f, {u(L["krazy"][1]):.2f}f }};',
             f'    const float slotW = {u(L["slotW"]):.2f}f, slotH = {u(L["slotH"]):.2f}f;',
             f'    const juce::Point<float> ledPos {{ {u(L["led"][0]):.2f}f, {u(L["led"][1]):.2f}f }}; const float ledW = {u(ls.width):.2f}f, ledH = {u(ls.height):.2f}f, ledR = {u(L["ledR"]):.2f}f;',
             f'    const juce::Rectangle<float> barsRect {{ {u(bars_rect[0]):.2f}f, {u(bars_rect[1]):.2f}f, {u(bars_rect[2]):.2f}f, {u(bars_rect[3]):.2f}f }};',
             f'    const float barX0 = {u(L["bars"]["x0"]):.3f}f, barStep = {u(L["bars"]["step"]):.3f}f, barW = {u(L["bars"]["w"]):.3f}f;',
             f'    const juce::Rectangle<float> haloRect {{ {u(hx0):.2f}f, {u(hy0):.2f}f, {u(hw):.2f}f, {u(hh):.2f}f }};   // 10 calques empiles : LED, barres 1-9',
             f'    const juce::Rectangle<float> presetRect {{ {u(L["pill"][0] - L["pill"][2] / 2):.2f}f, {u(L["pill"][1] - L["pill"][3] / 2):.2f}f, {u(L["pill"][2]):.2f}f, {u(L["pill"][3]):.2f}f }};',
             '    const float presetFont = 23.0f;',
             f'    const juce::Point<float> fsPos {{ {u(L["foot"][0]):.2f}f, {u(L["foot"][1]):.2f}f }}; const float footR = {u(L["footW"]) * 0.5:.2f}f;',
             f'    const juce::Point<float> logoPos {{ {u(L["logo"][0]):.2f}f, {u(L["logo"][1]):.2f}f }}; const float logoW = {u(L["logo"][2]):.2f}f;',
             f'    const juce::Rectangle<float> bodyRect {{ {u(X0):.2f}f, 0.0f, {u(BW):.2f}f, {u(H):.2f}f }};',
             '    // inscriptions : texte, police (0 Medium, 1 SemiBold, 2 Bold), taille em, x, y, alignement (0 centre, 1 gauche, 2 droite)',
             '    struct Txt { const char* s; int font; float em, x, y; int align; };',
             '    const Txt texts[] = {']
    lines.append(',\n'.join(f'        {{ "{s}", {FONT_ID[f]}, {u(sz):.2f}f, {u(x):.2f}f, {u(y):.2f}f, {a} }}' for s, f, sz, x, y, a in TEXTS))
    lines += ['    };', '    struct Tick { float x0, y0, x1, y1, w; };', '    const Tick ticks[] = {']
    lines.append(',\n'.join(f'        {{ {u(a):.2f}f, {u(b):.2f}f, {u(c):.2f}f, {u(d):.2f}f, {u(w):.2f}f }}' for a, b, c, d, w in TICKS))
    lines += ['    };', '    struct Tri { float x0, y0, x1, y1, x2, y2; };', '    const Tri tris[] = {']
    lines.append(',\n'.join('        { ' + ', '.join(f'{u(v):.2f}f' for pt in p for v in pt) + ' }' for p in TRIS))
    lines += ['    };', '}', '']
    open(out('Layout.h'), 'w').write('\n'.join(lines))
    L.update(halo=halo_rect, barsRect=bars_rect)
    json.dump(L, open(os.path.join(ROOT, 'tools', 'layout.json'), 'w'), indent=1)
    print('ok', W, H, 'halo', halo_rect, 'bars', bars_rect)

if __name__ == '__main__':
    main()

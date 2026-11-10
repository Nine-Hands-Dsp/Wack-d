# WACK'D (NINE HANDS | DSP) - notice PDF en francais, illustree avec le rendu reel du plugin (tools/render).
# Usage : python3 tools/manual.py [<dossier des captures (tools/render)>] <fichier PDF de sortie>
#   avec captures : recompose les images et les copie dans tools/manual_assets/ ;
#   sans captures : reprend les images composees de tools/manual_assets/.
# Version lue dans CMakeLists.txt. Couverture « minimale » (gabarit fixe commun a toutes les notices NINE HANDS | DSP).
import os, re, sys, json, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = re.search(r"project\s*\(\s*\w+\s+VERSION\s+([0-9.]+)", open(os.path.join(ROOT, "CMakeLists.txt")).read()).group(1)
SHOTS = sys.argv[1] if len(sys.argv) > 2 else None
OUT = sys.argv[-1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "Wackd_Notice_FR_v" + VERSION + ".pdf")
TMP = os.path.dirname(os.path.abspath(OUT))
ASSETS = os.path.join(ROOT, "tools", "manual_assets")
LOGO_PNG = os.path.join(ASSETS, "logo_white.png")          # rendu du SVG officiel NineHandsLogoWhite.svg

for n, f in (("Pop", "Poppins-Regular"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(ROOT, f + ".ttf")))
pdfmetrics.registerFont(TTFont("Title", os.path.join(ASSETS, "BarlowCondensed-ExtraBold.ttf")))

ACC = colors.HexColor("#2A8DB8"); ACC_L = colors.HexColor("#9FE3FA")      # bleu glace de la LED
DARK = colors.HexColor("#1D1F22"); GREY = colors.HexColor("#5F646B"); LIGHT = colors.HexColor("#EAF6FB")
LAY = json.load(open(os.path.join(ROOT, "tools", "layout.json")))

NAMES = ["wk_annotated.png", "wk_onoff.png", "wk_switch.png", "wk_bar.png", "wk_glow.png", "wk_menus.png", "wk_cover.png"]
if SHOTS:
    def shot(name): return Image.open(os.path.join(SHOTS, name)).convert("RGB")
    src = shot("wk_exact_chorus.png")                  # 1230 x 1800 = coordonnees de layout.json
    K = LAY["knobs"]; R = LAY["knobR"]
    mx, my = LAY["mode"]; kx, ky = LAY["krazy"]; lx, ly = LAY["led"]
    px, py, pw, ph = LAY["pill"]; fx, fy = LAY["foot"]; J = LAY["jacks"]
    marks = [(1, K[0][0] + R * 0.8, K[0][1] - R - 16), (2, K[1][0] + R * 0.8, K[1][1] - R - 16), (3, K[2][0] + R * 0.8, K[2][1] - R - 16),
             (4, K[3][0] - R * 0.8, K[3][1] - R - 16), (5, mx, my - 110), (6, lx + 110, ly - 40), (7, kx, ky - 110),
             (8, px + pw / 2 - 20, py - 62), (9, fx + 140, fy - 40), (10, 120, J["out1"] - 66), (11, LAY["W"] - 120, J["in"] - 66)]
    ann = src.copy(); dr = ImageDraw.Draw(ann)
    fnt = ImageFont.truetype(os.path.join(ROOT, "Poppins-Bold.ttf"), 34)
    for n, x, y in marks:
        r = 30
        dr.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255), outline=(42, 141, 184), width=5)
        dr.text((x, y + 1), str(n), font=fnt, fill=(29, 31, 34), anchor="mm")
    ann.save(os.path.join(TMP, NAMES[0]))

    gap = 18
    def strip(parts, path, bg=(255, 255, 255)):
        s = Image.new("RGB", (sum(p.width for p in parts) + gap * (len(parts) - 1), max(p.height for p in parts)), bg)
        x = 0
        for p in parts: s.paste(p, (x, 0)); x += p.width + gap
        s.save(path); return path
    byp, fl = shot("wk_exact_bypass.png"), shot("wk_exact_flanger.png")
    strip([im.resize((615, 900), Image.LANCZOS) for im in (byp, src, fl)], os.path.join(TMP, NAMES[1]))
    box_sw = tuple(int(v) for v in (mx - 150, my - 100, kx + 150, my + 90))
    my_road = shot("wk_exact_myroad.png")
    col = Image.new("RGB", (box_sw[2] - box_sw[0], (box_sw[3] - box_sw[1]) * 2 + gap), (255, 255, 255))
    col.paste(src.crop(box_sw), (0, 0)); col.paste(fl.crop(box_sw), (0, box_sw[3] - box_sw[1] + gap)); col.save(os.path.join(TMP, NAMES[2]))
    box_bar = (int(px - pw / 2 - 10), int(py - ph / 2 - 10), int(px + pw / 2 + 10), int(py + ph / 2 + 10))
    bars = [src.crop(box_bar), fl.crop(box_bar)]
    col = Image.new("RGB", (bars[0].width, bars[0].height * 2 + gap), (255, 255, 255))
    for i, b in enumerate(bars): col.paste(b, (0, i * (b.height + gap)))
    col.save(os.path.join(TMP, NAMES[3]))
    box_gl = (int(lx - 170), int(ly - 120), int(lx + 170), int(ly + 200))
    strip([shot(n).crop(box_gl) for n in ("wk_glow_25.png", "wk_glow_50.png", "wk_glow_75.png", "wk_exact_chorus.png")], os.path.join(TMP, NAMES[4]))
    m1, m2 = Image.open(os.path.join(SHOTS, "wk_menu.png")).convert("RGBA"), Image.open(os.path.join(SHOTS, "wk_menu_glow.png")).convert("RGBA")
    mm_ = Image.new("RGBA", (m1.width + m2.width + gap * 2, max(m1.height, m2.height)), (255, 255, 255, 255))
    mm_.alpha_composite(m1, (0, 0)); mm_.alpha_composite(m2, (m1.width + gap * 2, 60))
    mm_.convert("RGB").save(os.path.join(TMP, NAMES[5]))

    # couverture : pedale detouree (canal alpha du fond), reflet au sol, halo bleu glace tres doux
    bg_a = Image.open(os.path.join(ROOT, "background.png")).split()[3].resize(src.size, Image.LANCZOS)
    cut = Image.new("RGBA", src.size, (0, 0, 0, 0)); cut.paste(src, (0, 0), bg_a)
    cut = cut.crop(cut.getbbox())
    cw, ch = cut.size
    pad = int(cw * 0.16)
    canvas = Image.new("RGBA", (cw + 2 * pad, int(ch * 1.30) + pad), (0, 0, 0, 255))
    yy, xx = np.mgrid[0:canvas.height, 0:canvas.width].astype(np.float64)
    gcx, gcy = canvas.width / 2, pad + ch * 0.45
    glow = np.exp(-(((xx - gcx) / (cw * 0.62)) ** 2 + ((yy - gcy) / (ch * 0.48)) ** 2)) * 30
    edge = np.clip(np.minimum.reduce([xx, canvas.width - 1 - xx, yy, canvas.height - 1 - yy]) / (pad * 0.9), 0, 1)
    glow *= edge ** 2
    halo = np.dstack([glow * 0.30, glow * 0.75, glow * 1.0, np.full_like(glow, 255)]).astype(np.uint8)
    canvas = Image.alpha_composite(canvas, Image.fromarray(halo, "RGBA"))
    refl = cut.transpose(Image.FLIP_TOP_BOTTOM)
    ra = np.array(refl).astype(np.float64)
    fade = np.clip(1 - np.arange(refl.height) / (refl.height * 0.22), 0, 1) ** 1.6 * 0.22
    ra[..., 3] *= fade[:, None]
    canvas.alpha_composite(Image.fromarray(ra.astype(np.uint8), "RGBA"), (pad, pad + ch + 6))
    canvas.alpha_composite(cut, (pad, pad))
    canvas = canvas.crop((0, 0, canvas.width, pad + int(ch * 1.20)))
    canvas.convert("RGB").save(os.path.join(TMP, NAMES[6]))
    os.makedirs(ASSETS, exist_ok=True)
    for n in NAMES: shutil.copy(os.path.join(TMP, n), os.path.join(ASSETS, n))
annotated, onoff, sw_img, bar_img, glow_img, menus_img, cover = [os.path.join(ASSETS, n) for n in NAMES]

def img(path, width):
    im = Image.open(path); h = width * im.height / im.width
    return RLImage(path, width=width, height=h)

st = {
    "h1": ParagraphStyle("h1", fontName="PopB", fontSize=20, leading=24, textColor=ACC, spaceAfter=8, spaceBefore=4, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="PopM", fontSize=13, leading=17, textColor=DARK, spaceAfter=4, spaceBefore=10, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Pop", fontSize=9.6, leading=14, textColor=DARK, spaceAfter=5),
    "tip": ParagraphStyle("tip", fontName="Pop", fontSize=9.2, leading=13, textColor=DARK, spaceAfter=4),
    "small": ParagraphStyle("small", fontName="Pop", fontSize=8.2, leading=11.5, textColor=GREY, spaceAfter=4),
    "cell": ParagraphStyle("cell", fontName="Pop", fontSize=8.6, leading=11.4, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="PopM", fontSize=8.6, leading=11.4, textColor=DARK),
}
def P(t, s="p"): return Paragraph(t, st[s])
def bullets(items, s="p"): return [P("&bull;&nbsp;&nbsp;" + i, s) for i in items]
def table(rows, widths, header=True):
    data = [[P(c, "cellb" if (header and r == 0) else "cell") for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#D3E3EA")),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header: style += [("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACC)]
    t.setStyle(TableStyle(style)); return t
W = A4[0] - 36 * mm
def side(left, right, wl):
    t = Table([[left, right]], colWidths=[wl, W - wl])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (-1, 0), (-1, 0), 0)]))
    return t

# ---------- donnees (identiques au code livre : PluginProcessor.cpp) ----------
FACTORY = [("Classic Chorus", "3,0", "5,0", "4,0", "1,0", "Chorus", "Normal", "Le chorus CF7 de référence (réglages par défaut)."),
           ("Lush Stereo Chorus", "2,2", "7,0", "7,0", "2,0", "Chorus", "Normal", "Chorus lent et ample, retard long."),
           ("Jet Flanger", "2,0", "8,0", "2,0", "7,5", "Flanger", "Normal", "Le « jet » classique, balayage profond."),
           ("Metallic Flange", "4,5", "3,0", "0,5", "9,0", "Flanger", "Normal", "Résonance aiguë, métallique."),
           ("Slow Deep Sweep", "1,0", "10", "3,0", "6,0", "Flanger", "Normal", "Balayage très lent sur toute la course."),
           ("Wack'd Vibrato", "4,0", "4,0", "3,0", "0,0", "Chorus", "Wack'd", "Vibrato pur (signal direct coupé)."),
           ("Korny Chirps", "7,0", "6,0", "2,0", "7,0", "Flanger", "Wack'd", "Gazouillis rapides et résonants."),
           ("Ring Mod Madness", "9,5", "7,0", "5,0", "3,0", "Chorus", "Wack'd", "Modulation si rapide qu'elle sonne comme un ring modulator."),
           ("My Road", "9,56", "0,16", "7,35", "1,23", "Chorus", "Wack'd", "L'intro de « My Way » (Limp Bizkit, 2000).")]

f = [NextPageTemplate("p"), Spacer(1, 1), PageBreak()]     # page 1 = couverture dessinee a positions fixes (cover_bg)

f += [P("1. Présentation", "h1"),
      P("<b>WACK'D</b> est un chorus / flanger VST3 NINE HANDS | DSP au format pédale, d'après l'<b>Ibanez CF7 Chorus/Flanger</b> "
        "(série Tone-Lok, 1999). La CF7 est une pédale numérique : une puce de retard Mitsubishi M50198 entourée de filtres, pilotée par "
        "un LFO triangle. Elle est connue pour son mode <b>KRAZY Wack'd</b>, qui coupe le signal direct et accélère fortement la modulation : "
        "vibratos, gazouillis, sons proches d'un ring modulator."),
      P("Le plugin reproduit le circuit d'après son schéma : LFO triangle à plage 1:100, retard à interpolation d'Hermite entouré de filtres "
        "anti-repliement et de reconstruction, réinjection saturée en douceur, modulation fixe ajoutée en Wack'd (R44). "
        "La version 2 redessine entièrement la pédale : coque aquarelle « Wack'd flangerus », potards, inverseurs, LED, footswitch et jacks "
        "photographiés, sérigraphie vectorielle nette à toutes les tailles, halos lumineux réglables (<b>Glow</b>) et menus du clic droit au style NINE HANDS | DSP."),
      P("2. Installation", "h1")]
f += bullets(["<b>Windows</b> : téléchargez <b>Wackd-VST3-Windows.zip</b> (bouton du dépôt GitHub Nine-Hands-Dsp/Wack-d), "
              "décompressez-le et copiez <b>Wackd.vst3</b> dans <b>C:\\Program Files\\Common Files\\VST3\\</b>.",
              "<b>macOS</b> (universel, Apple Silicon et Intel) : téléchargez <b>Wackd-VST3-macOS.zip</b>, copiez <b>Wackd.vst3</b> dans "
              "<b>~/Library/Audio/Plug-Ins/VST3/</b>, puis lancez une fois dans le Terminal : "
              "<i>xattr -cr ~/Library/Audio/Plug-Ins/VST3/Wackd.vst3</i> (retire la quarantaine du téléchargement).",
              "<b>Reaper</b> : Options &gt; Préférences &gt; Plug-ins &gt; VST &gt; <i>Re-scan</i>. Le plugin apparaît sous le nom "
              "<b>Wackd (NINE HANDS | DSP)</b>, catégorie Fx | Modulation. Pour le piloter en MIDI, la piste doit recevoir le MIDI du contrôleur."])
f.append(PageBreak())

ov = [["N°", "Commande", "Rôle"],
      ["1", "SPEED", "Vitesse du LFO."], ["2", "DEPTH", "Amplitude du balayage."],
      ["3", "DELAY TIME", "Retard de base (couleur du chorus, hauteur de la résonance du flanger)."],
      ["4", "REGEN.", "Réinjection (résonance)."],
      ["5", "MODE", "Chorus / Flanger."], ["6", "LED et jauge", "LED : effet actif (bleu glace en Chorus, jaune-orangé en Flanger). Jauge : valeur du dernier potard tourné."],
      ["7", "KRAZY", "Normal / Wack'd."],
      ["8", "Barre de presets / ligne d'état", "Au repos : flèches = preset précédent / suivant, clic sur le nom = menu. Pendant un réglage : la valeur en direct."],
      ["9", "Footswitch", "Effet / bypass."],
      ["10", "OUT1 / INV. OUT2", "Sorties (décoratives) : canal gauche et canal droit du plugin."],
      ["11", "IN", "Entrée (décorative), mono ou stéréo."]]
f += [P("3. Vue d'ensemble de l'interface", "h1"),
      side([img(annotated, 82 * mm)], table(ov, [8 * mm, 27 * mm, W - 86 * mm - 35 * mm]), 86 * mm),
      Spacer(1, 4 * mm), KeepTogether([img(onoff, W * 0.86), P("Bypass · Chorus (effet actif) · Flanger avec la ligne d'état d'un réglage.", "small")]),
      PageBreak()]

f += [P("4. Les commandes en détail", "h1"), P("Les quatre potards", "h2")]
f += bullets(["<b>SPEED</b> : vitesse du LFO triangle, potard logarithmique (plage 1:100). Normal : Chorus 0,1 → 10 Hz, Flanger 0,05 → 5 Hz. "
              "Wack'd : Chorus 0,6 → 40 Hz, Flanger 0,3 → 20 Hz. La ligne d'état affiche la vitesse en Hz.",
              "<b>DEPTH</b> : amplitude du balayage. En Wack'd, une modulation fixe s'ajoute (résistance R44 du circuit) : l'effet reste marqué même DEPTH au minimum.",
              "<b>DELAY TIME</b> : en Chorus, retard de 5 à 25 ms (plus long = chorus plus profond) ; en Flanger, retard minimum de 0,2 ms environ, "
              "balayage exponentiel jusqu'à 16 ms : vers la gauche, la résonance monte dans l'aigu.",
              "<b>REGEN.</b> : réinjection du signal retardé, jusqu'à 65 % en Chorus et 95 % en Flanger, avec saturation douce, anti-DC et aigus amortis dans la boucle.",
              "Souris : glisser verticalement (<b>Maj</b> = réglage fin), molette, <b>double-clic</b> = valeur par défaut, clic droit = MIDI Learn. "
              "Les calques du potard (jupe, chapeau, repère, ombre) tournent ensemble, avec un flou de mouvement quand il tourne vite ; "
              "la lumière reste fixe en haut à gauche."])
f += [P("Inverseurs MODE et KRAZY", "h2"),
      side(bullets(["<b>MODE</b> : sélecteur à gauche = <b>Chorus</b>, à droite = <b>Flanger</b>. La LED et la jauge passent du bleu glace au jaune-orangé.",
                    "<b>KRAZY</b> : à gauche = <b>Normal</b> (signal direct + effet, la pédale booste légèrement le volume comme l'original), "
                    "à droite = <b>Wack'd</b> : signal direct coupé (vibrato), LFO beaucoup plus rapide, modulation fixe ajoutée, aigus filtrés vers 6 kHz, "
                    "niveau égal au bypass.",
                    "Cliquez sur la fente pour basculer, ou directement sur l'inscription (CHORUS, FLANGER, NORMAL, WACK'D). La molette sur la fente marche aussi."]),
           [img(sw_img, 70 * mm), P("En haut : Chorus / Normal · En bas : Flanger", "small")], W - 74 * mm)]

f += [P("5. Footswitch, LED, jauge et Glow", "h1")]
f += bullets(["<b>Footswitch</b> : effet / bypass dès l'appui ; le bouton s'assombrit tant qu'on appuie.",
              "<b>LED</b> : allumée quand l'effet est actif, bleu glace en Chorus, jaune-orangé en Flanger, éteinte en bypass.",
              "<b>Jauge</b> (9 barres sous la LED) : s'allume de gauche (0 %) à droite (100 %) selon la valeur du dernier potard tourné "
              "(à l'ouverture : la moyenne des quatre potards). Éteinte en bypass.",
              "<b>Glow</b> (clic droit &gt; <i>Glow (halo of the lights)</i>) : règle le halo de la LED et de la jauge sur la façade, <b>25 %</b>, <b>50 %</b>, "
              "<b>75 %</b> ou <b>100 %</b> (par défaut). Seul le halo change ; la LED et les barres gardent leur éclat. Réglage commun à toutes les instances, "
              "enregistré sur l'ordinateur."])
f += [KeepTogether([Spacer(1, 1 * mm), img(glow_img, W * 0.86), P("Glow 25 %, 50 %, 75 % et 100 %.", "small")])]
f += [P("Sortie stéréo", "h2"),
      P("La vraie CF7 sort sur deux jacks : OUT1 = direct + effet, INV. OUT2 = direct − effet (effet inversé). Devant un simulateur d'ampli mono, "
        "l'effet inversé s'annule. Le plugin propose donc deux sorties (clic droit &gt; <b>Output</b>) :")]
f += bullets(["<b>Mono compatible (before amp sim)</b>, par défaut : la droite lit le retard avec un décalage de 90°, l'image reste large sans annulation. "
              "Le plugin se place devant la simulation d'ampli, comme une pédale.",
              "<b>CF7 stereo: OUT2 inverted (after amp sim)</b> : la sortie d'origine, à placer après la simulation d'ampli."])

midi = [["Commande", "Type"],
        ["Speed, Depth, Delay Time, Regen.", "Continu : 0-127 = toute la course du potard. À apprendre sur une pédale d'expression."],
        ["Mode", "Bascule : 0-63 = Chorus, 64-127 = Flanger."], ["Krazy", "Bascule : 0-63 = Normal, 64-127 = Wack'd."],
        ["Footswitch", "64-127 = effet, 0-63 = bypass."], ["Footswitch toggle", "Chaque appui (passage à 64 ou plus) inverse l'état."],
        ["Program Change", "Non apprenable : programmes 1 à 9 = presets d'usine."]]
f += [P("6. MIDI", "h1"),
      P("Chaque commande peut être pilotée par un footswitch, une pédale d'expression ou un contrôleur MIDI. <b>Aucun CC n'est assigné par défaut</b> : "
        "tout passe par le <b>MIDI Learn</b>.")]
f += bullets(["<b>Clic droit sur une commande</b> (potard, inverseur, footswitch) : le menu s'ouvre sur cette commande (son CC actuel ou <i>not assigned</i>), "
              "avec <b>MIDI Learn: &lt;commande&gt;</b> et <b>Clear MIDI: &lt;commande&gt;</b> (footswitch : ON/OFF et bascule).",
              "La ligne d'état affiche <b>MIDI LEARN</b> et le nom de la commande tant qu'elle attend ; bougez la commande MIDI : le CC est assigné et "
              "confirmé (<i>Speed = CC 11</i>). <b>Cancel MIDI learn</b> arrête l'attente.",
              "<b>Clic droit ailleurs &gt; MIDI</b> : Learn de chaque commande avec son CC actuel, <b>Clear all MIDI assignments</b>.",
              "Les assignations sont enregistrées avec le projet ; tous les paramètres sont aussi automatisables depuis le DAW."])
f += [KeepTogether([Spacer(1, 1 * mm), table(midi, [48 * mm, W - 48 * mm])])]

f += [P("7. Fenêtre et menus", "h1")]
f += bullets(["La fenêtre s'ouvre à la taille par défaut, <b>60 %</b> tant que vous n'en choisissez pas une autre, et ne peut jamais être plus petite que 60 %.",
              "Clic droit &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b> ou <b>100 %</b> (la taille actuelle est cochée, « (default) » marque la taille par défaut). "
              "On peut aussi agrandir la fenêtre par son coin, jusqu'à 150 % (proportions conservées).",
              "<b>Plugin size &gt; Default size (new windows)</b> : taille d'ouverture de toutes les nouvelles fenêtres de Wack'd (réglage commun à toutes les instances).",
              "La <b>barre de presets</b> et la <b>ligne d'état</b> partagent la même pastille, à hauteur de INV. OUT2. Au repos, elle affiche le preset en cours "
              "(ou <i>Edited</i> dès qu'un réglage s'en écarte). Dès qu'un réglage bouge (souris, molette, automation, MIDI), la ligne d'état prend sa place en fondu "
              "(<i>SPEED 70 % · 1.3 Hz</i>, <i>MODE Flanger</i>, <i>Bypass</i>…) pendant 2,5 s ; un clic sur la pastille fait revenir la barre de presets tout de suite."])
menu = [["Entrée", "Contenu"],
        ["MIDI Learn (sur une commande)", "MIDI Learn / Clear MIDI / Cancel MIDI learn"],
        ["Plugin size", "60 % · 75 % · 100 % · Default size (new windows)"],
        ["Glow (halo of the lights)", "Glow 25 % · 50 % · 75 % · 100 % (default)"],
        ["Factory presets", "les 9 presets d'usine (section 8)"],
        ["Load / Save user preset", "User 1 … 9"],
        ["Output", "Mono compatible · CF7 stereo (OUT2 inversée)"],
        ["MIDI", "Learn x8 · Cancel / Clear all MIDI assignments · rappel des plages"]]
f += [Spacer(1, 1 * mm),
      side([table(menu, [38 * mm, W - 38 * mm - 70 * mm])], [img(menus_img, 66 * mm), P("Menu du clic droit et sous-menu Glow : il s'ouvre là où vous cliquez.", "small")], W - 70 * mm)]
f += [KeepTogether([Spacer(1, 2 * mm), img(bar_img, 90 * mm), P("La pastille : barre de presets au repos, ligne d'état pendant un réglage.", "small")])]

pre = [["PC", "Preset", "SPEED", "DEPTH", "DELAY", "REGEN.", "MODE", "KRAZY", "Caractère"]] + \
      [[str(i + 1), "<b>" + n + "</b>", a, b, c, d, m, k, t] for i, (n, a, b, c, d, m, k, t) in enumerate(FACTORY)]
f += [P("8. Presets", "h1"),
      P("Les 9 presets d'usine (réglages notés de 0 à 10, comme sur la pédale) sont des programmes VST3 : ils apparaissent dans le menu des presets du DAW, "
        "sous les flèches et le nom de la barre de presets, et sous clic droit &gt; Factory presets. Clic droit &gt; <b>Save user preset</b> enregistre "
        "jusqu'à 9 presets personnels, communs à toutes les instances."),
      KeepTogether([table(pre, [9 * mm, 28 * mm, 15 * mm, 15 * mm, 15 * mm, 15 * mm, 17 * mm, 17 * mm, W - 131 * mm])]),
      P("<b>My Road</b> recrée l'intro de « My Way » (Limp Bizkit, 2000), jouée sur cette pédale : MODE Chorus, KRAZY Wack'd, Speed 95,6 % · "
        "Depth 1,6 % · Delay Time 73,5 % · Regen 12,3 %. Sur le disque, le son passe ensuite dans un écho à bande et un ampli clair.", "small")]

f += [P("9. Conseils d'utilisation", "h1")]
f += bullets(["<b>Chaîne Reaper</b> : laissez la sortie <b>Mono compatible</b> et placez Wack'd avant la simulation d'ampli (Ampire, Impulse…), comme une pédale. "
              "Pour la vraie stéréo inversée de la CF7, passez en <b>CF7 stereo</b> et placez le plugin après l'ampli.",
              "<b>7 cordes / accordages graves</b> : en Flanger, gardez REGEN. modéré sur les riffs graves ; le chorus en Normal garde le signal direct, la fondamentale "
              "reste ferme. Le mode Wack'd coupe le direct : réservez-le aux accords et aux effets.",
              "<b>Pédale d'expression</b> : apprenez SPEED sur la pédale d'expression pour passer du vibrato lent aux gazouillis Wack'd en direct ; "
              "apprenez KRAZY sur un footswitch MIDI pour basculer en Wack'd sur scène."], "tip")

tech = [["Format", "VST3 - Windows 64 bits, macOS universel (Apple Silicon + Intel) - NINE HANDS | DSP, Fx | Modulation"],
        ["Pédale d'origine", "Ibanez CF7 Chorus/Flanger (Tone-Lok, 1999)"],
        ["Canaux", "mono vers stéréo, stéréo vers stéréo"],
        ["LFO", "triangle, plage 1:100 ; Chorus 0,1 - 10 Hz, Flanger 0,05 - 5 Hz ; Wack'd 0,6 - 40 Hz / 0,3 - 20 Hz"],
        ["Retard", "interpolation d'Hermite ; Chorus 5 - 25 ms ; Flanger 0,2 - 16 ms (balayage exponentiel)"],
        ["Filtres", "anti-repliement et reconstruction 4 pôles autour du retard (6 à 13 kHz selon le mode)"],
        ["Réinjection", "jusqu'à 95 %, saturation douce, anti-DC, amortissement des aigus"],
        ["Presets", "9 usine (programmes VST3) + 9 utilisateur"],
        ["MIDI", "MIDI Learn sur les 8 commandes, aucun CC assigné par défaut, Program Change 1-9"],
        ["Fenêtre", "Plugin size 60 % / 75 % / 100 %, taille par défaut au choix, jamais moins de 60 %, jusqu'à 150 % par le coin ; Glow 25 - 100 %"],
        ["Stabilité Windows", "anti-gel v2 : le thread audio n'appelle jamais l'hôte, rafraîchissement piloté par un timer avec chien de garde"]]
f += [KeepTogether([P("10. Caractéristiques techniques", "h1"), table(tech, [30 * mm, W - 30 * mm], header=False)])]

def deco(c, doc):
    c.saveState()
    c.setFillColor(DARK); c.rect(0, A4[1] - 6 * mm, A4[0], 6 * mm, stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, A4[1] - 6.8 * mm, A4[0], 0.8 * mm, stroke=0, fill=1)
    c.setFont("Pop", 7.5); c.setFillColor(GREY)
    c.drawString(18 * mm, 10 * mm, "Wack'd (NINE HANDS | DSP) · v" + VERSION)
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                      title="WACK'D - Notice v" + VERSION, author="NINE HANDS | DSP")
# ---- Couverture « minimale » (modele 6) : gabarit fixe commun a toutes les notices (mm depuis le HAUT, logo et bandeau depuis le bas) ----
COVER_NAME, COVER_SUB, COVER_LANG = "WACK'D", "Chorus / flanger", "FRANÇAIS"
PEDAL_H, PEDAL_MAXW, PEDAL_TOP = 82 * mm, 115 * mm, 84 * mm
LANG_TOP = 18 * mm
NAME_TOP, NAME_PT = 194 * mm, 30
SUB_TOP, SUB_PT = 208 * mm, 10
LOGO_W, LOGO_BOTTOM = 38 * mm, 22 * mm
BAND_H = 3 * mm
def cover_bg(c, doc):
    c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, 0, A4[0], BAND_H, stroke=0, fill=1)
    def line(text, top, font, size, cs, col):
        w = pdfmetrics.stringWidth(text, font, size) + cs * (len(text) - 1)
        t = c.beginText((A4[0] - w) / 2, A4[1] - top - size * 0.8); t.setFont(font, size); t.setCharSpace(cs)
        t.setFillColor(col); t.textOut(text); c.drawText(t)
    line(COVER_LANG, LANG_TOP, "PopM", 8.5, 0, ACC_L)
    ci = Image.open(cover); iw, ih = ci.size
    cw = iw / 1.32; pad = int(cw * 0.16); ch = (ih - pad) / 1.2            # geometrie de wk_cover.png
    k = min(PEDAL_H / ch, PEDAL_MAXW / cw)
    dw, dh = iw * k, ih * k
    y0 = A4[1] - (PEDAL_TOP + (PEDAL_H - ch * k) / 2) + pad * k
    c.drawImage(cover, (A4[0] - dw) / 2, y0 - dh, dw, dh)
    line(COVER_NAME, NAME_TOP - NAME_PT * 0.02, "Title", NAME_PT, NAME_PT * 0.5, colors.white)
    line(COVER_SUB, SUB_TOP, "Pop", SUB_PT, 1.5, colors.HexColor("#BDC4B8"))
    lw, lh = Image.open(LOGO_PNG).size
    c.drawImage(LOGO_PNG, (A4[0] - LOGO_W) / 2, LOGO_BOTTOM, LOGO_W, LOGO_W * lh / lw, mask="auto")
    c.restoreState()
doc.addPageTemplates([PageTemplate(id="cover", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="fc")], onPage=cover_bg),
                      PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=deco)])
doc.build(f)
print(OUT)

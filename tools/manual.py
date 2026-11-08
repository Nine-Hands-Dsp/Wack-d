# WACK'D flangerus (NINE HANDS | DSP) - notice PDF bilingue (anglais puis francais), illustree.
# Usage : python3 tools/manual.py <fichier PDF de sortie>
#
# Images sources dans tools/manual_assets/ (reprises de la notice v1.7.0, rendu reel du plugin) :
#   cover_cutout.jpg (pedale detouree + reflet), annotated.jpg (capture numerotee), lfo_en/fr.png,
#   flow_en/fr.png, outputs_en/fr.png (schemas), leds.png, learn_status.png, status.png, preset_1..9.png.
# Les menus du clic droit sont redessines ici (draw_menu) avec les libelles exacts de PluginEditor.cpp :
# a mettre a jour si le menu change.
# Pas d'historique des versions dans la notice (demande de l'utilisateur).
import os, sys
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, CondPageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AS = os.path.join(ROOT, "tools", "manual_assets")
FONTS = os.path.join(AS, "fonts")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "Wackd_Manual_EN-FR.pdf")
import tempfile
TMP = tempfile.mkdtemp(prefix="wackd_manual_")   # menus dessines (fichiers temporaires)
VERSION = "1.8.2"     # = version du plugin dans CMakeLists.txt

for n, f in (("Pop", "Poppins-Regular"), ("PopL", "Poppins-Light"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold"),
             ("PopI", "Poppins-Italic"), ("Mono", "DejaVuSansMono"), ("DjV", "DejaVuSans")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f + ".ttf")))
pdfmetrics.registerFontFamily("Pop", normal="Pop", bold="PopB", italic="PopI", boldItalic="PopB")

ACC = colors.HexColor("#E8761E")          # orange du bandeau (comme la notice precedente)
DARK = colors.HexColor("#1E1E22"); GREY = colors.HexColor("#6B6B70"); LIGHT = colors.HexColor("#F6EFE8")

def A(n): return os.path.join(AS, n)

# ---------- menus du clic droit (style des menus de la notice precedente) ----------
MBG, MBORD, MTXT, MDIS, MSEP, MHI = (38, 37, 38), (70, 68, 70), (236, 233, 233), (128, 125, 126), (80, 78, 80), (232, 118, 30)
F_MENU = ImageFont.truetype(os.path.join(FONTS, "Poppins-Regular.ttf"), 26)
ROW, SEPH, PADX, PADY = 48, 18, 50, 10

def menu_img(items, width):
    """items : liste de (texte, flags) ; flags : 'sub' (fleche), 'dis' (grise), 'hi' (surligne), 'chk' (coche), 'sep'."""
    h = PADY * 2 + sum(SEPH if f == "sep" else ROW for _, f in items)
    im = Image.new("RGBA", (width, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, width - 1, h - 1), 12, fill=MBG, outline=MBORD, width=2)
    y = PADY; rows = {}
    for t, f in items:
        if f == "sep":
            d.line((24, y + SEPH // 2, width - 24, y + SEPH // 2), fill=MSEP, width=2); y += SEPH; continue
        if "hi" in f:
            d.rectangle((6, y + 2, width - 7, y + ROW - 2), fill=MHI)
        col = MDIS if "dis" in f else MTXT
        d.text((PADX + 6, y + ROW // 2), t, font=F_MENU, fill=col, anchor="lm")
        if "sub" in f:
            d.text((width - 28, y + ROW // 2), "\u203a", font=F_MENU, fill=col, anchor="mm")
        if "chk" in f:
            c = MTXT if "hi" in f else MHI
            d.line((24, y + ROW // 2, 31, y + ROW // 2 + 9), fill=c, width=4); d.line((31, y + ROW // 2 + 9, 44, y + ROW // 2 - 10), fill=c, width=4)
        rows[t] = y; y += ROW
    return im, rows

def compose(menus, gap=16):
    """menus : liste de (image, x, y) ; renvoie une image RGB sur fond blanc."""
    W = max(x + m.width for m, x, y in menus); H = max(y + m.height for m, x, y in menus)
    out = Image.new("RGB", (W, H), (255, 255, 255))
    for m, x, y in menus: out.paste(m, (x, y), m)
    return out

DASH = "\u2014"
def build_menus():
    tail = [("", "sep"), ("Factory presets", "sub"), ("Load user preset", "sub"), ("Save user preset", "sub"), ("", "sep"),
            ("Output", "sub"), ("", "sep"), ("MIDI map", "sub"), ("", "sep"), ("Wack'd flangerus v" + VERSION + " - NINE HANDS | DSP", "dis")]
    # 1) clic droit sur SPEED : Plugin size > Default size (new windows)
    m1, r1 = menu_img([("MIDI Learn: Speed (" + DASH + ")", ""), ("Clear MIDI: Speed", "dis"), ("", "sep"), ("Plugin size", "sub hi")] + tail, 600)
    m2, r2 = menu_img([("60 %  (default)", "chk"), ("75 %", ""), ("100 %", ""), ("", "sep"), ("Default size (new windows)", "sub hi")], 470)
    m3, r3 = menu_img([("60 %", "chk"), ("75 %", ""), ("100 %", "")], 230)
    y2 = r1["Plugin size"] - PADY; y3 = y2 + r2["Default size (new windows)"] - PADY
    size_menu = compose([(m1, 0, 0), (m2, 600 + 8, y2), (m3, 600 + 8 + 470 + 8, y3)])
    # 2) clic droit sur le footswitch (debut du menu)
    f1, _ = menu_img([("MIDI Learn: Footswitch (" + DASH + ")", ""), ("Clear MIDI: Footswitch", "dis"),
                      ("MIDI Learn: Footswitch toggle (" + DASH + ")", ""), ("Clear MIDI: Footswitch toggle", "dis"), ("", "sep"),
                      ("Plugin size", "sub"), ("", "sep"), ("Factory presets", "sub"), ("...", "dis")], 640)
    foot_menu = compose([(f1, 0, 0)])
    # 3) clic droit ailleurs : MIDI map
    g1, q1 = menu_img([("Plugin size", "sub")] + [x if x[0] != "MIDI map" else ("MIDI map", "sub hi") for x in tail], 600)
    learn = [("Learn: " + n + " (" + DASH + ")", "") for n in ("Speed", "Depth", "Delay Time", "Regen.", "Mode", "Krazy", "Footswitch", "Footswitch toggle")]
    g2, _ = menu_img(learn + [("", "sep"), ("Clear all MIDI assignments", ""), ("", "sep"),
                              ("Mode / Krazy: 64+ = Flanger / Wack'd", "dis"), ("Footswitch: 64+ ON / 0-63 OFF", "dis"),
                              ("Program Change 1-9  Factory presets", "dis")], 600)
    # sous-menu MIDI map : son bas aligne sur la ligne « MIDI map » (il remonte au-dessus, comme a l'ecran)
    gy = q1["MIDI map"] - PADY
    dy = max(0, g2.height - (gy + ROW + 2 * PADY))
    map_menu = compose([(g1, 0, dy), (g2, 600 + 8, max(0, gy + ROW + 2 * PADY - g2.height + dy))])
    p = {}
    for n, im in (("menu_size", size_menu), ("menu_foot", foot_menu), ("menu_map", map_menu)):
        p[n] = os.path.join(TMP, "wackd_" + n + ".png"); im.save(p[n])
    return p

MENUS = build_menus()

def img(path, width):
    im = Image.open(path); h = width * im.height / im.width
    return RLImage(path, width=width, height=h)

# ---------- styles ----------
st = {
    "h1": ParagraphStyle("h1", fontName="PopB", fontSize=18, leading=23, textColor=ACC, spaceAfter=6, spaceBefore=10, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="Pop", fontSize=12, leading=16, textColor=DARK, spaceAfter=3, spaceBefore=8, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName="PopM", fontSize=10, leading=13, textColor=DARK, spaceAfter=1, spaceBefore=6, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Pop", fontSize=9, leading=13.2, textColor=DARK, spaceAfter=4),
    "b": ParagraphStyle("b", fontName="Pop", fontSize=9, leading=13.2, textColor=DARK, spaceAfter=2.5, leftIndent=10, bulletIndent=1),
    "small": ParagraphStyle("small", fontName="Pop", fontSize=7.6, leading=10.5, textColor=GREY, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6),
    "note": ParagraphStyle("note", fontName="Pop", fontSize=8.2, leading=11.5, textColor=GREY, spaceAfter=4),
    "cell": ParagraphStyle("cell", fontName="Pop", fontSize=8.2, leading=11, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="PopM", fontSize=8.2, leading=11, textColor=DARK),
    "pset": ParagraphStyle("pset", fontName="Pop", fontSize=7.8, leading=10.5, textColor=GREY, spaceAfter=2),
    "cover": ParagraphStyle("cover", fontName="PopL", fontSize=40, leading=48, textColor=colors.white, alignment=TA_CENTER),
    "coversub": ParagraphStyle("coversub", fontName="Pop", fontSize=11, leading=16, textColor=colors.HexColor("#BDBDBD"), alignment=TA_CENTER),
    "coverlang": ParagraphStyle("coverlang", fontName="PopM", fontSize=8, leading=11, textColor=ACC),
}
def P(t, s="p"): return Paragraph(t, st[s])
def bullets(items): return [Paragraph(i, st["b"], bulletText="\u2022") for i in items]
def table(rows, widths, header=True):
    data = [[P(c, "cellb" if (header and r == 0) else "cell") for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#DCD6D0")),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4)]
    if header: style += [("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACC)]
    t.setStyle(TableStyle(style)); return t
def mono(s): return "<font name='Mono' size='8.2'>" + s + "</font>"

# ---------- presets (identiques a PluginProcessor.cpp) ----------
PRESETS = [("Classic Chorus", 3, 5, 4, 1, 0, 0), ("Lush Stereo Chorus", 2.2, 7, 7, 2, 0, 0), ("Jet Flanger", 2, 8, 2, 7.5, 1, 0),
           ("Metallic Flange", 4.5, 3, 0.5, 9, 1, 0), ("Slow Deep Sweep", 1, 10, 3, 6, 1, 0), ("Wack'd Vibrato", 4, 4, 3, 0, 0, 1),
           ("Korny Chirps", 7, 6, 2, 7, 1, 1), ("Ring Mod Madness", 9.5, 7, 5, 3, 0, 1), ("My Road", 9.56, 0.16, 7.35, 1.23, 0, 1)]

def num(v, lang):
    s = ("%g" % v)
    return s.replace(".", ",") if lang == "fr" else s

# ---------- textes ----------
T = {
"en": dict(
 lang="ENGLISH", sub="Chorus / Flanger &middot; VST3 &middot; Windows &amp; macOS", ver="User manual &middot; version " + VERSION,
 foot="Wack'd flangerus (NINE HANDS | DSP) &middot; User manual &middot; v" + VERSION,
 pres_t="1. Presentation",
 pres=["<b>Wack'd flangerus</b> is a NINE HANDS | DSP VST3 plugin modelled on the <b>Ibanez CF7 Chorus/Flanger</b> from the Tone-Lok series (1999). Like the pedal, it combines a chorus and a flanger built around a digital delay chip (Mitsubishi M50198), with four knobs, a MODE switch and the famous KRAZY switch whose Wack'd position turns the pedal into a vibrato and a ring-mod-like noise machine.",
       "The model was built from the original CF7 schematic: triangle LFO, speed pot law, the extra modulation injected by the Krazy switch, the equal-weight dry/effect mixers and the inverted second output. The interface reproduces the Wack'd flangerus artwork with real, animated controls."],
 feat_t="Main features",
 feat=["Chorus and flanger, each with a Normal and a Wack'd voice: four characters in one pedal.",
       "Speed, Depth, Delay Time and Regen as on the CF7, all automatable.",
       "<b>MIDI Learn on every control</b> (right-click on the control). No CC is assigned by default; your assignments are saved with your project.",
       "LED and 9-segment meter: ice blue in Chorus, amber in Flanger.",
       "Status line that appears only while a knob moves (or while MIDI Learn is waiting).",
       "Stereo output that stays mono-compatible by default, or the original CF7 inverted output.",
       "9 factory presets (including My Road), 9 user slots, MIDI Program Change 1 to 9.",
       "Plugin size 60 %, 75 % or 100 %, with a default size of your choice for new windows; never smaller than 60 %. Windows 11 and macOS (Intel and Apple Silicon)."],
 inst_t="2. Installation",
 inst=[("Windows 11", "Copy <b>Wackd.vst3</b> into " + mono("C:\\Program Files\\Common Files\\VST3\\") + "."),
       ("macOS", "Unzip the download, then copy <b>Wackd.vst3</b> into " + mono("~/Library/Audio/Plug-Ins/VST3/") + " (universal binary: Intel and Apple Silicon)."),
       ("Reaper", "Options &gt; Preferences &gt; Plug-ins &gt; VST: click <b>Re-scan</b> (or <i>Clear cache/re-scan</i> if the plugin was already installed). The plugin appears as <b>Wackd</b> by <b>NINE HANDS | DSP</b> in the FX browser."),
       ("Build from GitHub", "Each push to the repository starts the build in the <i>Actions</i> tab (Windows and macOS); download the artifact of the latest run.")],
 ov_t="3. Interface overview", ov_cap="The numbers refer to the table below.",
 ov=[["#", "Element", "Role"], ["1", "SPEED", "LFO rate."], ["2", "DEPTH", "Modulation width."],
     ["3", "DELAY TIME", "Base delay: chorus depth / flanger resonance."], ["4", "REGEN.", "Feedback amount."],
     ["5", "MODE", "Chorus (lever left) / Flanger (lever right)."], ["6", "KRAZY", "Normal (left) / Wack'd (right)."],
     ["7", "LED", "On when the effect is active: ice blue in Chorus, amber in Flanger."],
     ["8", "Meter", "Value of the last knob moved, from 0 % (left) to 100 % (right)."],
     ["9", "Status line", "Knob values, mode, preset and last MIDI message; MIDI Learn messages. Shown only while a knob moves."],
     ["10", "IN", "Input jack (decorative)."], ["11", "OUT1", "Left output: dry + effect."],
     ["12", "INV. OUT2", "Right output (see \"Outputs\")."], ["13", "Footswitch", "Click to switch the effect on / off (bypass)."]],
 ctl_t="4. Controls in detail",
 ctl=[("SPEED", "Sets the LFO rate. Turning clockwise speeds up the chorus or flanger. The pot is logarithmic, like the CF7's 500 k<font name='DjV'>&Omega;</font> log pot, giving a 1:100 range. Each voice has its own range (chart below). In Wack'd mode the top of the range enters the audio band, where the modulation turns into ring-mod-like tones."),
      ("DEPTH", "Sets the width of the modulation. Clockwise, the chorus becomes more detuned and the flanger sweep wider. In Wack'd mode a fixed amount of modulation is always added (resistor R44 on the CF7), so the effect stays strong even with Depth at zero."),
      ("DELAY TIME", "Sets the base delay of the digital delay line. In Chorus, clockwise means a longer delay and a deeper, more spacious chorus (5 to 25 ms). In Flanger, counter-clockwise means a shorter delay and a higher resonance: the comb filter moves up."),
      ("REGEN.", "Sets the feedback. Clockwise adds resonance: subtle thickness in Chorus, a strong metallic \"jet\" in Flanger (up to 95 %). The feedback loop has soft saturation and high-frequency damping, so high settings stay musical."),
      ("MODE", "Chooses Chorus (lever left) or Flanger (lever right). Click the switch to toggle. The LED and the meter turn ice blue in Chorus and amber in Flanger."),
      ("KRAZY", "Normal (lever left): classic chorus or flanger, dry and effect mixed at equal level. Wack'd (lever right): the dry signal is removed (pure vibrato), the LFO goes much faster, fixed modulation is added and the tone is darker. The output level matches the bypass level.")],
 knobs_note="Knobs: drag up / down (or turn the mouse wheel). Every control also answers MIDI (section 6).",
 lfo_cap="LFO speed range for each voice. Beyond about 25 Hz the modulation is heard as ring-mod-like sidebands.",
 voices_h="The four voices",
 voices=[["Voice", "Character"], ["Chorus &middot; Normal", "Bright, wide chorus. Dry + effect, rounded triangle LFO, 5-25 ms delay."],
         ["Flanger &middot; Normal", "Classic flanger with exponential sweep (0.2-16 ms) for an even jet sweep, strong Regen."],
         ["Chorus &middot; Wack'd", "Dry signal removed: vibrato, then warble and ring-mod tones as Speed rises (up to 40 Hz)."],
         ["Flanger &middot; Wack'd", "Wet-only flanger with resonance: chirps, blurbs and metallic warbles (up to 20 Hz)."]],
 flow_h="Signal flow",
 flow="The guitar is buffered, filtered, written into the digital delay line (Mitsubishi M50198 on the CF7) and read back at a time modulated by the LFO. Regen feeds part of the output back into the delay. The dry signal and the effect are then summed at equal weight.",
 fs_t="5. Footswitch, LED and outputs",
 fs=["<b>Footswitch</b>: click it to switch the effect on or off. The change is smooth (no click). In bypass the LED and the meter turn off and the status line shows BYPASS.",
     "<b>LED</b>: ice blue in Chorus, amber in Flanger, with the same brightness; the meter below it follows the last knob moved.",
     "Right-clicking the footswitch opens its MIDI Learn entries (section 6)."],
 led_cap="Left: Chorus (ice blue). Right: Flanger (amber). The switch levers move with the selected position.",
 out_h="Outputs and placement in your DAW",
 out=["The real CF7 has two outputs: OUT1 = dry + effect and OUT2 = dry &minus; effect (effect inverted). In stereo this sounds very wide. But if the two channels are summed to mono, the inverted effect cancels the normal one and only the dry signal is left. In Wack'd mode, where there is no dry signal, the sound disappears completely.",
      "Many amp simulators process the guitar in mono: they sum left and right. Choose the output in the right-click menu, <b>Output</b> (saved with your project):"],
 out_b=["<b>Mono compatible</b> (default): the right channel reads the delay a second time with the LFO shifted by 90&deg; instead of inverting it. Stereo width is kept and nothing cancels in mono. Place Wack'd <b>before</b> the amp sim, like your other pedals.",
        "<b>CF7 stereo: OUT2 inverted</b>: the original behaviour. Use it only <b>after</b> the amp sim, on a stereo track."],
 midi_t="6. MIDI",
 midi_i="Wack'd receives MIDI on any channel. In Reaper, arm the track for recording with MIDI input from your controller (or send MIDI to the track) and enable record monitoring, so the plugin receives your expression pedals and footswitches (an M-Vave Chocolate Plus for example).",
 learn_h="MIDI Learn",
 learn=["<b>No CC is assigned by default</b>: every control you want to drive from your controller is assigned with MIDI Learn.",
        "<b>Right-click a control</b> (knob, MODE or KRAZY switch, footswitch): the menu starts with <b>MIDI Learn: &lt;control&gt; (CC n)</b>, or a dash (&mdash;) when the control is not assigned. Choose it, then move a pedal or press a button on your controller: the first CC received is assigned to that control. The learning message itself does not change the sound.",
        "While waiting, the status line shows <b>MIDI LEARN: move a control for &lt;control&gt;</b>, then <b>&lt;control&gt; = CC n</b> for 2 seconds.",
        "<b>Clear MIDI: &lt;control&gt;</b> removes the assignment (available only if a CC is assigned). <b>Cancel MIDI learn</b> (or choosing the same MIDI Learn item again) stops waiting.",
        "Right-click on the footswitch offers two entries: <b>Footswitch</b> (latching: value 64 or more = on, below 64 = off) and <b>Footswitch toggle</b> (each press switches on/off, ideal for a momentary footswitch).",
        "A CC number can drive only one control: learning a CC already used by another control removes it from that control.",
        "Right-click anywhere else &gt; <b>MIDI map</b>: <b>Learn: &lt;control&gt; (CC n)</b> for every control, <b>Cancel MIDI learn</b> while waiting, and <b>Clear all MIDI assignments</b>.",
        "Assignments are <b>saved with your project</b> (and restored with it). A project saved with an earlier version that still used the former factory CC numbers opens with no assignment; a project in which you had changed an assignment keeps its assignments. CC 0 to 119 can be learnt (120 to 127 are channel mode messages)."],
 mtab=[["Control", "Type"], ["Speed", "Continuous: 0-127 = 0 to 10"], ["Depth", "Continuous: 0-127 = 0 to 10"],
       ["Delay Time", "Continuous: 0-127 = 0 to 10"], ["Regen.", "Continuous: 0-127 = 0 to 10"], ["Mode", "Switch: 0-63 Chorus, 64-127 Flanger"],
       ["Krazy", "Switch: 0-63 Normal, 64-127 Wack'd"], ["Footswitch", "Footswitch, latching: 64 and above = on, below 64 = off"],
       ["Footswitch toggle", "Footswitch, momentary: each press (value reaching 64 or more) switches on / off"],
       ["Factory presets", "Program Change 1-9: loads factory preset 1 to 9 (fixed, no learning needed)"]],
 mtab_note="All parameters can also be automated and MIDI-learned in your DAW.",
 menus_cap="Left: right-click on the SPEED knob (not assigned yet), with Plugin size &gt; Default size (new windows) open. Right: right-click on the footswitch (two learnable functions).",
 map_cap="Right-click elsewhere: MIDI map with every control and Clear all MIDI assignments.",
 lstat_cap="Status line during MIDI Learn: waiting for a CC, then confirmation (here the pedal sent CC 20).",
 win_t="7. Window and right-click menu",
 win=["The window opens at the default size, 60 % at first, and can never be made smaller than 60 %. Right-click &gt; <b>Plugin size</b> offers <b>60 %</b>, <b>75 %</b> and <b>100 %</b>; <b>(default)</b> is shown next to the current default size. You can also drag the bottom-right corner (up to 150 %); the window keeps its proportions.",
      "<b>Plugin size &gt; Default size (new windows)</b> chooses the size at which every new Wack'd window opens: the setting is shared by all instances and saved on your computer, and the open window takes that size at once.",
      "The status line under the LED shows the four knob values, then the mode, preset and last MIDI message (CC or PC). It appears only while a knob moves (mouse, automation or MIDI), stays 2.5 s and fades out. It also shows the MIDI Learn messages."],
 stat_cap="Status line (appears while a knob moves).",
 mmenu=[["Item", "Use"], ["MIDI Learn / Clear MIDI", "At the top of the menu when you right-click a control (section 6)."],
        ["Plugin size", "60 %, 75 % or 100 % (<b>(default)</b> is shown next to the default size), then Default size (new windows)."],
        ["Factory presets", "The 9 factory presets."], ["Load / Save user preset", "User slots 1 to 9."],
        ["Output", "Mono compatible (before amp sim) or CF7 stereo: OUT2 inverted (after amp sim)."],
        ["MIDI map", "Learn for every control, Cancel MIDI learn, Clear all MIDI assignments, reminder of switch values and Program Change."]],
 pre_t="8. Presets",
 pre_i="Choose a factory preset from the right-click menu (<b>Factory presets</b>), from your DAW preset menu, or with MIDI Program Change 1 to 9.",
 pdesc=["The bright, ringing chorus the CF7 is loved for. Gentle movement, wide stereo.",
        "Slower and deeper, with a longer delay and a touch of Regen: pads, clean arpeggios, ballads.",
        "The classic \"jet plane\" whoosh: low base delay, wide sweep, strong resonance.",
        "Very short delay and high Regen for a cold, metallic, almost pitched comb.",
        "Full-depth, slow flanger sweep: dramatic on chords and distorted tones.",
        "Chorus + Wack'd: the dry signal is removed, leaving a pure pitch vibrato.",
        "Flanger + Wack'd at high speed: the \"chirps and blurbs\" of late-90s nu-metal.",
        "Chorus + Wack'd near maximum speed: the LFO enters the audio range and creates ring-modulator-like tones.",
        "The intro tone of Limp Bizkit's \"My Way\" (2000), played on this pedal. On the record the guitar then went into an Echoplex and a clean amp: add a ~350 ms echo after the plugin to get closer."],
 user_h="User presets",
 user=["Right-click &gt; <b>Save user preset</b> &gt; User 1 to 9 stores the current settings; <b>Load user preset</b> recalls them. User presets are shared by every project and stored in:"],
 user_b=["Windows: " + mono("%APPDATA%\\NINE HANDS | DSP\\Wackd\\UserPresets.xml"), "macOS: " + mono("~/Library/NINE HANDS | DSP/Wackd/UserPresets.xml")],
 tips_t="9. Tips",
 tips=["<b>Reaper chain</b>: guitar track &gt; tuner &gt; drive / distortion &gt; <b>Wack'd</b> (Output: Mono compatible) &gt; amp sim (Ampire, Impulse&hellip;) &gt; reverb. Like on a real board, the chorus / flanger goes after the drive and before the amp.",
       "<b>Low-tuned 7-string</b>: on low riffs keep Depth and Regen moderate, and Delay Time below the middle, or the low end gets seasick. Jet Flanger and Slow Deep Sweep work great on heavy palm-muted chords; Wack'd Vibrato is best on clean arpeggios and single notes.",
       "Start with Classic Chorus and only move Depth: on the CF7 a little depth goes a long way.",
       "Wack'd has no dry signal: it sounds best on single notes and arpeggios, and on clean sounds.",
       "Use MIDI Learn to put Speed on an expression pedal and the footswitch on a Chocolate Plus button (Footswitch toggle for a momentary button).",
       "The status line shows the last MIDI message: handy to check that your controller reaches the plugin."],
 trb_h="Troubleshooting",
 trb=[["Problem", "Solution"], ["The effect disappears or gets thin before my amp sim", "Set Output to Mono compatible (default)."],
      ["Wack'd is silent", "You are using CF7 stereo into a mono stage. Switch to Mono compatible or place the plugin after the amp sim."],
      ["The plugin does not react to MIDI", "Check that MIDI reaches the track (input armed, monitoring on), then use MIDI Learn on the control: no CC is assigned by default."],
      ["A control reacts to the wrong pedal", "Right-click the control &gt; Clear MIDI, or MIDI map &gt; Clear all MIDI assignments, then learn again."],
      ["The window is too small", "Right-click &gt; Plugin size &gt; 75 % or 100 %, or drag the bottom-right corner. To open every new window bigger: Plugin size &gt; Default size (new windows)."]],
 spec_t="10. Specifications",
 spec=[["Format", "VST3, stereo in / stereo out (mono input accepted)"], ["Systems", "Windows 11 (x64), macOS 10.13 or later (Intel and Apple Silicon)"],
       ["Voices", "Chorus / Flanger &times; Normal / Wack'd"], ["LFO", "Triangle (rounded for chorus), 0.05 Hz to 40 Hz depending on the voice"],
       ["Delay", "Chorus 5-25 ms, flanger exponential sweep 0.2-16 ms, cubic interpolation"],
       ["Regen", "Up to 95 %, soft saturation, DC blocking, high-frequency damping"],
       ["Outputs", "Mono compatible (90&deg; second tap) or CF7 stereo (OUT2 inverted)"], ["Presets", "9 factory, 9 user, MIDI Program Change 1-9"],
       ["MIDI", "MIDI Learn on 8 functions (no CC assigned by default), saved with the project, any channel"],
       ["Window", "Plugin size 60 % (minimum), 75 %, 100 %; default size for new windows selectable; resizable by the corner"],
       ["Stability", "Windows anti-freeze v2: the interface never blocks the host"], ["Version", VERSION]],
 legal="Modelled on the Ibanez CF7 schematic. Ibanez and Tone-Lok are trademarks of their owners; Wack'd flangerus is an independent personal project by NINE HANDS | DSP."),
"fr": dict(
 lang="FRANÇAIS", sub="Chorus / Flanger &middot; VST3 &middot; Windows &amp; macOS", ver="Notice d'utilisation &middot; version " + VERSION,
 foot="Wack'd flangerus (NINE HANDS | DSP) &middot; Notice d'utilisation &middot; v" + VERSION,
 pres_t="1. Présentation",
 pres=["<b>Wack'd flangerus</b> est un plugin VST3 NINE HANDS | DSP modélisé d'après la pédale <b>Ibanez CF7 Chorus/Flanger</b> de la série Tone-Lok (1999). Comme la pédale, il réunit un chorus et un flanger construits autour d'une puce de retard numérique (Mitsubishi M50198), avec quatre potards, un switch MODE et le fameux switch KRAZY dont la position Wack'd transforme la pédale en vibrato et en machine à sons proches du ring-mod.",
       "Le modèle a été construit à partir du schéma d'origine de la CF7 : LFO triangle, loi du potard de vitesse, modulation ajoutée par le switch Krazy, mélangeurs direct/effet à poids égal et seconde sortie inversée. L'interface reprend le visuel Wack'd flangerus avec de vraies commandes animées."],
 feat_t="Points forts",
 feat=["Chorus et flanger, chacun avec une voix Normal et une voix Wack'd : quatre caractères dans une pédale.",
       "Speed, Depth, Delay Time et Regen comme sur la CF7, tous automatisables.",
       "<b>MIDI Learn sur toutes les commandes</b> (clic droit sur la commande). Aucun CC n'est assigné d'office ; tes assignations sont sauvegardées avec le projet.",
       "LED et jauge à 9 segments : bleu glace en Chorus, jaune-orangé en Flanger.",
       "Ligne d'état qui n'apparaît que lorsqu'un potard bouge (ou pendant l'attente du MIDI Learn).",
       "Sortie stéréo compatible mono par défaut, ou sortie inversée d'origine de la CF7.",
       "9 presets d'usine (dont My Road), 9 emplacements utilisateur, Program Change MIDI 1 à 9.",
       "Taille du plugin 60 %, 75 % ou 100 %, avec une taille d'ouverture au choix pour les nouvelles fenêtres ; jamais plus petite que 60 %. Windows 11 et macOS (Intel et Apple Silicon)."],
 inst_t="2. Installation",
 inst=[("Windows 11", "Copie <b>Wackd.vst3</b> dans " + mono("C:\\Program Files\\Common Files\\VST3\\") + "."),
       ("macOS", "Dézippe le téléchargement puis copie <b>Wackd.vst3</b> dans " + mono("~/Library/Audio/Plug-Ins/VST3/") + " (binaire universel : Intel et Apple Silicon)."),
       ("Reaper", "Options &gt; Preferences &gt; Plug-ins &gt; VST : clique sur <b>Re-scan</b> (ou <i>Clear cache/re-scan</i> si le plugin était déjà installé). Le plugin apparaît sous le nom <b>Wackd</b>, fabricant <b>NINE HANDS | DSP</b>, dans la liste des effets."),
       ("Compilation GitHub", "Chaque push sur le dépôt lance la compilation dans l'onglet <i>Actions</i> (Windows et macOS) ; télécharge l'artefact de la dernière exécution.")],
 ov_t="3. Vue d'ensemble de l'interface", ov_cap="Les numéros renvoient au tableau ci-dessous.",
 ov=[["#", "Élément", "Rôle"], ["1", "SPEED", "Vitesse du LFO."], ["2", "DEPTH", "Amplitude de la modulation."],
     ["3", "DELAY TIME", "Retard de base : profondeur du chorus / résonance du flanger."], ["4", "REGEN.", "Quantité de réinjection."],
     ["5", "MODE", "Chorus (levier à gauche) / Flanger (levier à droite)."], ["6", "KRAZY", "Normal (gauche) / Wack'd (droite)."],
     ["7", "LED", "Allumée quand l'effet est actif : bleu glace en Chorus, jaune-orangé en Flanger."],
     ["8", "Jauge", "Valeur du dernier potard tourné, de 0 % (gauche) à 100 % (droite)."],
     ["9", "Ligne d'état", "Valeurs des potards, mode, preset et dernier message MIDI ; messages du MIDI Learn. Visible seulement pendant qu'un potard bouge."],
     ["10", "IN", "Prise d'entrée (décorative)."], ["11", "OUT1", "Sortie gauche : direct + effet."],
     ["12", "INV. OUT2", "Sortie droite (voir « Sorties »)."], ["13", "Footswitch", "Un clic active / coupe l'effet (bypass)."]],
 ctl_t="4. Les commandes en détail",
 ctl=[("SPEED", "Règle la vitesse du LFO. Dans le sens horaire, le chorus ou le flanger accélère. Le potard est logarithmique, comme le potard log 500 k<font name='DjV'>&Omega;</font> de la CF7, soit une plage de 1 à 100. Chaque voix a sa propre plage (graphique ci-dessous). En mode Wack'd, le haut de la plage entre dans le domaine audio : la modulation se transforme en sons proches du ring-mod."),
      ("DEPTH", "Règle l'amplitude de la modulation. Dans le sens horaire, le chorus se désaccorde davantage et le balayage du flanger s'élargit. En mode Wack'd, une modulation fixe s'ajoute toujours (résistance R44 de la CF7) : l'effet reste marqué même avec Depth à zéro."),
      ("DELAY TIME", "Règle le retard de base de la ligne à retard numérique. En Chorus, sens horaire = retard plus long, chorus plus profond et spacieux (5 à 25 ms). En Flanger, sens antihoraire = retard plus court, résonance plus aiguë : le filtre en peigne monte."),
      ("REGEN.", "Règle la réinjection. Dans le sens horaire, la résonance augmente : épaississement discret en Chorus, « jet » métallique marqué en Flanger (jusqu'à 95 %). La boucle a une saturation douce et un amortissement des aigus : les réglages élevés restent musicaux."),
      ("MODE", "Choisit Chorus (levier à gauche) ou Flanger (levier à droite). Clique sur le switch pour basculer. La LED et la jauge passent au bleu glace en Chorus et au jaune-orangé en Flanger."),
      ("KRAZY", "Normal (levier à gauche) : chorus ou flanger classique, direct et effet mélangés à niveau égal. Wack'd (levier à droite) : le son direct est supprimé (vibrato pur), le LFO va beaucoup plus vite, une modulation fixe s'ajoute et le son est plus sombre. Le niveau de sortie est égal à celui du bypass.")],
 knobs_note="Potards : glisser vers le haut / le bas (ou molette de la souris). Toutes les commandes répondent aussi au MIDI (section 6).",
 lfo_cap="Plage de vitesse du LFO pour chaque voix. Au-delà d'environ 25 Hz, la modulation s'entend comme des bandes latérales de type ring-mod.",
 voices_h="Les quatre voix",
 voices=[["Voix", "Caractère"], ["Chorus &middot; Normal", "Chorus brillant et large. Direct + effet, LFO triangle arrondi, retard 5-25 ms."],
         ["Flanger &middot; Normal", "Flanger classique à balayage exponentiel (0,2-16 ms) pour un « jet » régulier, Regen puissant."],
         ["Chorus &middot; Wack'd", "Son direct supprimé : vibrato, puis ondulation et sons ring-mod quand Speed monte (jusqu'à 40 Hz)."],
         ["Flanger &middot; Wack'd", "Flanger sans direct, avec résonance : chirps, blurbs et ondulations métalliques (jusqu'à 20 Hz)."]],
 flow_h="Chemin du signal",
 flow="La guitare passe par un tampon, un filtre, puis entre dans la ligne à retard numérique (Mitsubishi M50198 sur la CF7) et en ressort avec un temps modulé par le LFO. Regen renvoie une partie de la sortie dans le retard. Le son direct et l'effet sont ensuite additionnés à poids égal.",
 fs_t="5. Footswitch, LED et sorties",
 fs=["<b>Footswitch</b> : un clic active ou coupe l'effet, sans clic audible. En bypass, la LED et la jauge s'éteignent et la ligne d'état indique BYPASS.",
     "<b>LED</b> : bleu glace en Chorus, jaune-orangé en Flanger, à la même intensité ; la jauge en dessous suit le dernier potard tourné.",
     "Le clic droit sur le footswitch ouvre ses entrées MIDI Learn (section 6)."],
 led_cap="À gauche : Chorus (bleu glace). À droite : Flanger (jaune-orangé). Les leviers des switchs suivent la position choisie.",
 out_h="Sorties et placement dans le DAW",
 out=["La vraie CF7 a deux sorties : OUT1 = direct + effet et OUT2 = direct &minus; effet (effet inversé). En stéréo, c'est très large. Mais si les deux canaux sont additionnés en mono, l'effet inversé annule l'effet normal et il ne reste que le son direct. En mode Wack'd, sans son direct, le son disparaît complètement.",
      "Beaucoup de simulateurs d'ampli traitent la guitare en mono : ils additionnent gauche et droite. Choisis la sortie dans le menu du clic droit, <b>Output</b> (enregistré avec le projet) :"],
 out_b=["<b>Mono compatible</b> (par défaut) : le canal droit relit le retard une seconde fois avec un LFO décalé de 90&deg; au lieu de l'inverser. La largeur stéréo est conservée et rien ne s'annule en mono. Place Wack'd <b>avant</b> le simulateur d'ampli, comme tes autres pédales.",
        "<b>CF7 stereo: OUT2 inverted</b> : le comportement d'origine. À utiliser uniquement <b>après</b> le simulateur d'ampli, sur une piste stéréo."],
 midi_t="6. MIDI",
 midi_i="Wack'd reçoit le MIDI sur tous les canaux. Dans Reaper, arme la piste avec l'entrée MIDI de ton contrôleur (ou envoie du MIDI à la piste) et active le monitoring, pour que le plugin reçoive tes pédales d'expression et footswitchs (un M-Vave Chocolate Plus par exemple).",
 learn_h="MIDI Learn",
 learn=["<b>Aucun CC n'est assigné d'office</b> : chaque commande à piloter depuis ton contrôleur s'assigne avec le MIDI Learn.",
        "<b>Clic droit sur une commande</b> (potard, switch MODE ou KRAZY, footswitch) : le menu commence par <b>MIDI Learn: &lt;commande&gt; (CC n)</b>, ou un tiret (&mdash;) si la commande n'est pas assignée. Choisis-le puis bouge une pédale ou appuie sur un bouton de ton contrôleur : le premier CC reçu est affecté à cette commande. Ce message d'apprentissage ne modifie pas le son.",
        "Pendant l'attente, la ligne d'état affiche <b>MIDI LEARN: move a control for &lt;commande&gt;</b>, puis <b>&lt;commande&gt; = CC n</b> pendant 2 secondes.",
        "<b>Clear MIDI: &lt;commande&gt;</b> retire l'affectation (actif seulement si un CC est affecté). <b>Cancel MIDI learn</b> (ou un nouveau choix du même MIDI Learn) annule l'attente.",
        "Le clic droit sur le footswitch propose deux entrées : <b>Footswitch</b> (à accrochage : valeur 64 ou plus = actif, moins de 64 = coupé) et <b>Footswitch toggle</b> (chaque appui active / coupe, idéal pour un footswitch momentané).",
        "Un numéro de CC ne pilote qu'une commande : apprendre un CC déjà utilisé le retire de l'autre commande.",
        "Clic droit ailleurs &gt; <b>MIDI map</b> : <b>Learn: &lt;commande&gt; (CC n)</b> pour chaque commande, <b>Cancel MIDI learn</b> pendant l'attente, et <b>Clear all MIDI assignments</b>.",
        "Les affectations sont <b>sauvegardées avec le projet</b> (et rappelées avec lui). Un projet enregistré avec une version précédente resté sur les anciens numéros de CC d'usine s'ouvre sans aucune affectation ; un projet où tu avais changé une affectation garde ses affectations. Les CC 0 à 119 peuvent être appris (120 à 127 sont des messages de mode de canal)."],
 mtab=[["Commande", "Type"], ["Speed", "Continu : 0-127 = 0 à 10"], ["Depth", "Continu : 0-127 = 0 à 10"],
       ["Delay Time", "Continu : 0-127 = 0 à 10"], ["Regen.", "Continu : 0-127 = 0 à 10"], ["Mode", "Bascule : 0-63 Chorus, 64-127 Flanger"],
       ["Krazy", "Bascule : 0-63 Normal, 64-127 Wack'd"], ["Footswitch", "Footswitch à accrochage : 64 et plus = actif, moins de 64 = coupé"],
       ["Footswitch toggle", "Footswitch momentané : chaque appui (valeur qui atteint 64 ou plus) active / coupe"],
       ["Presets d'usine", "Program Change 1-9 : charge le preset d'usine 1 à 9 (fixe, sans apprentissage)"]],
 mtab_note="Tous les paramètres sont aussi automatisables et assignables en MIDI-learn dans le DAW.",
 menus_cap="À gauche : clic droit sur le potard SPEED (pas encore assigné), avec Plugin size &gt; Default size (new windows) ouvert. À droite : clic droit sur le footswitch (deux fonctions apprenables).",
 map_cap="Clic droit ailleurs : MIDI map avec toutes les commandes et Clear all MIDI assignments.",
 lstat_cap="Ligne d'état pendant le MIDI Learn : attente d'un CC, puis confirmation (ici la pédale a envoyé le CC 20).",
 win_t="7. Fenêtre et menu du clic droit",
 win=["La fenêtre s'ouvre à la taille par défaut, 60 % au départ, et ne peut jamais être réduite sous 60 %. Clic droit &gt; <b>Plugin size</b> propose <b>60 %</b>, <b>75 %</b> et <b>100 %</b> ; <b>(default)</b> est indiqué à côté de la taille par défaut actuelle. Tu peux aussi tirer le coin inférieur droit (jusqu'à 150 %) ; la fenêtre garde ses proportions.",
      "<b>Plugin size &gt; Default size (new windows)</b> choisit la taille d'ouverture de toutes les nouvelles fenêtres de Wack'd : le réglage est commun à toutes les instances et enregistré sur l'ordinateur, et la fenêtre ouverte prend aussitôt cette taille.",
      "La ligne d'état sous la LED affiche les valeurs des quatre potards, puis le mode, le preset et le dernier message MIDI (CC ou PC). Elle n'apparaît que lorsqu'un potard bouge (souris, automation ou MIDI), reste 2,5 s puis s'efface en fondu. Elle affiche aussi les messages du MIDI Learn."],
 stat_cap="Ligne d'état (visible pendant qu'un potard bouge).",
 mmenu=[["Élément", "Rôle"], ["MIDI Learn / Clear MIDI", "En tête du menu quand tu fais un clic droit sur une commande (section 6)."],
        ["Plugin size", "60 %, 75 % ou 100 % (<b>(default)</b> est indiqué à côté de la taille par défaut), puis Default size (new windows)."],
        ["Factory presets", "Les 9 presets d'usine."], ["Load / Save user preset", "Emplacements utilisateur 1 à 9."],
        ["Output", "Mono compatible (avant le simulateur d'ampli) ou CF7 stereo : OUT2 inversée (après)."],
        ["MIDI map", "Learn pour chaque commande, Cancel MIDI learn, Clear all MIDI assignments, rappel des valeurs des switchs et du Program Change."]],
 pre_t="8. Presets",
 pre_i="Choisis un preset d'usine dans le menu du clic droit (<b>Factory presets</b>), dans le menu de presets du DAW, ou avec un Program Change MIDI de 1 à 9.",
 pdesc=["Le chorus brillant et cristallin qui a fait la réputation de la CF7. Mouvement doux, stéréo large.",
        "Plus lent et plus profond, retard plus long et un peu de Regen : nappes, arpèges en son clair, ballades.",
        "Le « avion à réaction » classique : retard de base court, grand balayage, forte résonance.",
        "Retard très court et Regen élevé : peigne froid, métallique, presque accordé.",
        "Balayage de flanger lent à pleine profondeur : spectaculaire sur les accords et les sons saturés.",
        "Chorus + Wack'd : le son direct est supprimé, il reste un vibrato pur.",
        "Flanger + Wack'd à vitesse élevée : les « chirps and blurbs » du nu-metal de la fin des années 90.",
        "Chorus + Wack'd près de la vitesse maximale : le LFO entre dans le domaine audio et produit des sons proches d'un modulateur en anneau.",
        "Le son de l'intro de « My Way » de Limp Bizkit (2000), joué sur cette pédale. Sur le disque, la guitare passait ensuite dans un Echoplex et un ampli clair : ajoute un écho d'environ 350 ms après le plugin pour t'en approcher."],
 user_h="Presets utilisateur",
 user=["Clic droit &gt; <b>Save user preset</b> &gt; User 1 à 9 enregistre les réglages actuels ; <b>Load user preset</b> les rappelle. Les presets utilisateur sont communs à tous les projets et stockés dans :"],
 user_b=["Windows : " + mono("%APPDATA%\\NINE HANDS | DSP\\Wackd\\UserPresets.xml"), "macOS : " + mono("~/Library/NINE HANDS | DSP/Wackd/UserPresets.xml")],
 tips_t="9. Conseils d'utilisation",
 tips=["<b>Chaîne Reaper</b> : piste guitare &gt; accordeur &gt; overdrive / distorsion &gt; <b>Wack'd</b> (Output : Mono compatible) &gt; simulateur d'ampli (Ampire, Impulse&hellip;) &gt; reverb. Comme sur un vrai pedalboard, le chorus / flanger se place après la saturation et avant l'ampli.",
       "<b>7 cordes accordée grave</b> : sur les riffs graves, garde Depth et Regen modérés et Delay Time sous la moitié, sinon le bas du spectre « tangue ». Jet Flanger et Slow Deep Sweep sont superbes sur des accords saturés étouffés ; Wack'd Vibrato est à réserver aux arpèges en son clair et aux notes seules.",
       "Pars de Classic Chorus et ne bouge que Depth : sur la CF7, un peu de profondeur suffit souvent.",
       "Wack'd n'a pas de son direct : il sonne mieux sur des notes seules, des arpèges et des sons clairs.",
       "Utilise le MIDI Learn pour mettre Speed sur une pédale d'expression et le footswitch sur un bouton du Chocolate Plus (Footswitch toggle pour un bouton momentané).",
       "La ligne d'état affiche le dernier message MIDI : pratique pour vérifier que ton contrôleur atteint le plugin."],
 trb_h="Dépannage",
 trb=[["Problème", "Solution"], ["L'effet disparaît ou s'amincit avant mon simulateur d'ampli", "Règle Output sur Mono compatible (par défaut)."],
      ["Wack'd ne fait aucun son", "Tu utilises CF7 stereo vers un étage mono. Passe en Mono compatible ou place le plugin après le simulateur."],
      ["Le plugin ne réagit pas au MIDI", "Vérifie que le MIDI arrive à la piste (entrée armée, monitoring actif), puis fais un MIDI Learn sur la commande : aucun CC n'est assigné d'office."],
      ["Une commande réagit à la mauvaise pédale", "Clic droit sur la commande &gt; Clear MIDI, ou MIDI map &gt; Clear all MIDI assignments, puis refais l'apprentissage."],
      ["La fenêtre est trop petite", "Clic droit &gt; Plugin size &gt; 75 % ou 100 %, ou tire le coin inférieur droit. Pour ouvrir toutes les nouvelles fenêtres plus grandes : Plugin size &gt; Default size (new windows)."]],
 spec_t="10. Caractéristiques techniques",
 spec=[["Format", "VST3, entrée stéréo / sortie stéréo (entrée mono acceptée)"], ["Systèmes", "Windows 11 (x64), macOS 10.13 ou plus récent (Intel et Apple Silicon)"],
       ["Voix", "Chorus / Flanger &times; Normal / Wack'd"], ["LFO", "Triangle (arrondi pour le chorus), de 0,05 Hz à 40 Hz selon la voix"],
       ["Retard", "Chorus 5-25 ms, flanger à balayage exponentiel 0,2-16 ms, interpolation cubique"],
       ["Regen", "Jusqu'à 95 %, saturation douce, anti-DC, amortissement des aigus"],
       ["Sorties", "Mono compatible (seconde lecture à 90&deg;) ou CF7 stereo (OUT2 inversée)"], ["Presets", "9 usine, 9 utilisateur, Program Change MIDI 1-9"],
       ["MIDI", "MIDI Learn sur 8 fonctions (aucun CC assigné d'office), sauvegardé avec le projet, tous canaux"],
       ["Fenêtre", "Plugin size 60 % (minimum), 75 %, 100 % ; taille d'ouverture des nouvelles fenêtres au choix ; redimensionnable par le coin"],
       ["Stabilité", "Anti-gel v2 de la fenêtre sous Windows : l'interface ne bloque jamais l'hôte"], ["Version", VERSION]],
 legal="Modélisé d'après le schéma de l'Ibanez CF7. Ibanez et Tone-Lok sont des marques de leurs propriétaires ; Wack'd flangerus est un projet personnel indépendant de NINE HANDS | DSP."),
}

W = A4[0] - 36 * mm
CUR = {"foot": ""}

def section(lang):
    t = T[lang]; f = []
    f.append(NextPageTemplate("p"))
    f.append(Spacer(1, 4 * mm)); f.append(P(t["lang"], "coverlang")); f.append(Spacer(1, 6 * mm))
    f.append(img(A("cover_cutout.jpg"), W * 0.40)); f.append(Spacer(1, 4 * mm))
    f.append(P("W A C K ' D", "cover")); f.append(Spacer(1, 2 * mm))
    f.append(P(t["sub"], "coversub")); f.append(P(t["ver"], "coversub")); f.append(Spacer(1, 7 * mm))
    f.append(img(A("logo_studio_wiga_blanc.png"), 44 * mm))
    f.append(SetFoot(t["foot"]))
    f.append(PageBreak())
    # 1-2
    f.append(P(t["pres_t"], "h1")); f += [P(x) for x in t["pres"]]
    f.append(P(t["feat_t"], "h2")); f += bullets(t["feat"])
    f.append(P(t["inst_t"], "h1"))
    for h, x in t["inst"]: f.append(P(h, "h2")); f.append(P(x))
    f.append(PageBreak())
    # 3
    f.append(P(t["ov_t"], "h1")); f.append(img(A("annotated.jpg"), 92 * mm)); f.append(P(t["ov_cap"], "small"))
    f.append(table(t["ov"], [10 * mm, 34 * mm, W - 44 * mm]))
    f.append(PageBreak())
    # 4
    f.append(P(t["ctl_t"], "h1"))
    for h, x in t["ctl"]: f.append(P(h, "h3")); f.append(P(x))
    f.append(P(t["knobs_note"], "note"))
    f.append(KeepTogether([img(A("lfo_" + lang + ".png"), W * 0.88), P(t["lfo_cap"], "small")]))
    f.append(KeepTogether([P(t["voices_h"], "h2"), table(t["voices"], [36 * mm, W - 36 * mm])]))
    f.append(P(t["flow_h"], "h2")); f.append(P(t["flow"]))
    f.append(img(A("flow_" + lang + ".png"), W * 0.92))
    # 5
    f.append(CondPageBreak(90 * mm))
    f.append(P(t["fs_t"], "h1")); f += bullets(t["fs"])
    f.append(KeepTogether([Spacer(1, 2 * mm), img(A("leds.png"), W * 0.78), P(t["led_cap"], "small")]))
    f.append(P(t["out_h"], "h2")); f += [P(x) for x in t["out"]]; f += bullets(t["out_b"])
    f.append(Spacer(1, 2 * mm)); f.append(img(A("outputs_" + lang + ".png"), W * 0.85))
    f.append(CondPageBreak(120 * mm))
    # 6
    f.append(P(t["midi_t"], "h1")); f.append(P(t["midi_i"]))
    f.append(P(t["learn_h"], "h2")); f += bullets(t["learn"])
    f.append(Spacer(1, 2 * mm))
    f.append(KeepTogether([table(t["mtab"], [40 * mm, W - 40 * mm]), P(t["mtab_note"], "note")]))
    mt = Table([[img(MENUS["menu_size"], W * 0.66), img(MENUS["menu_foot"], W * 0.32)]], colWidths=[W * 0.67, W * 0.33])
    mt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    f.append(KeepTogether([Spacer(1, 3 * mm), mt, P(t["menus_cap"], "small")]))
    f.append(KeepTogether([img(MENUS["menu_map"], W * 0.62), P(t["map_cap"], "small")]))
    f.append(KeepTogether([img(A("learn_status.png"), W * 0.55), P(t["lstat_cap"], "small")]))
    # 7
    f.append(CondPageBreak(110 * mm))
    f.append(P(t["win_t"], "h1")); f += [P(x) for x in t["win"]]
    f.append(KeepTogether([img(A("status.png"), W * 0.5), P(t["stat_cap"], "small")]))
    f.append(KeepTogether([table(t["mmenu"], [42 * mm, W - 42 * mm])]))
    f.append(PageBreak())
    # 8
    f.append(P(t["pre_t"], "h1")); f.append(P(t["pre_i"]))
    for i, (n, sp, de, dl, rg, mo, kr) in enumerate(PRESETS):
        line = ("Flanger" if mo else "Chorus") + " &middot; " + ("Wack'd" if kr else "Normal") + \
               " &middot; Speed %s &middot; Depth %s &middot; Delay Time %s &middot; Regen %s" % tuple(num(v, lang) for v in (sp, de, dl, rg))
        f.append(KeepTogether([P("%d. %s" % (i + 1, n), "h3"), P(t["pdesc"][i]), P(line, "pset"), img(A("preset_%d.png" % (i + 1)), W * 0.62), Spacer(1, 2 * mm)]))
    f.append(KeepTogether([P(t["user_h"], "h2")] + [P(x) for x in t["user"]] + bullets(t["user_b"])))
    f.append(PageBreak())
    # 9-10
    f.append(P(t["tips_t"], "h1")); f += bullets(t["tips"])
    f.append(KeepTogether([P(t["trb_h"], "h2"), table(t["trb"], [52 * mm, W - 52 * mm])]))
    f.append(KeepTogether([P(t["spec_t"], "h1"), table(t["spec"], [30 * mm, W - 30 * mm], header=False), Spacer(1, 3 * mm), P(t["legal"], "note")]))
    f.append(PageBreak())
    return f

from reportlab.platypus.flowables import Flowable
class SetFoot(Flowable):
    def __init__(self, s): Flowable.__init__(self); self.s = s
    def wrap(self, *a): return (0, 0)
    def draw(self): CUR["foot"] = self.s

def deco(c, doc):
    c.saveState()
    c.setFillColor(ACC); c.rect(0, A4[1] - 3 * mm, A4[0], 3 * mm, stroke=0, fill=1)
    c.setFont("Pop", 7.5); c.setFillColor(GREY)
    c.drawString(18 * mm, 10 * mm, CUR["foot"].replace("&middot;", "\u00b7"))
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    c.restoreState()

def cover_bg(c, doc):
    c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, A4[1] - 3 * mm, A4[0], 3 * mm, stroke=0, fill=1); c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                      title="Wack'd flangerus - User manual / Notice v" + VERSION, author="NINE HANDS | DSP")
doc.addPageTemplates([PageTemplate(id="cover", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="fc")], onPage=cover_bg),
                      PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=deco)])
en = section("en"); fr = section("fr")
en[-1:] = [NextPageTemplate("cover"), PageBreak()]
doc.build(en + fr[:-1])
print(OUT)

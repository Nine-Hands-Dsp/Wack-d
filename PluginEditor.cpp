#include "PluginEditor.h"
#include "BinaryData.h"
#include "WigaWindowSize.h"
#include "NineHandsGlow.h"

using namespace juce;

namespace
{
    const Colour ink (0xff24231d);                  // encre de la serigraphie (comme « Wack'd »)
    const Colour pillOut (0xff141414), pillRim (0xff969696), pillFace (0xff0a0a0b), pillInk (0xffeef1f5), pillArrow (0xff969696);
    const Colour menuAccent (0xff78d2f5);           // pastille des en-tetes de menu (bleu glace de la LED)
    constexpr float arrowW = 34.0f;
    const char* knobIds[4]   = { "speed", "depth", "delay", "regen" };
    const char* knobNames[4] = { "Speed", "Depth", "Delay Time", "Regen." };
}

static Image png (const void* d, int n) { return ImageCache::getFromMemory (d, n); }

//==============================================================================
WackdAudioProcessorEditor::WackdAudioProcessorEditor (WackdAudioProcessor& p)
    : AudioProcessorEditor (p), proc (p)
{
    background = png (BinaryData::background_png, BinaryData::background_pngSize);
    ledImg[0]   = png (BinaryData::led_blue_png,   BinaryData::led_blue_pngSize);
    ledImg[1]   = png (BinaryData::led_amber_png,  BinaryData::led_amber_pngSize);
    barsImg[0]  = png (BinaryData::bars_blue_png,  BinaryData::bars_blue_pngSize);
    barsImg[1]  = png (BinaryData::bars_amber_png, BinaryData::bars_amber_pngSize);
    haloImg[0]  = png (BinaryData::halo_blue_png,  BinaryData::halo_blue_pngSize);
    haloImg[1]  = png (BinaryData::halo_amber_png, BinaryData::halo_amber_pngSize);
    bloomImg[0] = png (BinaryData::bloom_blue_png,  BinaryData::bloom_blue_pngSize);
    bloomImg[1] = png (BinaryData::bloom_amber_png, BinaryData::bloom_amber_pngSize);
    slideImg[0] = png (BinaryData::slide_left_png,  BinaryData::slide_left_pngSize);
    slideImg[1] = png (BinaryData::slide_right_png, BinaryData::slide_right_pngSize);

    regularFace = Typeface::createSystemTypefaceFor (BinaryData::PoppinsRegular_ttf,  BinaryData::PoppinsRegular_ttfSize);
    mediumFace  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf,   BinaryData::PoppinsMedium_ttfSize);
    semiFace    = Typeface::createSystemTypefaceFor (BinaryData::PoppinsSemiBold_ttf, BinaryData::PoppinsSemiBold_ttfSize);
    boldFace    = Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf,     BinaryData::PoppinsBold_ttfSize);
    menuLnf.f = { regularFace, mediumFace, boldFace };
    if (auto xml = XmlDocument::parse (String::fromUTF8 (BinaryData::NineHandsLogoBlack_svg, BinaryData::NineHandsLogoBlack_svgSize)))
        logo = Drawable::createFromSVG (*xml);
    buildPrint();
    glow = (float) NineHandsGlow::percent ("Wackd") / 100.0f;

    // potards : calques nh::Knob (lumiere en haut a gauche a 45 deg, ombre a 45 deg vers le bas a droite)
    nh::Knob::Layers L;
    L.shadow    = png (BinaryData::knob_shadow_png,    BinaryData::knob_shadow_pngSize);
    L.crown     = png (BinaryData::knob_crown_png,     BinaryData::knob_crown_pngSize);
    L.marker    = png (BinaryData::knob_marker_png,    BinaryData::knob_marker_pngSize);
    L.highlight = png (BinaryData::knob_highlight_png, BinaryData::knob_highlight_pngSize);
    for (int i = 0; i < 4; ++i)
    {
        nh::Knob::Style ks;
        ks.shadowOffset = { layout::knobShadowOffset, layout::knobShadowOffset };      // meme decalage qu'avant la marge (45 deg bas droite)
        knobs[i] = std::make_unique<nh::Knob> (*proc.apvts.getParameter (knobIds[i]), L, ks);
        knobs[i]->onRightClick = [this, i] (const MouseEvent&) { showContextMenu (i); };
        knobs[i]->onUserChange = [this, i] { meterKnob = i; };
        addAndMakeVisible (*knobs[i]);
    }

    // taille : 493 px par defaut (« 60 % ») = taille minimale, proportions bloquees
    const double aspect = (double) baseW / (double) baseH;
    setResizable (true, true);
    setResizeLimits (roundToInt (heightDefault * aspect), heightDefault, roundToInt (heightMax * aspect), heightMax);
    getConstrainer()->setFixedAspectRatio (aspect);
    setOpaque (true);
    const int h0 = sizeHeight (WigaWindowSize::defaultIndex ("Wackd", numSizes));
    setSize (roundToInt (h0 * aspect), h0);
    rebuildCaches();

    for (int i = 0; i < 4; ++i) lastKnob[i] = value (knobIds[i]);
    lastMode = flag ("mode"); lastKrazy = flag ("krazy"); lastOn = flag ("active"); lastStereo = flag ("stereo");
    for (auto& b : dBars) b = -1.0f;
    snapshotPreset();
    lastPreset = proc.currentPreset.load();
    settleForCapture();
    startTimerHz (30);
}

WackdAudioProcessorEditor::~WackdAudioProcessorEditor()
{
    PopupMenu::dismissAllActiveMenus();
    stopTimer();
}

//==============================================================================
// Anti-gel v2 (NINE HANDS | DSP) : moteur logiciel sous Windows, caches refaits par le timer seulement,
// chien de garde des redessins, aucun appel a l'hote depuis le thread audio (voir PluginProcessor).
void WackdAudioProcessorEditor::useSoftwareRenderer()
{
    auto* peer = getPeer();
    if (peer != lastPeer) { lastPeer = peer; repaint(); }
   #if JUCE_WINDOWS
    if (peer != nullptr)
    {
        int sw = peer->getAvailableRenderingEngines().indexOf ("Software Renderer");
        if (sw < 0) sw = 0;
        if (peer->getCurrentRenderingEngine() != sw)
            peer->setCurrentRenderingEngine (sw);
    }
   #endif
}

void WackdAudioProcessorEditor::parentHierarchyChanged() { useSoftwareRenderer(); }
void WackdAudioProcessorEditor::visibilityChanged()      { useSoftwareRenderer(); if (isShowing()) repaint(); }

float WackdAudioProcessorEditor::physicalScale() const
{
    if (forcedScale > 0.0f) return forcedScale;
    return jlimit (1.0f, 4.0f, (float) Component::getApproximateScaleFactorForComponent (this));
}

void WackdAudioProcessorEditor::askRepaint (Rectangle<float> u)
{
    if (repaintAskedMs <= 0.0) repaintAskedMs = Time::getMillisecondCounterHiRes();
    repaint (u.transformedBy (AffineTransform::scale (k())).getSmallestIntegerContainer().expanded (2));
}

void WackdAudioProcessorEditor::resized()
{
    // jamais de setSize ici ; les caches attendent que la taille se stabilise (timer)
    const float kk = k();
    for (int i = 0; i < 4; ++i)
        knobs[i]->setBounds (Rectangle<float> (layout::knobS, layout::knobS).withCentre (layout::knobPos[i])
                                 .transformedBy (AffineTransform::scale (kk)).getSmallestIntegerContainer());
    resizeSettle = 4;
}

int WackdAudioProcessorEditor::sizeHeight (int idx)
{
    const int h[numSizes] = { heightDefault, 719, 958 };
    return h[jlimit (0, numSizes - 1, idx)];
}

void WackdAudioProcessorEditor::setWindowHeight (int h)
{
    h = jlimit (heightDefault, heightMax, h);
    setSize (roundToInt ((double) h * baseW / baseH), h);
}

void WackdAudioProcessorEditor::rebuildCaches (float sc)
{
    if (sc <= 0.0f) sc = physicalScale();
    const int w = getWidth(), h = getHeight();
    if (w <= 0 || h <= 0) return;
    if (w == cacheW && h == cacheH && std::abs (sc - cacheScale) < 0.01f && bgScaled.isValid()) return;
    cacheW = w; cacheH = h; cacheScale = sc;
    const int pw = roundToInt ((float) w * sc), ph = roundToInt ((float) h * sc);
    bgScaled = (pw >= background.getWidth()) ? background : background.rescaled (pw, ph, Graphics::highResamplingQuality);
    repaint();
}

void WackdAudioProcessorEditor::forceRenderScale (float sc)
{
    forcedScale = sc;
    resized();
    resizeSettle = 0;
    cacheW = 0;
    rebuildCaches (sc);
    for (auto& kn : knobs) kn->forceRenderScale (sc);
}

void WackdAudioProcessorEditor::setGlowPercent (int pc)
{
    NineHandsGlow::setPercent ("Wackd", pc);
    glow = (float) jlimit (25, 100, pc) / 100.0f;
    repaint();
}

void WackdAudioProcessorEditor::settleForCapture()
{
    ledLevel = flag ("active") ? 1.0f : 0.0f;
    amber = flag ("mode") ? 1.0f : 0.0f;
    updateMeter();
    meterLevel = jlimit (0.0f, 1.0f, meterLevel);
    float level = 0.0f;
    if (meterKnob >= 0) level = value (knobIds[meterKnob]) / 10.0f;
    else for (auto* id : knobIds) level += value (id) / 40.0f;
    meterLevel = ledLevel > 0.5f ? jlimit (0.0f, 1.0f, level) : 0.0f;
    for (int i = 0; i < numBars; ++i) barFill[i] = jlimit (0.0f, 1.0f, meterLevel * (float) numBars - (float) i);
    presetText = presetLine();
    statusAlpha = Time::getMillisecondCounterHiRes() < statusUntil ? 1.0f : 0.0f;
    repaint();
}

//==============================================================================
// Serigraphie vectorielle (Layout.h) : construite une fois en chemins (unites du plugin)
//==============================================================================
void WackdAudioProcessorEditor::buildPrint()
{
    printPath.clear();
    auto faceOf = [this] (int f) { return f == 2 ? boldFace : (f == 1 ? semiFace : mediumFace); };
    int lab = 0;
    for (const auto& t : layout::texts)
    {
        const Font font (FontOptions (faceOf (t.font)).withPointHeight (t.em));
        const String s (t.s);
        const float w = GlyphArrangement::getStringWidth (font, s);
        const float base = (font.getAscent() - font.getDescent()) * 0.5f;
        GlyphArrangement ga;
        ga.addLineOfText (font, s, t.align == 0 ? -w * 0.5f : (t.align == 2 ? -w : 0.0f), base);
        Path p; ga.createPath (p);
        p.applyTransform (AffineTransform::translation (t.x, t.y));
        printPath.addPath (p);
        if (s == "CHORUS" || s == "FLANGER" || s == "NORMAL" || s == "WACK'D")
            if (lab < 4) labelHit[lab++] = p.getBounds().expanded (6.0f, 6.0f);
    }
    for (const auto& tk : layout::ticks)
    {
        Path seg; seg.startNewSubPath (tk.x0, tk.y0); seg.lineTo (tk.x1, tk.y1);
        Path stroked;
        PathStrokeType (tk.w, PathStrokeType::curved, PathStrokeType::butt).createStrokedPath (stroked, seg);
        printPath.addPath (stroked);
    }
    for (const auto& tr : layout::tris)
    {
        Path p; p.addTriangle (tr.x0, tr.y0, tr.x1, tr.y1, tr.x2, tr.y2);
        printPath.addPath (p);
    }
}

//==============================================================================
String WackdAudioProcessorEditor::knobText (int i) const
{
    const float v = value (knobIds[i]);
    String s = String (knobNames[i]).toUpperCase() + "  " + String (roundToInt (v * 10.0f)) + " %";
    if (i == 0)
    {
        // meme loi que le moteur (triangle, plage 1:100 en Normal)
        const bool fl = flag ("mode"), wk = flag ("krazy");
        const double sp = v / 10.0;
        const double hz = ! wk ? (fl ? 0.05 : 0.10) * std::pow (100.0, sp) : (fl ? 0.30 : 0.60) * std::pow (66.7, sp);
        s << String (CharPointer_UTF8 ("  \xc2\xb7  ")) << String (hz, hz < 1.0 ? 2 : 1) << " Hz";
    }
    return s;
}

void WackdAudioProcessorEditor::snapshotPreset()
{
    const char* ids[6] = { "speed", "depth", "delay", "regen", "mode", "krazy" };
    for (int i = 0; i < 6; ++i) presetSnap[i] = value (ids[i]);
}

bool WackdAudioProcessorEditor::editedSincePreset() const
{
    const char* ids[6] = { "speed", "depth", "delay", "regen", "mode", "krazy" };
    const int cp = proc.currentPreset.load();
    if (cp >= 0 && cp < WackdAudioProcessor::getNumFactoryPresets())
    {
        // preset d'usine : compare aux valeurs du preset (quelle que soit la facon dont il a ete charge)
        const auto& fp = WackdAudioProcessor::getFactoryPreset (cp);
        const float ref[6] = { fp.speed, fp.depth, fp.delay, fp.regen, (float) fp.mode, (float) fp.krazy };
        for (int i = 0; i < 6; ++i)
            if (std::abs (value (ids[i]) - ref[i]) > 0.006f) return true;
        return false;
    }
    for (int i = 0; i < 6; ++i)
        if (std::abs (value (ids[i]) - presetSnap[i]) > 0.006f) return true;
    return false;
}

String WackdAudioProcessorEditor::presetLine() const
{
    const int cp = proc.currentPreset.load();
    if (cp < 0 || editedSincePreset()) return "Edited";
    if (cp < WackdAudioProcessor::getNumFactoryPresets())
        return String (cp + 1) + "  " + WackdAudioProcessor::getFactoryPreset (cp).name;
    if (cp > 100) return "User " + String (cp - 100);
    return "Edited";
}

void WackdAudioProcessorEditor::flash (const String& t, double seconds)
{
    statusText = t;
    statusUntil = Time::getMillisecondCounterHiRes() + seconds * 1000.0;
}

void WackdAudioProcessorEditor::setParam (const String& id, float plain)
{
    if (auto* p = proc.apvts.getParameter (id))
    {
        p->beginChangeGesture();
        p->setValueNotifyingHost (p->convertTo0to1 (plain));
        p->endChangeGesture();
    }
}

void WackdAudioProcessorEditor::loadFactory (int i)
{
    proc.applyFactoryPreset (i);
    proc.updateHostDisplay (AudioProcessor::ChangeDetails().withProgramChanged (true));
    snapshotPreset();
    lastPreset = proc.currentPreset.load();
    for (int j = 0; j < 4; ++j) lastKnob[j] = value (knobIds[j]);
    lastMode = flag ("mode"); lastKrazy = flag ("krazy");
}

void WackdAudioProcessorEditor::loadUser (int slot)
{
    if (proc.loadUserPreset (slot))
    {
        snapshotPreset();
        lastPreset = proc.currentPreset.load();
        for (int j = 0; j < 4; ++j) lastKnob[j] = value (knobIds[j]);
        lastMode = flag ("mode"); lastKrazy = flag ("krazy");
    }
}

void WackdAudioProcessorEditor::stepPreset (int delta)
{
    const int n = WackdAudioProcessor::getNumFactoryPresets();
    int cp = proc.currentPreset.load();
    if (cp < 0 || cp >= n) cp = delta > 0 ? -1 : 0;
    loadFactory ((cp + delta + n) % n);
}

//==============================================================================
// Jauge sous la LED : de gauche (0 %) a droite (100 %) = valeur du dernier potard tourne
// (au demarrage : moyenne des 4 potards) ; eteinte en bypass.
void WackdAudioProcessorEditor::updateMeter()
{
    float level = 0.0f;
    if (meterKnob >= 0) level = value (knobIds[meterKnob]) / 10.0f;
    else for (auto* id : knobIds) level += value (id) / 40.0f;
    const float target = flag ("active") ? jlimit (0.0f, 1.0f, level) : 0.0f;
    meterLevel += (target - meterLevel) * 0.35f;
    if (std::abs (target - meterLevel) < 0.002f) meterLevel = target;
    for (int i = 0; i < numBars; ++i)
        barFill[i] = jlimit (0.0f, 1.0f, meterLevel * (float) numBars - (float) i);
}

void WackdAudioProcessorEditor::timerCallback()
{
    const double now = Time::getMillisecondCounterHiRes();
    if (getPeer() != lastPeer || now - lastRendererCheckMs > 1000.0) { lastRendererCheckMs = now; useSoftwareRenderer(); }
    if (resizeSettle > 0 && --resizeSettle == 0) rebuildCaches();
    else if (resizeSettle == 0 && now - lastScaleCheckMs > 250.0)
    {
        lastScaleCheckMs = now;
        const float sc = physicalScale();
        if (std::abs (sc - cacheScale) > 0.01f) rebuildCaches (sc);
    }
    if (repaintAskedMs > 0.0 && isShowing() && now - repaintAskedMs > 1500.0 && lastPaintMs < repaintAskedMs)
    {
        repaintAskedMs = 0.0; lastPeer = nullptr;
        useSoftwareRenderer(); repaint();
    }
    if (now - lastGlowCheckMs > 3000.0)
    {
        lastGlowCheckMs = now;
        glow = (float) NineHandsGlow::percent ("Wackd") / 100.0f;          // reglage commun a toutes les fenetres
    }

    // ---- reglages qui changent (souris, automation, MIDI) -> ligne d'etat ; chargement de preset -> barre seulement
    const int cp = proc.currentPreset.load();
    const bool presetLoaded = cp != lastPreset;
    if (presetLoaded) { lastPreset = cp; snapshotPreset(); }
    const bool mode = flag ("mode"), krazy = flag ("krazy"), on = flag ("active"), stereo = flag ("stereo");
    for (int i = 0; i < 4; ++i)
    {
        const float v = value (knobIds[i]);
        if (std::abs (v - lastKnob[i]) > 1.0e-4f)
        {
            lastKnob[i] = v;
            if (! presetLoaded) { meterKnob = i; flash (knobText (i)); }
        }
    }
    if (! presetLoaded)
    {
        if (mode != lastMode)   flash (String ("MODE  ") + (mode ? "Flanger" : "Chorus"));
        if (krazy != lastKrazy) flash (String ("KRAZY  ") + (krazy ? "Wack'd" : "Normal"));
    }
    if (on != lastOn)         flash (on ? "Effect on" : "Bypass", 1.6);
    if (stereo != lastStereo) flash (stereo ? "Output  CF7 stereo (INV)" : "Output  Mono compatible");
    lastMode = mode; lastKrazy = krazy; lastOn = on; lastStereo = stereo;

    if (const int lt = proc.learnTarget.load(); lt >= 0)
        flash ("MIDI LEARN  " + String (WackdAudioProcessor::learnDef (lt).name), 0.25);
    if (const int learned = proc.lastLearned.exchange (-1); learned >= 0)
        flash (String (WackdAudioProcessor::learnDef (learned).name) + " = CC " + String (proc.ccMap[learned].load()));

    const float st = now < statusUntil ? 1.0f : 0.0f;
    statusAlpha += (st - statusAlpha) * (st > statusAlpha ? 0.45f : 0.30f);      // ~120 ms a l'apparition, ~300 ms au retour
    if (statusAlpha < 0.005f) statusAlpha = 0.0f;
    if (statusAlpha > 0.995f) statusAlpha = 1.0f;
    presetText = presetLine();

    // ---- lumieres
    ledLevel += ((on ? 1.0f : 0.0f) - ledLevel) * (on ? 0.45f : 0.28f);
    amber += ((mode ? 1.0f : 0.0f) - amber) * 0.30f;
    for (auto* v : { &ledLevel, &amber })
    {
        if (*v < 0.003f) *v = 0.0f;
        if (*v > 0.997f) *v = 1.0f;
    }
    updateMeter();

    // ---- redessins limites a ce qui change
    auto changed = [] (float& drawn, float v) { if (std::abs (drawn - v) < 0.003f) return false; drawn = v; return true; };
    bool lights = dFirst;
    lights |= changed (dLed, ledLevel);
    lights |= changed (dAmber, amber);
    lights |= changed (dGlow, glow);
    for (int i = 0; i < numBars; ++i) lights |= changed (dBars[i], barFill[i]);
    if (lights) askRepaint (layout::haloRect);
    if (mode != dMode || dFirst)   { dMode = mode;   askRepaint (Rectangle<float> (layout::slotW, layout::slotH).withCentre (layout::modePos).expanded (3.0f)); }
    if (krazy != dKrazy || dFirst) { dKrazy = krazy; askRepaint (Rectangle<float> (layout::slotW, layout::slotH).withCentre (layout::krazyPos).expanded (3.0f)); }
    if (footDown != dFootDown)     { dFootDown = footDown; askRepaint (Rectangle<float> (layout::footR * 2.4f, layout::footR * 2.4f).withCentre (layout::fsPos)); }
    if (changed (dStatus, statusAlpha) || statusText != dStatusText || presetText != dPresetText || hover != dHover)
    {
        dStatusText = statusText; dPresetText = presetText; dHover = hover;
        askRepaint (layout::presetRect.expanded (3.0f));
    }
    dFirst = false;
}

//==============================================================================
void WackdAudioProcessorEditor::paint (Graphics& g)
{
    lastPaintMs = Time::getMillisecondCounterHiRes();
    repaintAskedMs = 0.0;
    g.fillAll (Colour (0xff111112));          // derriere les jacks : le fond de l'image est transparent
    const Image& bg = bgScaled.isValid() ? bgScaled : background;
    g.setImageResamplingQuality (&bg == &background ? Graphics::highResamplingQuality : Graphics::lowResamplingQuality);
    if (bg.isValid()) g.drawImage (bg, getLocalBounds().toFloat());

    g.addTransform (AffineTransform::scale (k()));
    g.setImageResamplingQuality (Graphics::mediumResamplingQuality);
    drawLights (g);
    drawSwitches (g);
    drawPrint (g);
    drawFoot (g);
    drawBar (g);
}

void WackdAudioProcessorEditor::drawLights (Graphics& g)
{
    const float wColour[2] = { 1.0f - amber, amber };
    // 1. halos sur la facade (calques alpha precalcules), doses par le reglage Glow (25 a 100 %)
    const auto hr = layout::haloRect;
    for (int c = 0; c < 2; ++c)
    {
        const auto& im = haloImg[c];
        if (wColour[c] <= 0.003f || ! im.isValid()) continue;
        const int lw = im.getWidth(), lh = im.getHeight() / 10;
        for (int j = 0; j < 10; ++j)
        {
            const float lvl = (j == 0 ? ledLevel : barFill[j - 1]) * glow * wColour[c];
            if (lvl <= 0.003f) continue;
            g.setOpacity (jmin (1.0f, lvl));
            g.drawImage (im, roundToInt (hr.getX()), roundToInt (hr.getY()), roundToInt (hr.getWidth()), roundToInt (hr.getHeight()),
                         0, j * lh, lw, lh);
        }
    }
    // 2. barres allumees (sources, jamais dosees par Glow)
    const auto br = layout::barsRect;
    for (int c = 0; c < 2; ++c)
    {
        if (wColour[c] <= 0.003f || ! barsImg[c].isValid()) continue;
        for (int i = 0; i < numBars; ++i)
        {
            const float lvl = barFill[i] * wColour[c];
            if (lvl <= 0.003f) continue;
            const float x = layout::barX0 + (float) i * layout::barStep - (layout::barStep - layout::barW) * 0.5f;
            Graphics::ScopedSaveState ss (g);
            g.reduceClipRegion (Rectangle<float> (x, br.getY(), layout::barStep, br.getHeight()).getSmallestIntegerContainer());
            g.setOpacity (jmin (1.0f, lvl));
            g.drawImage (barsImg[c], br);
        }
    }
    // 3. LED allumee
    const auto lr = Rectangle<float> (layout::ledW, layout::ledH).withCentre (layout::ledPos);
    for (int c = 0; c < 2; ++c)
    {
        const float lvl = ledLevel * wColour[c];
        if (lvl <= 0.003f || ! ledImg[c].isValid()) continue;
        g.setOpacity (jmin (1.0f, lvl));
        g.drawImage (ledImg[c], lr);
    }
    // 4. effet glow : lueur serree par-dessus la LED et les barres allumees (dosee par Glow, comme le halo)
    for (int c = 0; c < 2; ++c)
    {
        const auto& im = bloomImg[c];
        if (wColour[c] <= 0.003f || ! im.isValid()) continue;
        const int lw = im.getWidth(), lh = im.getHeight() / 10;
        for (int j = 0; j < 10; ++j)
        {
            const float lvl = (j == 0 ? ledLevel : barFill[j - 1]) * glow * wColour[c];
            if (lvl <= 0.003f) continue;
            g.setOpacity (jmin (1.0f, lvl));
            g.drawImage (im, roundToInt (hr.getX()), roundToInt (hr.getY()), roundToInt (hr.getWidth()), roundToInt (hr.getHeight()),
                         0, j * lh, lw, lh);
        }
    }
    g.setOpacity (1.0f);
}

void WackdAudioProcessorEditor::drawSwitches (Graphics& g)
{
    g.setImageResamplingQuality (Graphics::highResamplingQuality);
    for (int s = 0; s < 2; ++s)
    {
        const bool right = flag (s == 0 ? "mode" : "krazy");
        const auto r = Rectangle<float> (layout::slotW, layout::slotH).withCentre (s == 0 ? layout::modePos : layout::krazyPos);
        if (slideImg[right ? 1 : 0].isValid()) g.drawImage (slideImg[right ? 1 : 0], r);
    }
    g.setImageResamplingQuality (Graphics::mediumResamplingQuality);
}

void WackdAudioProcessorEditor::drawPrint (Graphics& g)
{
    g.setColour (ink);
    g.fillPath (printPath);
    if (logo != nullptr)
    {
        const auto vb = logo->getDrawableBounds();
        const float w = layout::logoW, h = w * vb.getHeight() / jmax (1.0f, vb.getWidth());
        logo->drawWithin (g, { layout::logoPos.x - w * 0.5f, layout::logoPos.y - h * 0.5f, w, h }, RectanglePlacement::centred, 1.0f);
    }
}

void WackdAudioProcessorEditor::drawFoot (Graphics& g)
{
    if (! footDown) return;      // bouton enfonce (fonctionnement d'Echoflex)
    const auto c = layout::fsPos;
    const float r = layout::footR * 0.62f;
    g.setColour (Colours::black.withAlpha (0.25f));
    g.fillEllipse (c.x - r, c.y - r, r * 2.0f, r * 2.0f);
}

void WackdAudioProcessorEditor::drawBar (Graphics& g)
{
    // pastille unique (400 x 38) : barre de presets au repos, ligne d'etat pendant les reglages
    const auto r = layout::presetRect;
    const bool barHot = hover == Hit::presetPrev || hover == Hit::presetName || hover == Hit::presetNext;
    const float rad = r.getHeight() * 0.5f;
    g.setColour (pillOut);  g.fillRoundedRectangle (r.expanded (1.5f), rad + 1.5f);
    g.setColour (pillRim.brighter (barHot && statusAlpha <= 0.0f ? 0.5f : 0.0f));
    g.fillRoundedRectangle (r.expanded (0.5f), rad + 0.5f);
    g.setColour (pillFace); g.fillRoundedRectangle (r, rad);

    g.setFont (Font (FontOptions (mediumFace).withPointHeight (layout::presetFont)));
    if (statusAlpha > 0.0f)
    {
        g.setColour (pillInk.withAlpha (statusAlpha));
        g.drawFittedText (statusText, r.reduced (rad, 0.0f).translated (0.0f, 1.0f).toNearestInt(), Justification::centred, 1, 0.6f);
    }
    const float a = 1.0f - statusAlpha;
    if (a <= 0.0f) return;
    auto arrow = [&] (Rectangle<float> ar, bool left, bool hot)
    {
        Path p; const auto c = ar.getCentre(); const float sz = 5.5f;
        if (left) p.addTriangle (c.x - sz * 0.8f, c.y, c.x + sz * 0.6f, c.y - sz, c.x + sz * 0.6f, c.y + sz);
        else      p.addTriangle (c.x + sz * 0.8f, c.y, c.x - sz * 0.6f, c.y - sz, c.x - sz * 0.6f, c.y + sz);
        g.setColour ((hot ? Colours::white : pillArrow).withAlpha (a));
        g.fillPath (p);
    };
    arrow (r.withWidth (arrowW), true, hover == Hit::presetPrev);
    arrow (r.withTrimmedLeft (r.getWidth() - arrowW), false, hover == Hit::presetNext);
    g.setColour (pillInk.withAlpha ((hover == Hit::presetName ? 1.0f : 0.94f) * a));
    g.drawFittedText (presetText, r.reduced (arrowW, 0.0f).translated (0.0f, 1.0f).toNearestInt(), Justification::centred, 1, 0.7f);
}

//==============================================================================
// Souris
//==============================================================================
WackdAudioProcessorEditor::Hit WackdAudioProcessorEditor::hitAt (Point<float> u) const
{
    const auto slot = [] (Point<float> c) { return Rectangle<float> (layout::slotW, layout::slotH).withCentre (c).expanded (4.0f); };
    if (slot (layout::modePos).contains (u))  return Hit::mode;
    if (slot (layout::krazyPos).contains (u)) return Hit::krazy;
    if (labelHit[0].contains (u)) return Hit::modeL;
    if (labelHit[1].contains (u)) return Hit::modeR;
    if (labelHit[2].contains (u)) return Hit::krazyL;
    if (labelHit[3].contains (u)) return Hit::krazyR;
    if (u.getDistanceFrom (layout::fsPos) <= layout::footR) return Hit::foot;
    const auto r = layout::presetRect;
    if (r.contains (u))
        return u.x < r.getX() + arrowW ? Hit::presetPrev : (u.x > r.getRight() - arrowW ? Hit::presetNext : Hit::presetName);
    return Hit::none;
}

void WackdAudioProcessorEditor::mouseMove (const MouseEvent& e)
{
    hover = hitAt (toUnits (e.position));
    setMouseCursor (hover == Hit::none ? MouseCursor::NormalCursor : MouseCursor::PointingHandCursor);
}

void WackdAudioProcessorEditor::mouseExit (const MouseEvent&) { hover = Hit::none; }

void WackdAudioProcessorEditor::mouseDown (const MouseEvent& e)
{
    const auto h = hitAt (toUnits (e.position));
    if (e.mods.isPopupMenu())
    {
        // clic droit sur une commande : son MIDI Learn en tete du menu
        showContextMenu ((h == Hit::mode || h == Hit::modeL || h == Hit::modeR) ? 4
                         : (h == Hit::krazy || h == Hit::krazyL || h == Hit::krazyR) ? 5 : h == Hit::foot ? 6 : -1);
        return;
    }
    if (statusAlpha > 0.0f && layout::presetRect.contains (toUnits (e.position)))
    {   // la ligne d'etat ne bloque pas : un clic fait revenir la barre de presets
        statusUntil = 0.0;
        return;
    }
    switch (h)
    {
        case Hit::mode:   setParam ("mode",  flag ("mode")  ? 0.0f : 1.0f); break;
        case Hit::modeL:  setParam ("mode",  0.0f); break;
        case Hit::modeR:  setParam ("mode",  1.0f); break;
        case Hit::krazy:  setParam ("krazy", flag ("krazy") ? 0.0f : 1.0f); break;
        case Hit::krazyL: setParam ("krazy", 0.0f); break;
        case Hit::krazyR: setParam ("krazy", 1.0f); break;
        case Hit::foot:
            footDown = true;
            setParam ("active", flag ("active") ? 0.0f : 1.0f);
            break;
        case Hit::presetPrev: stepPreset (-1); break;
        case Hit::presetNext: stepPreset (1); break;
        case Hit::presetName: showPresetMenu(); break;
        case Hit::none: break;
    }
}

void WackdAudioProcessorEditor::mouseUp (const MouseEvent&) { footDown = false; }

void WackdAudioProcessorEditor::mouseWheelMove (const MouseEvent& e, const MouseWheelDetails& w)
{
    const auto h = hitAt (toUnits (e.position));
    const float step = (std::abs (w.deltaY) > 1.0e-6f ? w.deltaY : w.deltaX) * (w.isReversed ? -1.0f : 1.0f);
    if (std::abs (step) <= 0.0f) return;
    if (h == Hit::mode)  setParam ("mode",  step < 0 ? 1.0f : 0.0f);
    if (h == Hit::krazy) setParam ("krazy", step < 0 ? 1.0f : 0.0f);
}

//==============================================================================
// Presets
//==============================================================================
static void addPresetItems (PopupMenu& factory, PopupMenu& load, PopupMenu& save, const WackdAudioProcessor& proc, int cp)
{
    for (int i = 0; i < WackdAudioProcessor::getNumFactoryPresets(); ++i)
        factory.addItem (100 + i, String (i + 1) + ". " + WackdAudioProcessor::getFactoryPreset (i).name, true, cp == i);
    for (int s = 1; s <= 9; ++s)
    {
        const bool exists = proc.hasUserPreset (s);
        load.addItem (200 + s, "User " + String (s) + (exists ? "" : "  (empty)"), exists, cp == 100 + s);
        save.addItem (300 + s, "User " + String (s) + (exists ? "  (overwrite)" : ""));
    }
}

void WackdAudioProcessorEditor::showPresetMenu()
{
    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    NineHandsMenu::addHeader (m, menuLnf.f, NineHandsMenu::icoPreset, menuAccent, "Presets", presetLine());
    PopupMenu factory, load, save;
    const int cp = editedSincePreset() ? -1 : proc.currentPreset.load();
    addPresetItems (factory, load, save, proc, cp);
    m.addSectionHeader ("Factory presets");
    for (int i = 0; i < WackdAudioProcessor::getNumFactoryPresets(); ++i)
        m.addItem (100 + i, String (i + 1) + ". " + WackdAudioProcessor::getFactoryPreset (i).name, true, cp == i);
    m.addSeparator();
    m.addSubMenu ("Load user preset", load);
    m.addSubMenu ("Save user preset", save);
    const auto area = layout::presetRect.transformedBy (AffineTransform::scale (k())).getSmallestIntegerContainer();
    m.showMenuAsync (PopupMenu::Options().withTargetScreenArea (localAreaToGlobal (area)),
        [safe = Component::SafePointer<WackdAudioProcessorEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            if (r >= 100 && r < 200)      safe->loadFactory (r - 100);
            else if (r > 200 && r < 300)  safe->loadUser (r - 200);
            else if (r > 300 && r < 400)
            {
                if (safe->proc.saveUserPreset (r - 300)) { safe->snapshotPreset(); safe->lastPreset = safe->proc.currentPreset.load(); safe->flash ("Saved  User " + String (r - 300)); }
            }
        });
}

//==============================================================================
// Menu clic droit (design d'Octopus, NineHandsMenu.h), toujours ouvert a l'endroit du clic
//==============================================================================
void WackdAudioProcessorEditor::showContextMenu (int learnIdx)
{
    using namespace NineHandsMenu;
    PopupMenu menu;
    menu.setLookAndFeel (&menuLnf);
    auto ccText = [this] (int i) { const int cc = proc.ccMap[i].load(); return cc >= 0 ? "CC " + String (cc) : String ("not assigned"); };
    const int lt = proc.learnTarget.load();
    if (learnIdx >= 0)
    {
        const String name = WackdAudioProcessor::learnDef (learnIdx).name;
        const int ico = learnIdx < 4 ? icoKnob : learnIdx < 6 ? icoSwitch : icoPedal;
        addHeader (menu, menuLnf.f, ico, menuAccent, name, "MIDI: " + ccText (learnIdx));
        const int last = learnIdx == 6 ? 7 : learnIdx;          // footswitch : ON/OFF et bascule
        for (int i = learnIdx; i <= last; ++i)
        {
            const String n = WackdAudioProcessor::learnDef (i).name;
            menu.addItem (1000 + i, "MIDI Learn: " + n + (i != learnIdx ? "  (" + ccText (i) + ")" : String()), true, lt == i);
            menu.addItem (1100 + i, "Clear MIDI: " + n, proc.ccMap[i].load() >= 0);
        }
        if (lt >= 0) menu.addItem (1200, "Cancel MIDI learn");
        menu.addSeparator();
    }
    else
        addHeader (menu, menuLnf.f, icoPedal, menuAccent, "Wack'd", "Chorus / Flanger  v" + String (JucePlugin_VersionString));

    PopupMenu sizes, defSizes;
    {
        const char* names[numSizes] = { "60 %", "75 %", "100 %" };
        const int def = WigaWindowSize::defaultIndex ("Wackd", numSizes);
        for (int i = 0; i < numSizes; ++i)
        {
            sizes.addItem (1 + i, String (names[i]) + (i == def ? "  (default)" : ""), true, std::abs (getHeight() - sizeHeight (i)) <= 2);
            defSizes.addItem (20 + i, names[i], true, i == def);
        }
        sizes.addSeparator();
        sizes.addSubMenu ("Default size (new windows)", defSizes);
    }
    menu.addSubMenu ("Plugin size", sizes);
    PopupMenu glowM;                   // reglage du halo des lumieres (regle des skills, nov. 2026)
    {
        const int now = roundToInt (glow * 100.0f);
        for (int i = 0; i < NineHandsGlow::numSteps; ++i)
        {
            const int pc = NineHandsGlow::steps[i];
            glowM.addItem (60 + i, "Glow " + String (pc) + " %" + (pc == 100 ? "  (default)" : ""), true, now == pc);
        }
    }
    menu.addSubMenu ("Glow (halo of the lights)", glowM);
    menu.addSeparator();

    PopupMenu factory, load, save;
    addPresetItems (factory, load, save, proc, editedSincePreset() ? -1 : proc.currentPreset.load());
    menu.addSubMenu ("Factory presets", factory);
    menu.addSubMenu ("Load user preset", load);
    menu.addSubMenu ("Save user preset", save);
    menu.addSeparator();

    PopupMenu outMenu;
    const bool cf7 = flag ("stereo");
    outMenu.addItem (40, "Mono compatible (before amp sim)", true, ! cf7);
    outMenu.addItem (41, "CF7 stereo: OUT2 inverted (after amp sim)", true, cf7);
    menu.addSubMenu ("Output", outMenu);

    PopupMenu midi;
    midi.addSectionHeader ("MIDI Learn");
    for (int i = 0; i < WackdAudioProcessor::numLearn; ++i)
        midi.addItem (1000 + i, "Learn: " + String (WackdAudioProcessor::learnDef (i).name) + "  (" + ccText (i) + ")", true, lt == i);
    midi.addSeparator();
    if (lt >= 0) midi.addItem (1200, "Cancel MIDI learn");
    midi.addItem (1201, "Clear all MIDI assignments");
    midi.addSeparator();
    midi.addItem (906, "Mode / Krazy: 64+ = Flanger / Wack'd", false);
    midi.addItem (907, "Footswitch: 64+ ON / 0-63 OFF", false);
    midi.addItem (908, "Program Change 1-" + String (WackdAudioProcessor::getNumFactoryPresets()) + "  Factory presets", false);
    menu.addSubMenu ("MIDI", midi);
    menu.addSeparator();
    menu.addItem (999, "Wack'd v" + String (JucePlugin_VersionString) + "  NINE HANDS | DSP", false);

    menu.showMenuAsync (PopupMenu::Options().withMousePosition(),       // toujours la ou l'on clique
        [safe = Component::SafePointer<WackdAudioProcessorEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            auto& ed = *safe;
            auto& pr = ed.proc;
            if      (r >= 1 && r < 1 + numSizes) ed.setWindowHeight (sizeHeight (r - 1));
            else if (r >= 20 && r < 20 + numSizes)
            {
                WigaWindowSize::setDefaultIndex ("Wackd", r - 20);
                ed.setWindowHeight (sizeHeight (r - 20));
            }
            else if (r >= 60 && r < 60 + NineHandsGlow::numSteps)
            {
                ed.setGlowPercent (NineHandsGlow::steps[r - 60]);
                ed.flash ("Glow  " + String (NineHandsGlow::steps[r - 60]) + " %");
            }
            else if (r >= 100 && r < 200) ed.loadFactory (r - 100);
            else if (r > 200 && r < 300)  ed.loadUser (r - 200);
            else if (r > 300 && r < 400)
            {
                if (pr.saveUserPreset (r - 300)) { ed.snapshotPreset(); ed.lastPreset = pr.currentPreset.load(); ed.flash ("Saved  User " + String (r - 300)); }
            }
            else if (r == 40 || r == 41) ed.setParam ("stereo", r == 41 ? 1.0f : 0.0f);
            else if (r >= 1000 && r < 1000 + WackdAudioProcessor::numLearn)
            {
                const int t = r - 1000;
                pr.learnTarget.store (pr.learnTarget.load() == t ? -1 : t);       // re-cliquer annule
            }
            else if (r >= 1100 && r < 1100 + WackdAudioProcessor::numLearn)
            {
                pr.ccMap[r - 1100].store (-1);
                ed.flash (String (WackdAudioProcessor::learnDef (r - 1100).name) + "  MIDI cleared");
            }
            else if (r == 1200) pr.learnTarget.store (-1);
            else if (r == 1201) { pr.learnTarget.store (-1); pr.clearMidiMap(); ed.flash ("All MIDI cleared"); }
        });
}

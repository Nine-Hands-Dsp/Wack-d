// Captures PNG de la fenetre reelle de WACK'D (meme code que le plugin), pour l'apercu et la notice.
#include "PluginProcessor.h"
#include "PluginEditor.h"
#include "BinaryData.h"
using namespace juce;

int main (int argc, char** argv)
{
    ScopedJuceInitialiser_GUI init;
    const String out = argc > 1 ? argv[1] : ".";
    WackdAudioProcessor proc;
    proc.prepareToPlay (48000.0, 256);
    std::unique_ptr<AudioProcessorEditor> ed (proc.createEditor());
    auto* we = static_cast<WackdAudioProcessorEditor*> (ed.get());
    std::printf ("taille par defaut : %d x %d\n", ed->getWidth(), ed->getHeight());

    auto pump = [] (int n) { for (int i = 0; i < n; ++i) MessageManager::getInstance()->runDispatchLoopUntil (35); };
    auto set = [&] (const char* id, float v) { if (auto* p = proc.apvts.getParameter (id)) p->setValueNotifyingHost (p->convertTo0to1 (v)); };
    auto save = [&] (const String& name, float scale)
    {
        auto img = ed->createComponentSnapshot (ed->getLocalBounds(), true, scale);
        File f (out + "/" + name + ".png"); f.deleteFile();
        FileOutputStream os (f); PNGImageFormat().writeImageToStream (img, os);
        std::printf ("%s (%d x %d)\n", f.getFullPathName().toRawUTF8(), img.getWidth(), img.getHeight());
    };
    auto state = [&] (int preset, bool on, int glowPc, const String& status, int meterKnob = -1)
    {
        if (preset >= 0) proc.applyFactoryPreset (preset);
        set ("active", on ? 1.f : 0.f);
        we->setGlowPercent (glowPc);
        we->setMeterKnob (meterKnob);
        pump (8);
        we->flash (status, status.isNotEmpty() ? 60.0 : 0.0);
        we->settleForCapture();
        pump (4);
    };

    // fenetre par defaut (493 px, « 60 % »)
    we->forceRenderScale (2.0f); pump (6);
    state (0, true, 100, {});
    save ("wk_default", 2.0f);

    // rendu exact de la pedale seule (1230 x 1800)
    we->setWindowHeight (900);
    we->forceRenderScale (2.0f);
    pump (8);
    const float ex = 1800.0f / (float) ed->getHeight();
    state (0, true, 100, {});                                       save ("wk_exact_chorus", ex);
    state (2, true, 100, String::fromUTF8 ("SPEED  70 %  \xc2\xb7  1.3 Hz"), 0);        save ("wk_exact_flanger", ex);
    state (8, true, 100, {});                                       save ("wk_exact_myroad", ex);
    state (0, false, 100, {});                                      save ("wk_exact_bypass", ex);
    state (0, true, 25, {});                                        save ("wk_glow_25", ex);
    state (0, true, 50, {});                                        save ("wk_glow_50", ex);
    state (0, true, 75, {});                                        save ("wk_glow_75", ex);
    we->setGlowPercent (100);

    // animation d'un potard (SPEED) : images successives pour le GIF de controle
    if (argc > 2)
    {
        state (0, true, 100, {});
        auto* p = proc.apvts.getParameter ("speed");
        int fr = 0;
        auto shot = [&]
        {
            pump (1);
            auto img = ed->createComponentSnapshot ({ 0, 0, ed->getWidth() / 2 + 40, 190 }, true, 1.0f);
            File f (out + "/anim_" + String (fr++).paddedLeft ('0', 3) + ".png"); f.deleteFile();
            FileOutputStream os (f); PNGImageFormat().writeImageToStream (img, os);
        };
        for (int i = 0; i <= 30; ++i) { p->setValueNotifyingHost (0.3f + 0.6f * (float) i / 30.0f); shot(); }      // lent
        for (int i = 0; i < 8; ++i) shot();
        for (int i = 0; i <= 6; ++i) { p->setValueNotifyingHost (0.9f - 0.9f * (float) i / 6.0f); shot(); }        // rapide
        for (int i = 0; i < 8; ++i) shot();
        for (int i = 0; i <= 2; ++i) { p->setValueNotifyingHost (1.0f * (float) i / 2.0f); shot(); }               // tres rapide
        for (int i = 0; i < 10; ++i) shot();
    }

    // menus clic droit (design Octopus, NineHandsMenu.h) : rendu hors ecran avec le meme LookAndFeel que le plugin
    {
        NineHandsMenu::MenuLnf lnf;
        lnf.f = { Typeface::createSystemTypefaceFor (BinaryData::PoppinsRegular_ttf, BinaryData::PoppinsRegular_ttfSize),
                  Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize),
                  Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf, BinaryData::PoppinsBold_ttfSize) };
        struct It { String text; bool sep = false, sub = false, ticked = false, active = true; };
        auto render = [&] (const String& name, const String& title, const String& subtitle, int ico, const std::vector<It>& items, int hiIndex)
        {
            NineHandsMenu::Header hd (lnf.f, ico, Colour (0xff78d2f5), title, subtitle);
            int w = 0, h = 0; hd.getIdealSize (w, h);
            const int border = lnf.getPopupMenuBorderSize();
            int totalH = border * 2 + h + 11, maxW = w;
            for (auto& it : items) { int iw, ih; lnf.getIdealPopupMenuItemSize (it.text, it.sep, 0, iw, ih); totalH += ih; maxW = jmax (maxW, iw + (it.sub ? 20 : 0)); }
            maxW += border * 2;
            Image img (Image::ARGB, maxW * 2, totalH * 2, true);
            Graphics g (img); g.addTransform (AffineTransform::scale (2.0f));
            lnf.drawPopupMenuBackground (g, maxW, totalH);
            int y = border;
            hd.setSize (maxW - border * 2, h);
            { Graphics::ScopedSaveState ss (g); g.setOrigin (border, y); hd.paint (g); }
            y += h;
            lnf.drawPopupMenuItem (g, { border, y, maxW - border * 2, 11 }, true, true, false, false, false, {}, {}, nullptr, nullptr); y += 11;
            for (size_t i = 0; i < items.size(); ++i)
            {
                const auto& it = items[i]; int iw, ih; lnf.getIdealPopupMenuItemSize (it.text, it.sep, 0, iw, ih);
                lnf.drawPopupMenuItem (g, { border, y, maxW - border * 2, ih }, it.sep, it.active, (int) i == hiIndex, it.ticked, it.sub, it.text, {}, nullptr, nullptr);
                y += ih;
            }
            File f (out + "/" + name + ".png"); f.deleteFile();
            FileOutputStream os (f); PNGImageFormat().writeImageToStream (img, os);
            std::printf ("%s\n", f.getFullPathName().toRawUTF8());
        };
        render ("wk_menu", "Wack'd", "Chorus / Flanger  v2.0.4", NineHandsMenu::icoPedal,
                { { "Plugin size", false, true }, { "Glow (halo of the lights)", false, true }, { "", true },
                  { "Factory presets", false, true }, { "Load user preset", false, true }, { "Save user preset", false, true }, { "", true },
                  { "Output", false, true }, { "MIDI", false, true }, { "", true },
                  { "Wack'd v2.0.4  NINE HANDS | DSP", false, false, false, false } }, 1);
        std::vector<It> g;
        for (int pc : { 25, 50, 75, 100 })
            g.push_back ({ "Glow " + String (pc) + " %" + (pc == 100 ? "  (default)" : ""), false, false, pc == 100 });
        render ("wk_menu_glow", "Glow", "Halo of the lights", NineHandsMenu::icoGlow, g, 1);
        render ("wk_menu_knob", "Speed", "MIDI: not assigned", NineHandsMenu::icoKnob,
                { { "MIDI Learn: Speed" }, { "Clear MIDI: Speed", false, false, false, false }, { "", true },
                  { "Plugin size", false, true }, { "Glow (halo of the lights)", false, true } }, 0);
    }
    ed.reset();
    return 0;
}

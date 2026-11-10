#pragma once

#include "PluginProcessor.h"
#include "Layout.h"
#include "NHKnob.h"
#include "NineHandsMenu.h"
#include <juce_gui_basics/juce_gui_basics.h>

//==============================================================================
// WACK'D v2 (NINE HANDS | DSP) : pedale simple, fond 1230 x 1800 px plein cadre (repere 615 x 900, Layout.h,
// genere par tools/make_art.py). Le fond contient coque, jacks, fentes des inverseurs, LED et barres eteintes,
// footswitch ; l'editeur dessine par-dessus : halos (doses par Glow), barres et LED allumees, selecteurs,
// serigraphie vectorielle (Poppins), logo NINE HANDS | DSP, pastille presets / ligne d'etat.
// Les 4 potards sont des composants nh::Knob (calques qui tournent ensemble, flou de mouvement).
//==============================================================================
class WackdAudioProcessorEditor : public juce::AudioProcessorEditor,
                                  private juce::Timer
{
public:
    explicit WackdAudioProcessorEditor (WackdAudioProcessor&);
    ~WackdAudioProcessorEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;
    void parentHierarchyChanged() override;
    void visibilityChanged() override;

    void mouseDown (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    void mouseMove (const juce::MouseEvent&) override;
    void mouseExit (const juce::MouseEvent&) override;
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails&) override;

    static constexpr float baseW = layout::frameW, baseH = layout::frameH;
    static constexpr int numSizes = 3;                          // 60 % (defaut) / 75 % / 100 %
    static constexpr int heightDefault = 493, heightMax = 1437;
    static int sizeHeight (int idx);
    void setWindowHeight (int h);

    // outil de rendu (captures) : echelle forcee, etat lumineux immediat
    void forceRenderScale (float sc);
    void settleForCapture();
    void setGlowPercent (int pc);
    void flash (const juce::String& text, double seconds = 2.5);
    void setMeterKnob (int i) { meterKnob = i; }

private:
    void timerCallback() override;
    void useSoftwareRenderer();
    float physicalScale() const;
    void askRepaint (juce::Rectangle<float> unitsRect);
    void rebuildCaches (float sc = 0.0f);
    float k() const { return (float) getHeight() / baseH; }
    juce::Point<float> toUnits (juce::Point<float> p) const { return p / k(); }

    enum class Hit { none, mode, modeL, modeR, krazy, krazyL, krazyR, foot, presetPrev, presetName, presetNext };
    Hit hitAt (juce::Point<float> u) const;

    void setParam (const juce::String& id, float plain);
    bool flag (const char* id) const { return proc.apvts.getRawParameterValue (id)->load() > 0.5f; }
    float value (const char* id) const { return proc.apvts.getRawParameterValue (id)->load(); }
    juce::String knobText (int i) const;
    juce::String presetLine() const;
    void loadFactory (int i);
    void loadUser (int slot);
    void snapshotPreset();
    bool editedSincePreset() const;
    void stepPreset (int delta);
    void showPresetMenu();
    void showContextMenu (int learnIdx = -1);
    void buildPrint();
    void updateMeter();

    void drawLights (juce::Graphics&);
    void drawSwitches (juce::Graphics&);
    void drawPrint (juce::Graphics&);
    void drawFoot (juce::Graphics&);
    void drawBar (juce::Graphics&);

    WackdAudioProcessor& proc;
    NineHandsMenu::MenuLnf menuLnf;
    juce::Typeface::Ptr regularFace, mediumFace, semiFace, boldFace;
    std::unique_ptr<juce::Drawable> logo;
    juce::Path printPath;                       // serigraphie (unites du plugin)
    juce::Rectangle<float> labelHit[4];         // CHORUS, FLANGER, NORMAL, WACK'D

    juce::Image background, bgScaled, ledImg[2], barsImg[2], haloImg[2], slideImg[2];
    int cacheW = 0, cacheH = 0;
    float cacheScale = 0.0f, forcedScale = 0.0f;
    int resizeSettle = 0;
    void* lastPeer = nullptr;
    double lastPaintMs = 0.0, repaintAskedMs = 0.0, lastScaleCheckMs = 0.0, lastRendererCheckMs = 0.0, lastGlowCheckMs = 0.0;

    std::unique_ptr<nh::Knob> knobs[4];

    // etat affiche
    static constexpr int numBars = 9;
    float glow = 1.0f;                          // reglage Glow (1 = 100 %)
    float ledLevel = 1.0f, amber = 0.0f;        // amber : 0 = chorus (bleu glace), 1 = flanger (jaune-orange)
    float meterLevel = 0.0f, barFill[numBars] {};
    int meterKnob = -1;                         // dernier potard tourne (-1 = moyenne des 4)
    bool footDown = false;
    Hit hover = Hit::none;

    // pastille unique : barre de presets au repos, ligne d'etat pendant les reglages (fondu croise)
    juce::String statusText, presetText;
    double statusUntil = 0.0;
    float statusAlpha = 0.0f;
    float lastKnob[4] { -1.0f, -1.0f, -1.0f, -1.0f };
    bool lastMode = false, lastKrazy = false, lastOn = true, lastStereo = false;
    int lastPreset = -999;
    float presetSnap[6] {};

    // dernier etat dessine (on ne redessine une zone que si elle a change)
    float dLed = -1.0f, dAmber = -1.0f, dGlow = -1.0f, dStatus = -1.0f, dBars[numBars];
    bool dMode = false, dKrazy = false, dFootDown = false, dFirst = true;
    Hit dHover = Hit::none;
    juce::String dStatusText, dPresetText;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (WackdAudioProcessorEditor)
};

// genere par tools/make_art.py - ne pas modifier a la main (repere 615 x 900 = fond 1230 x 1800 px / 2)
#pragma once
#include <juce_graphics/juce_graphics.h>
namespace layout
{
    constexpr float frameW = 615.00f, frameH = 900.00f;
    const juce::Point<float> knobPos[4] = { { 89.69f, 120.60f }, { 234.59f, 120.60f }, { 379.95f, 120.60f }, { 525.78f, 120.60f } };
    const float knobR = 57.00f, knobS = 125.20f;   // rayon du potard, cote du composant nh::Knob
    const juce::Point<float> modePos { 144.81f, 310.77f }, krazyPos { 471.24f, 310.77f };
    const float slotW = 100.00f, slotH = 34.53f;
    const juce::Point<float> ledPos { 306.98f, 307.80f }; const float ledW = 91.00f, ledH = 92.00f, ledR = 40.00f;
    const juce::Rectangle<float> barsRect { 252.00f, 355.00f, 110.00f, 36.00f };
    const float barX0 = 253.425f, barStep = 12.250f, barW = 8.500f;
    const juce::Rectangle<float> haloRect { 218.00f, 240.00f, 178.00f, 177.00f };   // 10 calques empiles : LED, barres 1-9
    const juce::Rectangle<float> presetRect { 107.50f, 516.50f, 400.00f, 38.00f };
    const float presetFont = 23.0f;
    const juce::Point<float> fsPos { 307.50f, 782.10f }; const float footR = 48.50f;
    const juce::Point<float> logoPos { 307.50f, 859.00f }; const float logoW = 215.00f;
    const juce::Rectangle<float> bodyRect { 16.77f, 0.0f, 581.45f, 900.00f };
    // inscriptions : texte, police (0 Medium, 1 SemiBold, 2 Bold), taille em, x, y, alignement (0 centre, 1 gauche, 2 droite)
    struct Txt { const char* s; int font; float em, x, y; int align; };
    const Txt texts[] = {
        { "0", 0, 12.00f, 35.24f, 177.05f, 0 },
        { "10", 0, 12.00f, 144.14f, 177.05f, 0 },
        { "SPEED", 1, 20.50f, 89.69f, 208.60f, 0 },
        { "0", 0, 12.00f, 180.14f, 177.05f, 0 },
        { "10", 0, 12.00f, 289.03f, 177.05f, 0 },
        { "DEPTH", 1, 20.50f, 234.59f, 208.60f, 0 },
        { "0", 0, 12.00f, 325.50f, 177.05f, 0 },
        { "10", 0, 12.00f, 434.40f, 177.05f, 0 },
        { "DELAY TIME", 1, 20.50f, 379.95f, 208.60f, 0 },
        { "0", 0, 12.00f, 471.33f, 177.05f, 0 },
        { "10", 0, 12.00f, 580.22f, 177.05f, 0 },
        { "REGEN.", 1, 20.50f, 525.78f, 208.60f, 0 },
        { "CHORUS", 1, 14.00f, 137.81f, 280.00f, 2 },
        { "FLANGER", 1, 14.00f, 151.81f, 280.00f, 1 },
        { "MODE", 1, 19.00f, 144.81f, 346.54f, 0 },
        { "NORMAL", 1, 14.00f, 464.24f, 280.00f, 2 },
        { "WACK'D", 1, 14.00f, 478.24f, 280.00f, 1 },
        { "KRAZY", 1, 19.00f, 471.24f, 346.54f, 0 },
        { "OUT1", 1, 15.00f, 33.77f, 445.50f, 1 },
        { "INV.", 1, 15.00f, 33.77f, 526.00f, 1 },
        { "OUT2", 1, 15.00f, 33.77f, 545.00f, 1 },
        { "IN", 1, 15.00f, 578.23f, 445.50f, 2 },
        { "Wack'd", 2, 95.00f, 307.50f, 645.00f, 0 },
        { "flangerus", 1, 36.00f, 307.50f, 697.50f, 0 }
    };
    struct Tick { float x0, y0, x1, y1, w; };
    const Tick ticks[] = {
        { 46.20f, 164.09f, 41.61f, 168.68f, 1.50f },
        { 31.20f, 139.60f, 27.39f, 140.84f, 1.50f },
        { 28.95f, 110.98f, 24.99f, 110.35f, 1.50f },
        { 39.93f, 84.45f, 36.70f, 82.10f, 1.50f },
        { 61.77f, 65.80f, 59.95f, 62.24f, 1.50f },
        { 89.69f, 59.10f, 89.69f, 52.60f, 1.50f },
        { 117.61f, 65.80f, 119.42f, 62.24f, 1.50f },
        { 139.44f, 84.45f, 142.68f, 82.10f, 1.50f },
        { 150.43f, 110.98f, 154.38f, 110.35f, 1.50f },
        { 148.18f, 139.60f, 151.98f, 140.84f, 1.50f },
        { 133.18f, 164.09f, 137.77f, 168.68f, 1.50f },
        { 191.10f, 164.09f, 186.50f, 168.68f, 1.50f },
        { 176.10f, 139.60f, 172.29f, 140.84f, 1.50f },
        { 173.84f, 110.98f, 169.89f, 110.35f, 1.50f },
        { 184.83f, 84.45f, 181.60f, 82.10f, 1.50f },
        { 206.67f, 65.80f, 204.85f, 62.24f, 1.50f },
        { 234.59f, 59.10f, 234.59f, 52.60f, 1.50f },
        { 262.51f, 65.80f, 264.32f, 62.24f, 1.50f },
        { 284.34f, 84.45f, 287.58f, 82.10f, 1.50f },
        { 295.33f, 110.98f, 299.28f, 110.35f, 1.50f },
        { 293.08f, 139.60f, 296.88f, 140.84f, 1.50f },
        { 278.07f, 164.09f, 282.67f, 168.68f, 1.50f },
        { 336.46f, 164.09f, 331.87f, 168.68f, 1.50f },
        { 321.46f, 139.60f, 317.65f, 140.84f, 1.50f },
        { 319.21f, 110.98f, 315.26f, 110.35f, 1.50f },
        { 330.19f, 84.45f, 326.96f, 82.10f, 1.50f },
        { 352.03f, 65.80f, 350.21f, 62.24f, 1.50f },
        { 379.95f, 59.10f, 379.95f, 52.60f, 1.50f },
        { 407.87f, 65.80f, 409.69f, 62.24f, 1.50f },
        { 429.70f, 84.45f, 432.94f, 82.10f, 1.50f },
        { 440.69f, 110.98f, 444.64f, 110.35f, 1.50f },
        { 438.44f, 139.60f, 442.24f, 140.84f, 1.50f },
        { 423.44f, 164.09f, 428.03f, 168.68f, 1.50f },
        { 482.29f, 164.09f, 477.69f, 168.68f, 1.50f },
        { 467.29f, 139.60f, 463.48f, 140.84f, 1.50f },
        { 465.03f, 110.98f, 461.08f, 110.35f, 1.50f },
        { 476.02f, 84.45f, 472.79f, 82.10f, 1.50f },
        { 497.86f, 65.80f, 496.04f, 62.24f, 1.50f },
        { 525.78f, 59.10f, 525.78f, 52.60f, 1.50f },
        { 553.70f, 65.80f, 555.51f, 62.24f, 1.50f },
        { 575.53f, 84.45f, 578.77f, 82.10f, 1.50f },
        { 586.52f, 110.98f, 590.47f, 110.35f, 1.50f },
        { 584.27f, 139.60f, 588.07f, 140.84f, 1.50f },
        { 569.26f, 164.09f, 573.86f, 168.68f, 1.50f }
    };
    struct Tri { float x0, y0, x1, y1, x2, y2; };
    const Tri tris[] = {
        { 23.77f, 445.50f, 30.97f, 441.00f, 30.97f, 450.00f },
        { 23.77f, 545.00f, 30.97f, 540.50f, 30.97f, 549.50f },
        { 583.23f, 445.50f, 590.43f, 441.00f, 590.43f, 450.00f }
    };
}

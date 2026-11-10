# WACK'D (NINE HANDS | DSP) — VST3

Chorus / flanger d'après la pédale **Ibanez CF7 Chorus/Flanger** (série Tone-Lok, 1999), Windows 11 et macOS.
Visuel « Wack'd flangerus » NINE HANDS | DSP.

<p align="center">
  <a href="https://github.com/Nine-Hands-Dsp/Wack-d/releases/latest/download/Wackd-VST3-Windows.zip"><img alt="Télécharger pour Windows" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-Windows-0078D6?style=for-the-badge"></a>
  <a href="https://github.com/Nine-Hands-Dsp/Wack-d/releases/latest/download/Wackd-VST3-macOS.zip"><img alt="Télécharger pour macOS" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-macOS-111111?style=for-the-badge&logo=apple&logoColor=white"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Wack-d/releases/latest/download/Wackd-Notice.pdf"><img alt="Télécharger la notice (PDF)" src="https://img.shields.io/badge/%F0%9F%93%96%20Notice-PDF-919496?style=for-the-badge"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Wack-d/releases/latest"><img alt="Dernière version" src="https://img.shields.io/github/v/release/Nine-Hands-Dsp/Wack-d?label=derni%C3%A8re%20version&color=919496"></a>
</p>

Notice en français : [Wackd-Notice.pdf](https://github.com/Nine-Hands-Dsp/Wack-d/releases/latest/download/Wackd-Notice.pdf)

## Installation

- **Windows** : dézipper et copier `Wackd.vst3` dans `C:\Program Files\Common Files\VST3\`
- **macOS** : dézipper et copier `Wackd.vst3` dans `~/Library/Audio/Plug-Ins/VST3/`

Relancer ensuite l'analyse des plugins dans le DAW. Le plugin apparaît sous le nom **Wackd (NINE HANDS | DSP)**.

## La pédale

| Commande | Rôle |
|---|---|
| SPEED | Vitesse du LFO triangle (plage 1:100) : Chorus 0,1 → 10 Hz, Flanger 0,05 → 5 Hz ; en Wack'd : Chorus 0,6 → 40 Hz, Flanger 0,3 → 20 Hz |
| DEPTH | Amplitude du balayage |
| DELAY TIME | Retard de base : chorus 5 → 25 ms, flanger 0,2 → 16 ms (balayage exponentiel) |
| REGEN. | Réinjection, jusqu'à 95 % en flanger (saturation douce, anti-DC, aigus amortis dans la boucle) |
| MODE | Chorus / Flanger (LED et jauge bleu glace en Chorus, jaune-orangé en Flanger) |
| KRAZY | Normal / Wack'd : modulation fixe ajoutée (R44), signal direct coupé, aigus filtrés vers 6 kHz, LFO beaucoup plus rapide |
| Footswitch | Effet / bypass |
| Jauge (9 barres) | S'allume de gauche à droite selon la valeur du dernier potard tourné |

Sortie (clic droit > Output) : **Mono compatible** par défaut (la droite lit le retard décalé de 90°, aucune annulation devant un simulateur d'ampli mono), ou **CF7 stereo (INV)** d'origine (OUT2 = direct − effet, à placer après l'ampli).

## Interface

- Fenêtre ouverte à **60 %**, impossible de la réduire en dessous ; clic droit > Plugin size : 60 % / 75 % / 100 %, et « Default size (new windows) ».
- **Potards** : glisser verticalement (Maj = réglage fin), molette, double-clic = valeur par défaut. Les calques du potard tournent ensemble avec un flou de mouvement ; la lumière reste fixe en haut à gauche.
- **Inverseurs** : clic sur la fente pour basculer, ou clic sur CHORUS / FLANGER / NORMAL / WACK'D.
- **Pastille** : barre de presets au repos (◀ preset ▶, clic sur le nom pour le menu) ; dès qu'un réglage bouge, elle affiche la valeur en direct pendant 2,5 s.
- **Clic droit** (menus NINE HANDS | DSP, ouverts à l'endroit du clic) : taille, **Glow** (halo de la LED et de la jauge : 25 / 50 / 75 / 100 %), presets d'usine, presets utilisateur 1 à 9, Output, MIDI.

## MIDI

Aucun CC assigné par défaut : clic droit sur une commande > « MIDI Learn », puis bouger la commande MIDI. « Clear MIDI » retire l'assignation. Program Change 1-9 = presets d'usine. Tous les paramètres sont aussi automatisables dans le DAW.

## Presets d'usine

1. Classic Chorus · 2. Lush Stereo Chorus · 3. Jet Flanger · 4. Metallic Flange · 5. Slow Deep Sweep · 6. Wack'd Vibrato · 7. Korny Chirps · 8. Ring Mod Madness · **9. My Road**

**My Road** recrée l'intro de « My Way » (Limp Bizkit, 2000) : MODE Chorus, KRAZY Wack'd, Speed 95,6 % · Depth 1,6 % · Delay Time 73,5 % · Regen 12,3 %.

## Compilation

Le push lance la compilation GitHub Actions (Windows `windows-2022`, macOS binaire universel) puis publie la Release (fichiers à nom fixe, liens ci-dessus).

- `tools/make_art.py` : génère le visuel (fond 1230 × 1800 px, LED, jauge, halos, inverseurs, calques du potard) et `Layout.h`.
- `tools/render` : compile la fenêtre réelle sous Linux et exporte des captures PNG.
- `tools/manual.py` : génère la notice PDF (`docs/`).

Police Poppins (licence OFL, `Poppins-OFL.txt`). Référence DSP : J. O. Smith, *Physical Audio Signal Processing* (CCRMA), chapitre Flanger.

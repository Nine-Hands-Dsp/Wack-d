# Outil hors plugin : compile le processeur + la fenetre de WACK'D sous Linux et exporte des captures PNG (apercu, notice)
#   cmake -B build-render -S tools/render -DJUCE_DIR=/chemin/vers/JUCE && cmake --build build-render -j4
#   build-render/WackdRender_artefacts/WackdRender <dossier de sortie>
cmake_minimum_required(VERSION 3.22)
project(WackdRender VERSION 1.0.0)
set(CMAKE_CXX_STANDARD 17)
add_subdirectory(${JUCE_DIR} JUCE)
set(W ${CMAKE_CURRENT_SOURCE_DIR}/../..)
juce_add_binary_data(WackdData SOURCES
  ${W}/background.png ${W}/led_blue.png ${W}/led_amber.png ${W}/bars_blue.png ${W}/bars_amber.png
  ${W}/halo_blue.png ${W}/halo_amber.png ${W}/slide_left.png ${W}/slide_right.png
  ${W}/knob_shadow.png ${W}/knob_crown.png ${W}/knob_marker.png ${W}/knob_highlight.png
  ${W}/Poppins-Regular.ttf ${W}/Poppins-Medium.ttf ${W}/Poppins-SemiBold.ttf ${W}/Poppins-Bold.ttf ${W}/NineHandsLogoBlack.svg)
juce_add_console_app(WackdRender PRODUCT_NAME "WackdRender")
target_sources(WackdRender PRIVATE main.cpp ${W}/PluginProcessor.cpp ${W}/PluginEditor.cpp)
target_include_directories(WackdRender PRIVATE ${W})
target_compile_definitions(WackdRender PRIVATE JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0 JUCE_ALSA=0 JUCE_JACK=0
  JUCE_USE_XRANDR=0 JUCE_USE_XINERAMA=0 JUCE_USE_XCURSOR=0 JUCE_USE_XSHM=0 JucePlugin_Name="Wackd" JucePlugin_Build_VST3=0
  JucePlugin_VersionString="2.0.0" JUCE_STANDALONE_APPLICATION=1 JUCE_MODAL_LOOPS_PERMITTED=1)
target_link_libraries(WackdRender PRIVATE WackdData juce::juce_audio_utils juce::juce_recommended_config_flags)

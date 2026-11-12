cmake_minimum_required(VERSION 3.22)

# macOS : binaire universel (Apple Silicon + Intel)
set(CMAKE_OSX_ARCHITECTURES "arm64;x86_64" CACHE STRING "")
set(CMAKE_OSX_DEPLOYMENT_TARGET "10.13" CACHE STRING "")

project(WACKD VERSION 2.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
    JUCE
    GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
    GIT_TAG        8.0.15
    GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(JUCE)

juce_add_plugin(Wackd
    COMPANY_NAME                "NINE HANDS | DSP"
    COMPANY_WEBSITE             ""
    PLUGIN_MANUFACTURER_CODE    Wiga
    PLUGIN_CODE                 Wkcf
    FORMATS                     VST3
    PRODUCT_NAME                "Wackd"
    VERSION                     2.1.0
    IS_SYNTH                    FALSE
    NEEDS_MIDI_INPUT            TRUE
    NEEDS_MIDI_OUTPUT           FALSE
    IS_MIDI_EFFECT              FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    COPY_PLUGIN_AFTER_BUILD     FALSE
    VST3_CATEGORIES             "Fx" "Modulation"
)

# visuel v2 (tools/make_art.py), calques du potard (nh::Knob), police Poppins et logo integres au plugin
juce_add_binary_data(WackdData SOURCES
    background.png
    led_blue.png led_amber.png
    bars_blue.png bars_amber.png
    halo_blue.png halo_amber.png
    bloom_blue.png bloom_amber.png
    slide_left.png slide_right.png
    knob_shadow.png knob_crown.png knob_marker.png knob_highlight.png
    Poppins-Regular.ttf Poppins-Medium.ttf Poppins-SemiBold.ttf Poppins-Bold.ttf
    NineHandsLogoBlack.svg)
set_target_properties(WackdData PROPERTIES POSITION_INDEPENDENT_CODE TRUE)

target_sources(Wackd PRIVATE
    PluginProcessor.cpp
    PluginEditor.cpp
)


# verrou de taille de la fenetre du DAW (jamais sous 60 %, jamais au-dela de 150 %)
if(APPLE)
  target_sources(Wackd PRIVATE WindowMinSize.mm)
  target_link_libraries(Wackd PRIVATE "-framework Cocoa")
else()
  target_sources(Wackd PRIVATE WindowMinSize.cpp)
endif()
if(WIN32)
  target_link_libraries(Wackd PRIVATE comctl32 user32)
endif()
if(MSVC)
    target_compile_options(Wackd PRIVATE /utf-8)
endif()

target_compile_definitions(Wackd PUBLIC
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
    JUCE_DISPLAY_SPLASH_SCREEN=0
)

target_link_libraries(Wackd
    PRIVATE
        WackdData
        juce::juce_audio_utils
        juce::juce_audio_processors
        juce::juce_gui_basics
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags
)

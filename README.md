# Visual Effects (VFX) Plugin - Krita 4

Plugin to apply a host of different visual effects seen in post-processing

(Example and descriptive pictures coming eventually!)

Includes the following effects:

* Chromatic Aberration
* Bloom
* Pseudo Lens Flare
* Anamorphic Lens Flare

## How to Install

 1. Open Krita, go to Settings->Manage Resources...->Open Resource Folder
 2. Open the pykrita folder inside the folder that pops up
 3. Download this repository and save the files and folders exactly as they are to the pykrita folder
 4. Close and reopen Krita
 5. Go to Settings->Configure Krita->Python Plugin Manager
 6. Scroll down and enable VFX, click OK to save
 7. Close and reopen Krita again

## How to Use

With an open document active, select a layer you want to apply the effect to, then click Tools->Scripts->VFX - (...)  
This will pop open a window with options to control the effect before applying

**Common Settings:**

* Bias Color - Adds a chosen color to the intermediary results of an operation. This is additive and is used to bring out colors that would otherwise be lacking.
* Power - Multiplies the result by itself X times, making what would normally be very subtle colors more obvious.
* Displacement or Strength - How strong a certain stage for an effect will be, how much it will spread across the screen.
* Bilinear Interpolation - Checking this option will make the plugin run slightly slower, but will make edges created by the effect smoother and less aliased.
* Number of Worker Threads (FOR ADVANCED USERS) - As the warning says, this option is for users who know what their CPU is capable of. Larger values will apply the effect faster on very large images, but if the value exceeds the number of threads your CPU can reasonably handle the process will take longer. The default value of 4 will work well on the vast majority of CPUs that can handle Krita.

Once the effect is applied it will be placed on a new layer as a modified clone of the previously selected layer, the original layer is preserved.

## Planned Features

All listed below are planned to be added to this plugin at some point, no definitive time table or order yet. Check back regularly if you are interested in one or more of these features being added:

* Support for more color profiles - currently only supports 8 bit RGBA
* Help button with detailed description for each widget, on each plugin window
* New effect - Render Lens Dirt
* Color swatch picker for bias color
* Instant preview for any changes

### Extra Notes

This plugin relies on a shared C library for speeding up the computationally expensive parts. The source code for the C libraries is included in the `VFX/src` folder and has been precompiled for 32 and 64 bit versions of Windows, Mac OS, and Linux installations of Python. The source code can be compiled using gcc and the below commands:

```
gcc -shared -m32 -o VFXLib_32.so -fPIC VFXWrapper.c LensFlare.c HighPass.c ChromaticAberration.c Utils.c
gcc -shared -o VFXLib_64.so -fPIC VFXWrapper.c LensFlare.c HighPass.c ChromaticAberration.c Utils.c
```

# Visual Effects (VFX) Plugin - Krita 4/5

Plugin to apply a host of different visual effects seen in post-processing

(Example and descriptive pictures coming eventually!)

Includes the following effects:

* Chromatic Aberration
* Bloom
* Pseudo Lens Flare
* Anamorphic Lens Flare
* Render Lens Dirt

Supports the following color modes and depths:

* **ALL** color modes in Krita (as of 5.0), RGB/Alpha, CMYK/Alpha, XYZ/Alpha, L\*a\*b\*/Alpha, Grayscale/Alpha, and YCbCr/Alpha  
* 8-bit integer/channel, 16-bit integer/channel, and 32-bit float/channel depths
  * (32-bit float will likely have unintended effects as the current implementation of the plugin tries to do a best guess of the default color space)

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

* Power - Multiplies the result by itself X times, making what would normally be very subtle colors more obvious.
* Displacement or Strength - How strong a certain stage for an effect will be, how much it will spread across the screen.
* Bilinear Interpolation - Checking this option will make the plugin run slightly slower, but will make edges created by the effect smoother and less aliased.
* Number of Worker Threads (FOR ADVANCED USERS) - As the warning says, this option is for users who know what their CPU is capable of. Larger values will apply the effect faster on very large images, but if the value exceeds the number of threads your CPU can reasonably handle the process will take longer. By default, this will be set to the optimum setting, equal to the number fo concurrent threads your CPU can handle.

Once the effect is applied it will be placed on a new layer as a modified clone of the previously selected layer, the original layer is preserved.

Use the **Help** button to see a more descriptive explination of each option.

## Planned Features

All listed below are planned to be added to this plugin at some point, no definitive time table or order yet. Check back regularly if you are interested in one or more of these features being added:

* Instant preview for any changes
* Fine tune control over filter options and the ability to manually enter values

### Extra Notes

This plugin relies on a shared C library for speeding up the computationally expensive parts. The source code for the C libraries is included in the `VFX/src` folder. The main releases have been pre-compiled for 64 bit versions of MacOS, Windows, and Linux (Ubuntu). It is recommended that you use the 64 bit version of Krita for your system. The source code can be compiled using gcc and the below commands:

```
gcc -shared -m32 -Ofast -o VFXLib_32.so -fPIC VFXWrapper.c LensDirt.c LensFlare.c HighPass.c ChromaticAberration.c Utils.c
gcc -shared -Ofast -o VFXLib_64.so -fPIC VFXWrapper.c LensDirt.c LensFlare.c HighPass.c ChromaticAberration.c Utils.c
```

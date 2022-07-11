"""
LibHandler.py
Shared library loader, handles loading the correct library for
whatever system
"""

from ctypes import *
import os
import sys

# Structures for C functions
class ColorData(Structure):
    _fields_ = [("colorModel", c_int),
                ("colorDepth", c_int)]

class Coords(Structure):
    _fields_ = [("x", c_longlong),
                ("y", c_longlong)]

class RadialFilterData(Structure):
    _fields_ = [("power", c_int),
                ("deadzone", c_int),
                ("expFalloff", c_char),
                ("biFilter", c_char)]

class LinearFilterData(Structure):
    _fields_ = [("power", c_int),
                ("direction", c_int),
                ("biFilter", c_char)]

class LensFlareFilterData(Structure):
    _fields_ = [("artifactCopies", c_int),
                ("artifactDisplacement", c_double),
                ("haloDisplacement", c_int),
                ("power", c_double),
                ("bilinearFilter", c_char)]

class LensDirtFilterData(Structure):
    _fields_ = [("size", c_int),
                ("sizeVarience", c_int),
                ("opacity", c_int),
                ("opacityVarience", c_int),
                ("shape", c_char),
                ("direction", c_int),
                ("blur", c_int)]

# Helper function to translate color model/depth into struct
def TranslateColorData(colorModel, colorDepth):
    if colorModel == "A":
        mod = 0
    elif colorModel == "RGBA":
        mod = 1
    elif colorModel == "XYZA":
        mod = 2
    elif colorModel == "LABA":
        mod = 3
    elif colorModel == "CMYKA":
        mod = 4
    elif colorModel == "GRAYA":
        mod = 5
    elif colorModel == "YCbCrA":
        mod = 6
    else:
        return None
    if colorDepth == "U8":
        depth = 0
    elif colorDepth == "U16":
        depth = 1
    elif colorDepth == "F32":
        depth == 2
    else:
        return None
    return ColorData(mod, depth)

def GetBytesPerPixel(colorSpace):
    # Let's face it, this is more interesting than a pair of if/else blocks
    channelLUT = [1,4,4,4,5,2,4]
    return (channelLUT[colorSpace.colorModel] * pow(2, colorSpace.colorDepth))

def GetSharedLibrary():
    # Determine platform
    plat = sys.platform
    if plat == "win32":
        # get windows path
        libPath = os.getenv('APPDATA')
        libPath += "\\krita\\pykrita\\VFX\\VFXLib_WIN"
    elif plat == "darwin":
        # get osx path
        libPath = os.getenv('HOME')
        libPath += "/Library/Application Support/Krita/pykrita/VFX/VFXLib_MAC"
    else:
        # get linux path
        libPath = os.getenv('HOME')
        libPath += "/.local/share/krita/pykrita/VFX/VFXLib_NIX"
    # Determine 32 or 64 bit
    if sys.maxsize < 2**32:
        libPath += "32.so"
    else:
        libPath += "64.so"
    # Load and set argtypes
    dll = CDLL(libPath)
    dll.VFXLinearAberration.argtypes = [c_longlong, c_longlong, LinearFilterData, Coords, c_void_p, c_void_p, ColorData]
    dll.VFXRadialAberration.argtypes = [c_longlong, c_longlong, RadialFilterData, Coords, c_void_p, c_void_p, ColorData]
    dll.VFXPsuedoLensFlare.argtypes = [c_longlong, c_longlong, LensFlareFilterData, Coords, c_void_p, c_void_p, ColorData]
    dll.VFXPower.argtypes = [c_longlong, c_longlong, c_int, Coords, c_void_p, c_void_p, ColorData]
    dll.VFXHighPass.argtypes = [c_longlong, c_longlong, c_int, Coords, c_void_p, c_void_p, ColorData]
    dll.VFXCreateDirtShapes.argtypes = [c_longlong, c_longlong, LensDirtFilterData, Coords, c_uint, c_void_p]
    dll.VFXRenderLensDirt.argtypes = [c_longlong, c_longlong, c_longlong, LensDirtFilterData, Coords, c_void_p, c_void_p, ColorData]
    return dll

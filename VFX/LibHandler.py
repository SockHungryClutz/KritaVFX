"""
LibHandler.py
Shared library loader, handles loading the correct library for
whatever system
"""

from ctypes import *
import os
import sys

# Structures for C functions
class Pixel(Structure):
    _fields_ = [("blue", c_ubyte),
                ("green", c_ubyte),
                ("red", c_ubyte),
                ("alpha", c_ubyte)]

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
    dll.VFXLinearAberration.argtypes = [c_longlong, c_longlong, LinearFilterData, Coords, c_void_p, c_void_p]
    dll.VFXRadialAberration.argtypes = [c_longlong, c_longlong, RadialFilterData, Coords, c_void_p, c_void_p]
    dll.VFXPsuedoLensFlare.argtypes = [c_longlong, c_longlong, LensFlareFilterData, Coords, c_void_p, c_void_p]
    dll.VFXBias.argtypes = [c_longlong, c_longlong, Pixel, Coords, c_void_p, c_void_p]
    dll.VFXPower.argtypes = [c_longlong, c_longlong, Pixel, Coords, c_void_p, c_void_p]
    dll.VFXHighPass.argtypes = [c_longlong, c_longlong, c_int, Pixel, Coords, c_void_p, c_void_p]
    return dll

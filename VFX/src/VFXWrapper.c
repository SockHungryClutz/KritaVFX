/**
 * VFXWrapper.c
 * Wrapper class to provide a single interface for VFX library
 */

#include "Utils.h"
#include "ChromaticAberration.h"
#include "HighPass.h"
#include "LensDirt.h"
#include "LensFlare.h"

void VFXLinearAberration(
    long long start,
    long long n,
    LinearFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData,
    ColorData colorData)
{
    ApplyLinearAberration(start, n, filterData, imgSize, imgData, outData, colorData);
}

void VFXRadialAberration(
    long long start,
    long long n,
    RadialFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData,
    ColorData colorData)
{
    ApplyRadialAberration(start, n, filterData, imgSize, imgData, outData, colorData);
}

void VFXPsuedoLensFlare(
    long long start,
    long long n,
    LensFlareFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData,
    ColorData colorData)
{
    ApplyPsuedoLensFlare(start, n, filterData, imgSize, imgData, outData, colorData);
}

void VFXPower(
    long long start,
    long long n,
    int power,
    Coords imgSize,
    void* imgData,
    void* outData,
    ColorData colorData)
{
    ApplyPower(start, n, power, imgSize, imgData, outData, colorData);
}

void VFXHighPass(
    long long start,
    long long n,
    int threshold,
    Coords imgSize,
    void* imgData,
    void* outData,
    ColorData colorData)
{
    ApplyHighPass(start, n, threshold, imgSize, imgData, outData, colorData);
}

void VFXCreateDirtShapes(
    long long start,
    long long n,
    LensDirtFilterData filterData,
    Coords imgSize,
    unsigned int seed,
    void* outData)
{
    CreateDirtShapes(start, n, filterData, imgSize, seed, outData);
}

void VFXRenderLensDirt(
    long long start,
    long long n,
    long long numShapes,
    LensDirtFilterData filterData,
    Coords imgSize,
    void* shapes,
    void* outData,
    ColorData colorData)
{
    RenderLensDirt(start, n, numShapes, filterData, imgSize, shapes, outData, colorData);
}

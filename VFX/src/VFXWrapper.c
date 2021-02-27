/**
 * VFXWrapper.c
 * Wrapper class to provide a single interface for VFX library
 */

#include "Utils.h"
#include "ChromaticAberration.h"
#include "LensFlare.h"
#include "HighPass.h"

void VFXLinearAberration(
    long long start,
    long long n,
    LinearFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData)
{
    ApplyLinearAberration(start, n, filterData, imgSize, imgData, outData);
}

void VFXRadialAberration(
    long long start,
    long long n,
    RadialFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData)
{
    ApplyRadialAberration(start, n, filterData, imgSize, imgData, outData);
}

void VFXPsuedoLensFlare(
    long long start,
    long long n,
    LensFlareFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData)
{
    ApplyPsuedoLensFlare(start, n, filterData, imgSize, imgData, outData);
}

void VFXPower(
    long long start,
    long long n,
    Pixel power,
    Coords imgSize,
    void* imgData,
    void* outData)
{
    ApplyPower(start, n, power, imgSize, imgData, outData);
}

void VFXBias(
    long long start,
    long long n,
    Pixel bias,
    Coords imgSize,
    void* imgData,
    void* outData)
{
    ApplyBias(start, n, bias, imgSize, imgData, outData);
}

void VFXHighPass(
    long long start,
    long long n,
    int threshold,
    Pixel bias,
    Coords imgSize,
    void* imgData,
    void* outData)
{
    ApplyHighPass(start, n, threshold, bias, imgSize, imgData, outData);
}

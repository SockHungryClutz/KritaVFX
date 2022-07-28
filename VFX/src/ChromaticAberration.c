/**
 * ChromaticAberration.c
 * Contains functions for applying chromatic aberration effects to an image
 **/

#include <stdlib.h>
#include <math.h>
#include "ChromaticAberration.h"

// Applies the effect to a single pixel
Pixel ApplyOnePixel(
    Coords xy,
    Vect2 vec,
    Coords imgSize,
    void* imgData,
    ColorData colorData,
    char interpolate)
{
    Pixel baseColor = {0, 0, 0, 0, 0};
    Pixel redChannel = {0, 0, 0, 0, 0};
    Pixel blueChannel = {0, 0, 0, 0, 0};

    baseColor = GetColorAt(xy.x, xy.y, imgSize.x, imgData, colorData);
    redChannel = SampleAt(xy.x + vec.a, xy.y + vec.b, imgSize, imgData, colorData, interpolate);
    blueChannel = SampleAt(xy.x - vec.a, xy.y - vec.b, imgSize, imgData, colorData, interpolate);
    double transparency = (baseColor.a + redChannel.a + blueChannel.a) / 3.0;

    baseColor.r = redChannel.r;
    baseColor.b = blueChannel.b;
    baseColor.a = transparency;

    return baseColor;
}

// Applies a linear aberration over a set of n pixels
// where n <= imgwidth * imgheight
// outData must be allocated by the caller
void ApplyLinearAberration(
    long long start,
    long long n,
    LinearFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData,
    ColorData colorData)
{
    // Calculate vector to use for every pixel
    Vect2 vec;
    double rad = DegreeToRadian(filterData.direction);
    vec.a = -1 * sin(rad);
    vec.b = cos(rad);
    vec = ScaleVect2(vec, filterData.power);

    // Iterate over range of pixels, applying effect for each
    long long x = start % imgSize.x;
    long long y = start / imgSize.x;
    for (long long i = start; i < start + n; i++)
    {
        // Build coordinates
        Coords xy;
        xy.x = x;
        xy.y = y;

        // Allocate output vector
        Pixel outVec = {0, 0, 0, 0, 0};

        // Do the thing
        outVec = ApplyOnePixel(xy, vec, imgSize, imgData, colorData, filterData.biFilter);
        // There's no way this could happen, but just in case...
        outVec = ClampToColorSpace(outVec, colorData);
        WritePixel(i, outVec, outData, colorData);

        // Increment x
        x++;
        // Bounds checking
        if (x >= imgSize.x)
        {
            x = 0;
            y++;
        }
        if (y >= imgSize.y) break;
    }
}

// Applies a radial aberration over n pixels
void ApplyRadialAberration(
    long long start,
    long long n,
    RadialFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData,
    ColorData colorData)
{
    long long x = start % imgSize.x;
    long long y = start / imgSize.x;

    Vect2 center;
    center.a = (imgSize.x - 1) / 2;
    center.b = (imgSize.y - 1) / 2;
    for (long long i = start; i < start + n; i++)
    {
        Vect2 displace;
        displace.a = x - center.a;
        displace.b = y - center.b;

        // Normalize and check deadzone
        displace = ScaleVect2(displace, 1.0 / LenVect(center));
        double deadZone = filterData.deadzone;
        deadZone /= 100.0;
        if (LenVect(displace) < deadZone)
        {
            Pixel baseColor = {0, 0, 0, 0, 0};
            baseColor = GetColorAt(x, y, imgSize.x, imgData, colorData);
            WritePixel(i, baseColor, outData, colorData);
        }
        else
        {
            // Scale vector from 0 at edge of deadzone to 1 at corner of image
            displace = ScaleVect2(displace, (LenVect(displace) - deadZone) * (1.0 / 1.0-deadZone));
            if (filterData.expFalloff != 0)
            {
                // Effectively square if using exponential falloff
                displace = ScaleVect2(displace, LenVect(displace));
            }
            // Scale final result by power
            displace = ScaleVect2(displace, filterData.power);

            Coords xy;
            xy.x = x;
            xy.y = y;
            Pixel outVec = {0, 0, 0, 0, 0};

            // Do the thing
            outVec = ApplyOnePixel(xy, displace, imgSize, imgData, colorData, filterData.biFilter);
            // There's no way this could happen, but just in case...
            outVec = ClampToColorSpace(outVec, colorData);
            WritePixel(i, outVec, outData, colorData);
        }

        x++;
        // Bounds checking
        if (x >= imgSize.x)
        {
            x = 0;
            y++;
        }
        if (y >= imgSize.y) break;
    }
}

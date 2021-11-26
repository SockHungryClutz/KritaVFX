/**
 * ChromaticAberration.c
 * Contains functions for applying chromatic aberration effects to an image
 **/

#include <stdlib.h>
#include <math.h>
#include "ChromaticAberration.h"

// Applies the effect to a single pixel
Vect4 ApplyOnePixel(
    Coords xy,
    Vect2 vec,
    Coords imgSize,
    Pixel* imgData,
    char interpolate)
{
    Vect4 baseColor;
    Vect4 redChannel;
    Vect4 blueChannel;

    baseColor = GetColorAt(xy.x, xy.y, imgSize.x, imgData);
    redChannel = SampleAt(xy.x + vec.a, xy.y + vec.b, imgSize, imgData, interpolate);
    blueChannel = SampleAt(xy.x - vec.a, xy.y - vec.b, imgSize, imgData, interpolate);
    double transparency = (baseColor.d + redChannel.d + blueChannel.d) / 3;

    Vect4 out;
    out.a = redChannel.a;
    out.b = baseColor.b;
    out.c = blueChannel.c;
    out.d = transparency;
    return out;
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
    void* outData)
{
    Pixel* pixelData = (Pixel*)imgData;
    Pixel* pixelOut = (Pixel*)outData;

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
        // Bounds checking
        if (x >= imgSize.x)
        {
            x = 0;
            y++;
        }
        if (y >= imgSize.y) break;

        // Build coordinates
        Coords xy;
        xy.x = x;
        xy.y = y;

        // Allocate output vector
        Vect4 outVec;

        // Do the thing
        outVec = ApplyOnePixel(xy, vec, imgSize, pixelData, filterData.biFilter);
        // There's no way this could happen, but just in case...
        ClampVect4(outVec);
        pixelOut[i].blue = (unsigned int)outVec.a;
        pixelOut[i].green = (unsigned int)outVec.b;
        pixelOut[i].red = (unsigned int)outVec.c;
        pixelOut[i].alpha = (unsigned int)outVec.d;

        // Increment x
        x++;
    }
}

// Applies a radial aberration over n pixels
void ApplyRadialAberration(
    long long start,
    long long n,
    RadialFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData)
{
    Pixel* pixelData = (Pixel*)imgData;
    Pixel* pixelOut = (Pixel*)outData;

    long long x = start % imgSize.x;
    long long y = start / imgSize.x;

    Vect2 center;
    center.a = (imgSize.x - 1) / 2;
    center.b = (imgSize.y - 1) / 2;
    for (long long i = start; i < start + n; i++)
    {
        // Bounds checking
        if (x >= imgSize.x)
        {
            x = 0;
            y++;
        }
        if (y >= imgSize.y) break;

        Vect2 displace;
        displace.a = x - center.a;
        displace.b = y - center.b;

        // Normalize and check deadzone
        displace = ScaleVect2(displace, 1.0 / LenVect(center));
        double deadZone = filterData.deadzone;
        deadZone /= 100.0;
        if (LenVect(displace) < deadZone)
        {
            Vect4 baseColor;
            baseColor = GetColorAt(x, y, imgSize.x, imgData);
            pixelOut[i].blue = (unsigned int)baseColor.a;
            pixelOut[i].green = (unsigned int)baseColor.b;
            pixelOut[i].red = (unsigned int)baseColor.c;
            pixelOut[i].alpha = (unsigned int)baseColor.d;
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
            Vect4 outVec;

            // Do the thing
            outVec = ApplyOnePixel(xy, displace, imgSize, pixelData, filterData.biFilter);
            // There's no way this could happen, but just in case...
            ClampVect4(outVec);
            pixelOut[i].blue = (unsigned int)outVec.a;
            pixelOut[i].green = (unsigned int)outVec.b;
            pixelOut[i].red = (unsigned int)outVec.c;
            pixelOut[i].alpha = (unsigned int)outVec.d;
        }

        x++;
    }
}

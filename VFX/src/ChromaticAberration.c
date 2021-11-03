/**
 * ChromaticAberration.c
 * Contains functions for applying chromatic aberration effects to an image
 **/

#include <stdlib.h>
#include <math.h>
#include "ChromaticAberration.h"

// Applies the effect to a single pixel
void ApplyOnePixel(
    Coords xy,
    double* vec,
    Coords imgSize,
    Pixel* imgData,
    char interpolate,
    double* out)
{
    double baseColor[4];
    double redChannel[4];
    double blueChannel[4];
    double vecCoords[2];
    double negativeVec[2];

    GetColorAt(xy.x, xy.y, imgSize.x, imgData, baseColor);
    SampleAt(xy.x + vec[0], xy.y + vec[1], imgSize, imgData, interpolate, redChannel);
    SampleAt(xy.x - vec[0], xy.y - vec[1], imgSize, imgData, interpolate, blueChannel);
    double transparency = (baseColor[3] + redChannel[3] + blueChannel[3]) / 3;

    out[0] = redChannel[0];
    out[1] = baseColor[1];
    out[2] = blueChannel[2];
    out[3] = transparency;
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
    double vec[2];
    double rad = DegreeToRadian(filterData.direction);
    vec[0] = -1 * sin(rad);
    vec[1] = cos(rad);
    ScaleVect2(vec, filterData.power, vec);

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
        double outVec[4];

        // Do the thing
        ApplyOnePixel(xy, vec, imgSize, pixelData, filterData.biFilter, outVec);
        // There's no way this could happen, but just in case...
        ClampVect4(outVec);
        pixelOut[i].blue = (unsigned int)outVec[0];
        pixelOut[i].green = (unsigned int)outVec[1];
        pixelOut[i].red = (unsigned int)outVec[2];
        pixelOut[i].alpha = (unsigned int)outVec[3];

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

    double center[2];
    center[0] = (imgSize.x - 1) / 2;
    center[1] = (imgSize.y - 1) / 2;
    for (long long i = start; i < start + n; i++)
    {
        // Bounds checking
        if (x >= imgSize.x)
        {
            x = 0;
            y++;
        }
        if (y >= imgSize.y) break;

        double displace[2];
        displace[0] = x - center[0];
        displace[1] = y - center[1];

        // Normalize and check deadzone
        ScaleVect2(displace, 1.0 / LenVect(center), displace);
        double deadZone = filterData.deadzone;
        deadZone /= 100.0;
        if (LenVect(displace) < deadZone)
        {
            double baseColor[4];
            GetColorAt(x, y, imgSize.x, imgData, baseColor);
            pixelOut[i].blue = (unsigned int)baseColor[0];
            pixelOut[i].green = (unsigned int)baseColor[1];
            pixelOut[i].red = (unsigned int)baseColor[2];
            pixelOut[i].alpha = (unsigned int)baseColor[3];
        }
        else
        {
            // Scale vector from 0 at edge of deadzone to 1 at corner of image
            ScaleVect2(displace, (LenVect(displace) - deadZone) * (1.0 / 1.0-deadZone), displace);
            if (filterData.expFalloff != 0)
            {
                // Effectively square if using exponential falloff
                ScaleVect2(displace, LenVect(displace), displace);
            }
            // Scale final result by power
            ScaleVect2(displace, filterData.power, displace);

            Coords xy;
            xy.x = x;
            xy.y = y;
            double outVec[4];

            // Do the thing
            ApplyOnePixel(xy, displace, imgSize, pixelData, filterData.biFilter, outVec);
            // There's no way this could happen, but just in case...
            ClampVect4(outVec);
            pixelOut[i].blue = (unsigned int)outVec[0];
            pixelOut[i].green = (unsigned int)outVec[1];
            pixelOut[i].red = (unsigned int)outVec[2];
            pixelOut[i].alpha = (unsigned int)outVec[3];
        }

        x++;
    }
}

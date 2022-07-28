/**
 * HighPass.c
 * Apply a simple highpass filter (not gaussian)
 **/

#include <stdlib.h>
#include "HighPass.h"

void ApplyPower(
    long long start,
    long long n,
    int power,
    Coords imgSize,
    void* imgData,
    void* outData,
    ColorData colorData)
{
    for (long long i = start; i < start + n; i++)
    {
        Pixel outColor = GetColorAtIdx(i, imgSize.x, imgData, colorData);
        outColor = ScalePixel(outColor, power);
        outColor = ClampToColorSpace(outColor, colorData);
        WritePixel(i, outColor, outData, colorData);
    }
}

void ApplyHighPass(
    long long start,
    long long n,
    int threshold,
    Coords imgSize,
    void* imgData,
    void* outData,
    ColorData colorData)
{
    Pixel outVec = {0, 0, 0, 0, 0};
    double max = GetColorSpaceMax(colorData);
    double scaledThresh = ((double)threshold / 255.0) * max;
    double scale = max / ((max + 1) - scaledThresh);
    double halfThresh = scaledThresh / 2.0;
    Pixel threshVect = {scaledThresh, scaledThresh, scaledThresh, scaledThresh, 0};
    Pixel halfThreshVect = {halfThresh, halfThresh, halfThresh, halfThresh, 0};

    for (long long i = start; i < start + n; i++)
    {
        // nothing technical, subtract threshold from each color channel,
        // scale, clamp, then write to output
        Pixel originalVect = GetColorAtIdx(i, imgSize.x, imgData, colorData);
        switch (colorData.colorModel)
        {
            case CMYKA:
                outVec = AddPixel(originalVect, threshVect);
            case RGBA:
            case XYZA:
            case GRAYA:
                outVec = SubPixel(originalVect, threshVect);
                outVec = ScalePixel(outVec, scale);
                break;
            case LABA:
            case YCbCrA:
                outVec = ScalePixel(originalVect, scaledThresh);
                outVec = AddPixel(outVec, halfThreshVect);
                outVec.l = (originalVect.l - scaledThresh) * scale;
                break;
            default:
                break;
        }
        outVec.a = originalVect.a;
        outVec = ClampToColorSpace(outVec, colorData);
        WritePixel(i, outVec, outData, colorData);
    }
}

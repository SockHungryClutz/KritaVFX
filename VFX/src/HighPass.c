/**
 * HighPass.c
 * Apply a simple highpass filter (not gaussian)
 **/

#include <stdlib.h>
#include "HighPass.h"

void ApplyPowerOnePixel(
    Pixel power,
    Pixel* inColor,
    Pixel* outColor)
{
    double outVec[3];
    outVec[0] = inColor->blue * power.blue;
    outVec[1] = inColor->green * power.green;
    outVec[2] = inColor->red * power.red;
    if (outVec[0] < 0) outVec[0] = 0;
    else if (outVec[0] > 255) outVec[0] = 255;
    if (outVec[1] < 0) outVec[1] = 0;
    else if (outVec[1] > 255) outVec[1] = 255;
    if (outVec[2] < 0) outVec[2] = 0;
    else if (outVec[2] > 255) outVec[2] = 255;
    outColor->blue = (unsigned char)outVec[0];
    outColor->green = (unsigned char)outVec[1];
    outColor->red = (unsigned char)outVec[2];
    outColor->alpha = inColor->alpha;
}

void ApplyPower(
    long long start,
    long long n,
    Pixel power,
    Coords imgSize,
    void* imgData,
    void* outData)
{
    Pixel* pixelData = (Pixel*)imgData;
    Pixel* pixelOutData = (Pixel*)outData;

    for (long long i = start; i < start + n; i++)
    {
        ApplyPowerOnePixel(power, &(pixelData[i]), &(pixelOutData[i]));
    }
}

void ApplyHighPass(
    long long start,
    long long n,
    int threshold,
    Coords imgSize,
    void* imgData,
    void* outData)
{
    Pixel* pixelData = (Pixel*)imgData;
    Pixel* pixelOutData = (Pixel*)outData;
    double outVec[3];
    double scale = 255 / (256 - threshold);

    for (long long i = start; i < start + n; i++)
    {
        // nothing technical, subtract threshold from each color channel,
        // scale, clamp, then write to output
        outVec[0] = (pixelData[i].blue - threshold) * scale;
        outVec[1] = (pixelData[i].green - threshold) * scale;
        outVec[2] = (pixelData[i].red - threshold) * scale;
        if (outVec[0] < 0) outVec[0] = 0;
        else if (outVec[0] > 255) outVec[0] = 255;
        if (outVec[1] < 0) outVec[1] = 0;
        else if (outVec[1] > 255) outVec[1] = 255;
        if (outVec[2] < 0) outVec[2] = 0;
        else if (outVec[2] > 255) outVec[2] = 255;
        pixelOutData[i].blue = (unsigned char)outVec[0];
        pixelOutData[i].green = (unsigned char)outVec[1];
        pixelOutData[i].red = (unsigned char)outVec[2];
        // TODO: should this always be 255? maybe parameterize?
        pixelOutData[i].alpha = pixelData[i].alpha;
    }
}

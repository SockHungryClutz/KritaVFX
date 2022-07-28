/**
 * Utils.c
 * Common utility functions for vector math and pixel sampling
 */

#include <stdlib.h>
#include <math.h>
#include "Utils.h"

/** 
 * Python ctypes states that any memory allocated in the C library must be
 * freed by the C library. As such, no dynamic memory allocation occurs here.
 * Only automatic allocation that is freed when out of scope. 
 **/

// Scale a 2 dimensional vector
Vect2 ScaleVect2(Vect2 vec, double scalar)
{
    Vect2 out = {0, 0};
    out.a = vec.a * scalar;
    out.b = vec.b * scalar;
    return out;
}

// Scale a 5 dimensional vector
Pixel ScalePixel(Pixel pix, double scalar)
{
    Pixel out = {0, 0, 0, 0, 0};
    out.r = pix.r * scalar;
    out.b = pix.b * scalar;
    out.o = pix.o * scalar;
    out.l = pix.l * scalar;
    out.a = pix.a * scalar;
    return out;
}

// Sum two 2 dimensional vectors
Vect2 AddVect2(Vect2 vec1, Vect2 vec2)
{
    Vect2 out = {0, 0};
    out.a = vec1.a + vec2.a;
    out.b = vec1.b + vec2.b;
    return out;
}

// Sum two 5 dimensional vectors
Pixel AddPixel(Pixel pix1, Pixel pix2)
{
    Pixel out = {0, 0, 0, 0, 0};
    out.r = pix1.r + pix2.r;
    out.b = pix1.b + pix2.b;
    out.o = pix1.o + pix2.o;
    out.l = pix1.l + pix2.l;
    out.a = pix1.a + pix2.a;
    return out;
}

// Subtract two 2 dimensional vectors
Vect2 SubVect2(Vect2 vec1, Vect2 vec2)
{
    Vect2 out = {0, 0};
    out.a = vec1.a - vec2.a;
    out.b = vec1.b - vec2.b;
    return out;
}

// Subtract two 5 dimensional vectors
Pixel SubPixel(Pixel pix1, Pixel pix2)
{
    Pixel out = {0, 0, 0, 0, 0};
    if (pix1.r > pix2.r) out.r = pix1.r - pix2.r;
    if (pix1.b > pix2.b) out.b = pix1.b - pix2.b;
    if (pix1.o > pix2.o) out.o = pix1.o - pix2.o;
    if (pix1.l > pix2.l) out.l = pix1.l - pix2.l;
    if (pix1.a > pix2.a) out.a = pix1.a - pix2.a;
    return out;
}

// Calculates the length of a 2 dimensional vector
double LenVect(Vect2 vec)
{
    return sqrt(pow(vec.a, 2) + pow(vec.b, 2));
}

// Possibly other functions here? Unitize, etc?

double DegreeToRadian(double deg)
{
    return deg * (acos(-1) / 180.0);
}

double Max(double a, double b)
{
    if (a >= b)
    {
        return a;
    }
    else
    {
        return b;
    }
}

// Return the number of channels used for a color model
int GetNumChannels(ColorModel colorModel)
{
    switch (colorModel)
    {
        case A:
            return 1;
        case GRAYA:
            return 2;
        case RGBA:
        case XYZA:
        case LABA:
        case YCbCrA:
            return 4;
        case CMYKA:
            return 5;
        default:
            // Unknown color model
            return 0;
    };
}

// Returns the color at a certain point in the image data
Pixel GetColorAt(
    long long x,
    long long y,
    long long imgWidth,
    void* imgData,
    ColorData colorData)
{
    long long idx = (y * imgWidth) + x;
    return GetColorAtIdx(idx, imgWidth, imgData, colorData);
}

// Returns the color at a certain index in the image data
Pixel GetColorAtIdx(
    long long idx,
    long long imgWidth,
    void* imgData,
    ColorData colorData)
{
    Pixel scratch = {0, 0, 0, 0, 0};
    int numChannels = GetNumChannels(colorData.colorModel);
    unsigned char* uCharData = (unsigned char*)imgData;
    unsigned short* uShortData = (unsigned short*)imgData;
    float* floatData = (float*)imgData;
    long long index = idx * GetNumChannels(colorData.colorModel);
    switch (colorData.colorDepth)
    {
        case U8:
            if (numChannels >= 1) {scratch.r = (double)uCharData[index];}
            if (numChannels >= 2) {scratch.b = (double)uCharData[index + 1];}
            if (numChannels >= 4) {scratch.o = (double)uCharData[index + 2];
                                   scratch.l = (double)uCharData[index + 3];}
            if (numChannels == 5) {scratch.a = (double)uCharData[index + 4];}
            break;
        case U16:
            if (numChannels >= 1) {scratch.r = (double)uShortData[index];}
            if (numChannels >= 2) {scratch.b = (double)uShortData[index + 1];}
            if (numChannels >= 4) {scratch.o = (double)uShortData[index + 2];
                                   scratch.l = (double)uShortData[index + 3];}
            if (numChannels == 5) {scratch.a = (double)uShortData[index + 4];}
            break;
        case F32:
            if (numChannels >= 1) {scratch.r = (double)floatData[index];}
            if (numChannels >= 2) {scratch.b = (double)floatData[index + 1];}
            if (numChannels >= 4) {scratch.o = (double)floatData[index + 2];
                                   scratch.l = (double)floatData[index + 3];}
            if (numChannels == 5) {scratch.a = (double)floatData[index + 4];}
            break;
        default:
            // Unknown color depth, do not convert anything
            break;
    }
    // Arrange the data into the correct channels
    Pixel out = {0, 0, 0, 0, 0};
    switch (colorData.colorModel)
    {
        case A:
            out.a = scratch.r;
            break;
        case RGBA:
            // Order = RGBA if float, BGRA if int
            if (colorData.colorDepth != F32)
            {
                out.b = scratch.r;
                out.o = scratch.b;
                out.r = scratch.o;
                out.a = scratch.l;
                break;
            }
        case XYZA:
            out.r = scratch.r;
            out.o = scratch.b;
            out.b = scratch.o;
            out.a = scratch.l;
            break;
        case LABA:
            out.l = scratch.r;
            out.r = scratch.b;
            out.b = scratch.o;
            out.a = scratch.l;
            break;
        case CMYKA:
            out.b = scratch.r;
            out.r = scratch.b;
            out.o = scratch.o;
            out.l = scratch.l;
            out.a = scratch.a;
        case GRAYA:
            out.l = scratch.r;
            out.a = scratch.b;
            break;
        case YCbCrA:
            out.l = scratch.r;
            out.b = scratch.b;
            out.r = scratch.o;
            out.a = scratch.l;
            break;
        default:
            // Unknown color model
            break;
    }
    return out;
}

// Get a sample at the specified coordinates
// Performs bounds clamping and bilinear interpolation
Pixel SampleAt(
    double x,
    double y,
    Coords imgSize,
    void* imgData,
    ColorData colorData,
    char interpolate)
{
    double realX = x;
    double realY = y;
    // Clamp x and y coordinates to image size
    if (x >= imgSize.x) { realX = imgSize.x - 1; }
    else if (x < 0)    { realX = 0; }
    if (y >= imgSize.y) { realY = imgSize.y - 1; }
    else if (y < 0)    { realY = 0; }

    // Get offset from exact pixels
    Pixel baseColor = {0, 0, 0, 0, 0};
    Coords xy;
    xy.x = (long long)floor(realX);
    xy.y = (long long)floor(realY);
    realX = (realX - xy.x);
    realY = (realY - xy.y);
    baseColor = GetColorAt(xy.x, xy.y, imgSize.x, imgData, colorData);
    if (interpolate != 0)
    {
        // Blend colors using linear interpolation
        if (realY > 0.00001 && xy.y < imgSize.y - 1)
        {
            Pixel mixcolor1 = {0, 0, 0, 0, 0};
            mixcolor1 = GetColorAt(xy.x, xy.y + 1, imgSize.x, imgData, colorData);
            baseColor = ScalePixel(baseColor, 1.0 - realY);
            mixcolor1 = ScalePixel(mixcolor1, realY);
            baseColor = AddPixel(baseColor, mixcolor1);
        }
        if (realX > 0.00001 && xy.x < imgSize.x - 1)
        {
            Pixel mixcolor2 = {0, 0, 0, 0, 0};
            mixcolor2 = GetColorAt(xy.x + 1, xy.y, imgSize.x, imgData, colorData);
            if (realY > 0.00001 && xy.y < imgSize.y - 1)
            {
                Pixel mixcolor3 = {0, 0, 0, 0, 0};
                mixcolor3 = GetColorAt(xy.x + 1, xy.y + 1, imgSize.x, imgData, colorData);
                mixcolor2 = ScalePixel(mixcolor2, 1.0 - realY);
                mixcolor3 = ScalePixel(mixcolor3, realY);
                mixcolor2 = AddPixel(mixcolor2, mixcolor3);
            }
            baseColor = ScalePixel(baseColor, 1.0 - realX);
            mixcolor2 = ScalePixel(mixcolor2, realX);
            baseColor = AddPixel(baseColor, mixcolor2);
        }
    }
    return baseColor;
}

// Writes a pixel to the output buffer
void WritePixel(
    long long idx,
    Pixel pixelOut,
    void* outData,
    ColorData colorData)
{
    int numChannels = 0;
    // Arrange the data before writing. Also get number of channels to avoid
    // excess comparisons/switch statements
    Pixel scratch = {0, 0, 0, 0, 0};
    unsigned char* uCharData = (unsigned char*)outData;
    unsigned short* uShortData = (unsigned short*)outData;
    float* floatData = (float*)outData;
    long long index = idx * GetNumChannels(colorData.colorModel);
    switch (colorData.colorModel)
    {
        case A:
            scratch.r = pixelOut.a;
            numChannels = 1;
            break;
        case RGBA:
            // Order = RGBA if float, BGRA if int
            if (colorData.colorDepth != F32)
            {
                scratch.r = pixelOut.b;
                scratch.b = pixelOut.o;
                scratch.o = pixelOut.r;
                scratch.l = pixelOut.a;
                numChannels = 4;
                break;
            }
        case XYZA:
            scratch.r = pixelOut.r;
            scratch.b = pixelOut.o;
            scratch.o = pixelOut.b;
            scratch.l = pixelOut.a;
            numChannels = 4;
            break;
        case LABA:
            scratch.r = pixelOut.l;
            scratch.b = pixelOut.r;
            scratch.o = pixelOut.b;
            scratch.l = pixelOut.a;
            numChannels = 4;
            break;
        case CMYKA:
            scratch.r = pixelOut.b;
            scratch.b = pixelOut.r;
            scratch.o = pixelOut.o;
            scratch.l = pixelOut.l;
            scratch.a = pixelOut.a;
            numChannels = 5;
            break;
        case GRAYA:
            scratch.r = pixelOut.l;
            scratch.b = pixelOut.a;
            numChannels = 2;
            break;
        case YCbCrA:
            scratch.r = pixelOut.l;
            scratch.b = pixelOut.b;
            scratch.o = pixelOut.r;
            scratch.l = pixelOut.a;
            numChannels = 4;
            break;
        default:
            // Unknown color model
            break;
    }
    switch (colorData.colorDepth)
    {
        case U8:
            if (numChannels >= 1) {uCharData[index]     = (unsigned char)scratch.r;}
            if (numChannels >= 2) {uCharData[index + 1] = (unsigned char)scratch.b;}
            if (numChannels >= 4) {uCharData[index + 2] = (unsigned char)scratch.o;
                                   uCharData[index + 3] = (unsigned char)scratch.l;}
            if (numChannels == 5) {uCharData[index + 4] = (unsigned char)scratch.a;}
            break;
        case U16:
            if (numChannels >= 1) {uShortData[index]     = (unsigned short)scratch.r;}
            if (numChannels >= 2) {uShortData[index + 1] = (unsigned short)scratch.b;}
            if (numChannels >= 4) {uShortData[index + 2] = (unsigned short)scratch.o;
                                   uShortData[index + 3] = (unsigned short)scratch.l;}
            if (numChannels == 5) {uShortData[index + 4] = (unsigned short)scratch.a;}
            break;
        case F32:
            if (numChannels >= 1) {floatData[index]     = (float)scratch.r;}
            if (numChannels >= 2) {floatData[index + 1] = (float)scratch.b;}
            if (numChannels >= 4) {floatData[index + 2] = (float)scratch.o;
                                   floatData[index + 3] = (float)scratch.l;}
            if (numChannels == 5) {floatData[index + 4] = (float)scratch.a;}
            break;
        default:
            // Unknown color depth, do not write anything
            break;
    }
}

// Guess the maximum value for a color space
double GetColorSpaceMax(ColorData colorData)
{
    switch (colorData.colorDepth)
    {
        case U8:
            return 255;
        case U16:
            return 65535;
        case F32:
            // Here is where it becomes guesswork
            // For some color profiles, it's 0-1
            // For others it goes to some arbitrary number that's channel dependant
            // If the color model is commonly 0-1, return 1
            // Otherwise return 255. This is more than enough for all the default
            // color spaces. Krita will hopefully cap the values to the space)
            // I could code this to follow most of the defaults, but
            // people can always put in custom color profiles
            switch (colorData.colorModel)
            {
                case A:
                case RGBA:
                case GRAYA:
                    return 1;
                case CMYKA:
                case LABA:
                case XYZA:
                case YCbCrA:
                default:
                    return 255;
            }
        default:
            return 0;
    }
}

// Clamp a vector to the current color space
Pixel ClampToColorSpace(Pixel pix, ColorData colorData)
{
    Pixel out = {pix.r,pix.b,pix.o,pix.l,pix.a};
    double max = GetColorSpaceMax(colorData);
    if (out.r < 0) out.r = 0;
    else if (out.r > max) out.r = max;
    if (out.b < 0) out.b = 0;
    else if (out.b > max) out.b = max;
    if (out.o < 0) out.o = 0;
    else if (out.o > max) out.o = max;
    if (out.l < 0) out.l = 0;
    else if (out.l > max) out.l = max;
    if (out.a < 0) out.a = 0;
    else if (out.a > max) out.a = max;
    return out;
}

/**
 * Utils.c
 * Common utility functions for vector math and pixel sampling
 */

#include <stdlib.h>
#include <math.h>
#include "Utils.h"

/**
 *  TODO:
 * add a header file with different color modes and color-to-double conversion
 * possibly also how to handle each color type?
 */ 

/** 
 * Python ctypes states that any memory allocated in the C library must be
 * freed by the C library. I've accepted this by allocating no dynamic memory.
 * Memory is only allocated on the stack for as much as the function needs,
 * then is discarded when the function exits automatically. As such all returns
 * are in parameters passed by reference which the C functions modify.
 * No return types, although they may be used for errors, but I assume only I
 * will be using this library and make no coding mistakes...
 **/

// Scale a 2 dimensional vector
void ScaleVect2(double* vec, double scalar, double* out)
{
    out[0] = vec[0] * scalar;
    out[1] = vec[1] * scalar;
}

// Scale a 4 dimensional vector
void ScaleVect4(double* vec, double scalar, double* out)
{
    out[0] = vec[0] * scalar;
    out[1] = vec[1] * scalar;
    out[2] = vec[2] * scalar;
    out[3] = vec[3] * scalar;
}

// Sum two 2 dimensional vectors
void AddVect2(double* vec1, double* vec2, double* out)
{
    out[0] = vec1[0] + vec2[0];
    out[1] = vec1[1] + vec2[1];
}

// Sum two 4 dimensional vectors
void AddVect4(double* vec1, double* vec2, double* out)
{
    out[0] = vec1[0] + vec2[0];
    out[1] = vec1[1] + vec2[1];
    out[2] = vec1[2] + vec2[2];
    out[3] = vec1[3] + vec2[3];
}

// Subtract two 2 dimensional vectors
void SubVect2(double* vec1, double* vec2, double* out)
{
    out[0] = vec1[0] - vec2[0];
    out[1] = vec1[1] - vec2[1];
}

// Subtract two 4 dimensional vectors
void SubVect4(double* vec1, double* vec2, double* out)
{
    out[0] = vec1[0] - vec2[0];
    out[1] = vec1[1] - vec2[1];
    out[2] = vec1[2] - vec2[2];
    out[3] = vec1[3] - vec2[3];
}

// Calculates the length of a 2 dimensional vector
double LenVect(double* vec)
{
    return sqrt(pow(vec[0], 2) + pow(vec[1], 2));
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

// Returns the color at a certain point in the image data
void GetColorAt(
    long long x,
    long long y,
    long long imgWidth,
    Pixel* imgData,
    double* out)
{
    Pixel sample = imgData[(y * imgWidth) + x];
    out[0] = sample.blue;
    out[1] = sample.green;
    out[2] = sample.red;
    out[3] = sample.alpha;
}

// Get a sample at the specified coordinates
// Performs bounds clamping and bilinear interpolation
void SampleAt(
    double x,
    double y,
    Coords imgSize,
    Pixel* imgData,
    char interpolate,
    double* out)
{
    double realX = x;
    double realY = y;
    // Clamp x and y coordinates to image size
    if (x >= imgSize.x) { realX = imgSize.x - 1; }
    else if (x < 0)    { realX = 0; }
    if (y >= imgSize.y) { realY = imgSize.y - 1; }
    else if (y < 0)    { realY = 0; }

    // Get offset from exact pixels
    double baseColor[4];
    Coords xy;
    xy.x = (long long)floor(realX);
    xy.y = (long long)floor(realY);
    realX = (realX - xy.x);
    realY = (realY - xy.y);
    GetColorAt(xy.x, xy.y, imgSize.x, imgData, baseColor);

    if (interpolate != 0)
    {
        // Blend colors using linear interpolation
        if (realY > 0.00001 && xy.y < imgSize.y - 1)
        {
            double mixcolor1[4];
            GetColorAt(xy.x, xy.y + 1, imgSize.x, imgData, mixcolor1);
            ScaleVect4(baseColor, 1.0 - realY, baseColor);
            ScaleVect4(mixcolor1, realY, mixcolor1);
            AddVect4(baseColor, mixcolor1, baseColor);
        }
        if (realX > 0.00001 && xy.x < imgSize.x - 1)
        {
            double mixcolor2[4];
            GetColorAt(xy.x + 1, xy.y, imgSize.x, imgData, mixcolor2);
            if (realY > 0.00001 && xy.y < imgSize.y - 1)
            {
                double mixcolor3[4];
                GetColorAt(xy.x + 1, xy.y + 1, imgSize.x, imgData, mixcolor3);
                ScaleVect4(mixcolor2, 1.0 - realY, mixcolor2);
                ScaleVect4(mixcolor3, realY, mixcolor3);
                AddVect4(mixcolor2, mixcolor3, mixcolor2);
            }
            ScaleVect4(baseColor, 1.0 - realX, baseColor);
            ScaleVect4(mixcolor2, realX, mixcolor2);
            AddVect4(baseColor, mixcolor2, baseColor);
        }
    }

    // Deep copy of final output
    out[0] = baseColor[0];
    out[1] = baseColor[1];
    out[2] = baseColor[2];
    out[3] = baseColor[3];
}

// Clamp a vector to standard 8 bit values
void ClampVect4(double* vec)
{
    if (vec[0] < 0) vec[0] = 0;
    else if (vec[0] > 255) vec[0] = 255;
    if (vec[1] < 0) vec[1] = 0;
    else if (vec[1] > 255) vec[1] = 255;
    if (vec[2] < 0) vec[2] = 0;
    else if (vec[2] > 255) vec[2] = 255;
    if (vec[3] < 0) vec[3] = 0;
    else if (vec[3] > 255) vec[3] = 255;
}

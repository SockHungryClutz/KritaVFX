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
    Vect2 out;
    out.a = vec.a * scalar;
    out.b = vec.b * scalar;
    return out;
}

// Scale a 4 dimensional vector
Vect4 ScaleVect4(Vect4 vec, double scalar)
{
    Vect4 out;
    out.a = vec.a * scalar;
    out.b = vec.b * scalar;
    out.c = vec.c * scalar;
    out.d = vec.d * scalar;
    return out;
}

// Sum two 2 dimensional vectors
Vect2 AddVect2(Vect2 vec1, Vect2 vec2)
{
    Vect2 out;
    out.a = vec1.a + vec2.a;
    out.b = vec1.b + vec2.b;
    return out;
}

// Sum two 4 dimensional vectors
Vect4 AddVect4(Vect4 vec1, Vect4 vec2)
{
    Vect4 out;
    out.a = vec1.a + vec2.a;
    out.b = vec1.b + vec2.b;
    out.c = vec1.c + vec2.c;
    out.d = vec1.d + vec2.d;
    return out;
}

// Subtract two 2 dimensional vectors
Vect2 SubVect2(Vect2 vec1, Vect2 vec2)
{
    Vect2 out;
    out.a = vec1.a - vec2.a;
    out.b = vec1.b - vec2.b;
    return out;
}

// Subtract two 4 dimensional vectors
Vect4 SubVect4(Vect4 vec1, Vect4 vec2)
{
    Vect4 out;
    out.a = vec1.a - vec2.a;
    out.b = vec1.b - vec2.b;
    out.c = vec1.c - vec2.c;
    out.d = vec1.d - vec2.d;
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

// Returns the color at a certain point in the image data
Vect4 GetColorAt(
    long long x,
    long long y,
    long long imgWidth,
    Pixel* imgData)
{
    Pixel sample = imgData[(y * imgWidth) + x];
    Vect4 out;
    out.a = sample.blue;
    out.b = sample.green;
    out.c = sample.red;
    out.d = sample.alpha;
    return out;
}

// Get a sample at the specified coordinates
// Performs bounds clamping and bilinear interpolation
Vect4 SampleAt(
    double x,
    double y,
    Coords imgSize,
    Pixel* imgData,
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
    Vect4 baseColor;
    Coords xy;
    xy.x = (long long)floor(realX);
    xy.y = (long long)floor(realY);
    realX = (realX - xy.x);
    realY = (realY - xy.y);
    baseColor = GetColorAt(xy.x, xy.y, imgSize.x, imgData);
    if (interpolate != 0)
    {
        // Blend colors using linear interpolation
        if (realY > 0.00001 && xy.y < imgSize.y - 1)
        {
            Vect4 mixcolor1;
            mixcolor1 = GetColorAt(xy.x, xy.y + 1, imgSize.x, imgData);
            baseColor = ScaleVect4(baseColor, 1.0 - realY);
            mixcolor1 = ScaleVect4(mixcolor1, realY);
            baseColor = AddVect4(baseColor, mixcolor1);
        }
        if (realX > 0.00001 && xy.x < imgSize.x - 1)
        {
            Vect4 mixcolor2;
            mixcolor2 = GetColorAt(xy.x + 1, xy.y, imgSize.x, imgData);
            if (realY > 0.00001 && xy.y < imgSize.y - 1)
            {
                Vect4 mixcolor3;
                mixcolor3 = GetColorAt(xy.x + 1, xy.y + 1, imgSize.x, imgData);
                mixcolor2 = ScaleVect4(mixcolor2, 1.0 - realY);
                mixcolor3 = ScaleVect4(mixcolor3, realY);
                mixcolor2 = AddVect4(mixcolor2, mixcolor3);
            }
            baseColor = ScaleVect4(baseColor, 1.0 - realX);
            mixcolor2 = ScaleVect4(mixcolor2, realX);
            baseColor = AddVect4(baseColor, mixcolor2);
        }
    }

    // Deep copy of final output
    Vect4 out;
    out.a = baseColor.a;
    out.b = baseColor.b;
    out.c = baseColor.c;
    out.d = baseColor.d;
    return out;
}

// Clamp a vector to standard 8 bit values
void ClampVect4(Vect4 vec)
{
    if (vec.a < 0) vec.a = 0;
    else if (vec.a > 255) vec.a = 255;
    if (vec.b < 0) vec.b = 0;
    else if (vec.b > 255) vec.b = 255;
    if (vec.c < 0) vec.c = 0;
    else if (vec.c > 255) vec.c = 255;
    if (vec.d < 0) vec.d = 0;
    else if (vec.d > 255) vec.d = 255;
}

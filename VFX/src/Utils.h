/**
 * Utils.h
 * Common utility functions for vector math and pixel sampling
 */

#ifndef _UTILS_H_
#define _UTILS_H_

// What format the pixels are in
typedef enum
{
    A = 0,
    RGBA = 1,
    XYZA = 2,
    LABA = 3,
    CMYKA = 4,
    GRAYA = 5,
    YCbCrA = 6
} ColorModel;

// How many bytes and of what type
typedef enum
{
    U8 = 0,
    U16 = 1, // Krita also has F16 depth sometimes, but that's weird and not
    F32 = 2  // standard, so it's not supported for now
} ColorDepth;

// Combined color data
typedef struct
{
    ColorModel colorModel;
    ColorDepth colorDepth;
} ColorData;

// Coordinates, 64 bit for each direction
typedef struct 
{
    long long x;
    long long y;
} Coords;

// 2 dimensional vector of doubles
typedef struct
{
    double a;
    double b;
} Vect2;

// 5 dimensional vector of doubles
// Largest color space, CMYKA, uses 5 channels
// If channels are unused, it should be initialized to 0
// Labels are used on read and write to organize the data
// and make it easier to tell which channel is which
typedef struct
{
    double r; // Red(ish) or red/green channel
    double b; // Blue(ish) or blue/yellow channel
    double o; // Other color channel (usually green or yellow)
    double l; // Lightness (Y/L/K)
    double a; // Alpha
} Pixel;

// Scale a 2 dimensional vector
Vect2 ScaleVect2(Vect2 vec, double scalar);

// Scale a 5 dimensional vector
Pixel ScalePixel(Pixel pix, double scalar);

// Sum two 2 dimensional vectors
Vect2 AddVect2(Vect2 vec1, Vect2 vec2);

// Sum two 5 dimensional vectors
Pixel AddPixel(Pixel pix1, Pixel pix2);

// Subtract two 2 dimensional vectors
Vect2 SubVect2(Vect2 vec1, Vect2 vec2);

// Subtract two 5 dimensional vectors
Pixel SubPixel(Pixel pix1, Pixel pix2);

// Calculates the length of a 2 dimensional vector
double LenVect(Vect2 vec);

// Possibly other functions here? Unitize, etc?

double DegreeToRadian(double deg);

double Max(double a, double b);

// Returns the color at a certain point in the image data
Pixel GetColorAt(
    long long x,
    long long y,
    long long imgWidth,
    void* imgData,
    ColorData colorData);

// Returns the color at a certain index in the image data
Pixel GetColorAtIdx(
    long long idx,
    long long imgWidth,
    void* imgData,
    ColorData colorData);

// Get a sample at the specified coordinates
// Performs bounds clamping and bilinear interpolation
Pixel SampleAt(
    double x,
    double y,
    Coords imgSize,
    void* imgData,
    ColorData colorData,
    char interpolate);

// Writes a pixel to the output buffer
void WritePixel(
    long long idx,
    Pixel pixelOut,
    void* outData,
    ColorData colorData);

// Guess the maximum value for a color space
long GetColorSpaceMax(ColorData colorData);

// Clamp a vector to the current color space
void ClampToColorSpace(Pixel pix, ColorData colorData);

#endif // ifndef _UTILS_H_

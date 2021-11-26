/**
 * Utils.h
 * Common utility functions for vector math and pixel sampling
 */

#ifndef _UTILS_H_
#define _UTILS_H_

/**
 *  TODO:
 * add a header file with different color modes and color-to-double conversion
 * possibly also how to handle each color type?
 */ 

// Generic color sample
typedef struct 
{
    unsigned char blue;
    unsigned char green;
    unsigned char red;
    unsigned char alpha;
} Pixel;

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

// 4 dimensional vector of doubles
typedef struct
{
    double a;
    double b;
    double c;
    double d;
} Vect4;

// Scale a 2 dimensional vector
Vect2 ScaleVect2(Vect2 vec, double scalar);

// Scale a 4 dimensional vector
Vect4 ScaleVect4(Vect4 vec, double scalar);

// Sum two 2 dimensional vectors
Vect2 AddVect2(Vect2 vec1, Vect2 vec2);

// Sum two 4 dimensional vectors
Vect4 AddVect4(Vect4 vec1, Vect4 vec2);

// Subtract two 2 dimensional vectors
Vect2 SubVect2(Vect2 vec1, Vect2 vec2);

// Subtract two 4 dimensional vectors
Vect4 SubVect4(Vect4 vec1, Vect4 vec2);

// Calculates the length of a 2 dimensional vector
double LenVect(Vect2 vec);

// Possibly other functions here? Unitize, etc?

double DegreeToRadian(double deg);

double Max(double a, double b);

// Returns the color at a certain point in the image data
Vect4 GetColorAt(
    long long x,
    long long y,
    long long imgWidth,
    Pixel* imgData);

// Get a sample at the specified coordinates
// Performs bounds clamping and bilinear interpolation
Vect4 SampleAt(
    double x,
    double y,
    Coords imgSize,
    Pixel* imgData,
    char interpolate);

// Clamp a vector to standard 8 bit values
void ClampVect4(Vect4 vec);

#endif // ifndef _UTILS_H_

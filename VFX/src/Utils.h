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

// Scale a 2 dimensional vector
void ScaleVect2(double* vec, double scalar, double* out);

// Scale a 4 dimensional vector
void ScaleVect4(double* vec, double scalar, double* out);

// Sum two 2 dimensional vectors
void AddVect2(double* vec1, double* vec2, double* out);

// Sum two 4 dimensional vectors
void AddVect4(double* vec1, double* vec2, double* out);

// Subtract two 2 dimensional vectors
void SubVect2(double* vec1, double* vec2, double* out);

// Subtract two 4 dimensional vectors
void SubVect4(double* vec1, double* vec2, double* out);

// Calculates the length of a 2 dimensional vector
double LenVect(double* vec);

// Possibly other functions here? Unitize, etc?

double DegreeToRadian(double deg);

double Max(double a, double b);

// Returns the color at a certain point in the image data
void GetColorAt(
    long long x,
    long long y,
    long long imgWidth,
    Pixel* imgData,
    double* out);

// Get a sample at the specified coordinates
// Performs bounds clamping and bilinear interpolation
void SampleAt(
    double x,
    double y,
    Coords imgSize,
    Pixel* imgData,
    char interpolate,
    double* out);

// Clamp a vector to standard 8 bit values
void ClampVect4(double* vec);

#endif // ifndef _UTILS_H_

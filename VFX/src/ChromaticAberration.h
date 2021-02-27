/**
 * ChromaticAberration.h
 * Contains functions for applying chromatic aberration effects to an image
 **/

#ifndef _CHROMATICABERRATION_H_
#define _CHROMATICABERRATION_H_

#include "Utils.h"

// Data structures for filter settings
typedef struct 
{
    int power;
    int deadzone;
    char expFalloff;
    char biFilter;
} RadialFilterData;

typedef struct 
{
    int power;
    int direction;
    char biFilter;
} LinearFilterData;

void ApplyLinearAberration(
    long long start,
    long long n,
    LinearFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData);

void ApplyRadialAberration(
    long long start,
    long long n,
    RadialFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData);

#endif // ifndef _CHROMATICABERRATION_H_

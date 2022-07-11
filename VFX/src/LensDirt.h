/**
 * LensDirt.h
 * Contains functions for rendering shapes to give the effect of dirt
 **/

#ifndef _LENSDIRT_H_
#define _LENSDIRT_H_

#include "Utils.h"

// Data structures for filter settings
typedef struct 
{
    int size;
    int sizeVarience;
    int opacity;
    int opacityVarience;
    char shape;
    int direction;
    int blur;
} LensDirtFilterData;

void CreateDirtShapes(
    long long start,
    long long n,
    LensDirtFilterData filterData,
    Coords imgSize,
    unsigned int seed,
    void* outData);

void RenderLensDirt(
    long long start,
    long long n,
    long long numShapes,
    LensDirtFilterData filterData,
    Coords imgSize,
    void* shapes,
    void* outData,
    ColorData colorData);

#endif // ifndef _LENSDIRT_H_

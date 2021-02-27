/**
 * LensFlare.h
 * Contains functions for applying cinematic lens flares to an image
 **/

#ifndef _LENSFLARE_H_
#define _LENSFLARE_H_

#include "Utils.h"

// Data structure for filter settings
typedef struct
{
    int artifactCopies;
    double artifactDisplacement;
    int haloDisplacement;
    double power;
    char bilinearFilter;
} LensFlareFilterData;

void ApplyPsuedoLensFlare(
    long long start,
    long long n,
    LensFlareFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData);

#endif // ifndef _LENSFLARE_H_

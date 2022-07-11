/**
 * LensFlare.c
 * Contains functions for applying cinematic lens flares to an image
 **/

#include <stdlib.h>
#include <math.h>
#include "LensFlare.h"

// Helper function for wrapping vectors around edges
void WrapVector(
    Vect2 vec,
    Coords imgSize)
{
    while (vec.a >= imgSize.x)
    {
        vec.a -= imgSize.x;
    }
    while (vec.a < 0)
    {
        vec.a += imgSize.x;
    }
    while (vec.b >= imgSize.y)
    {
        vec.b -= imgSize.y;
    }
    while (vec.b < 0)
    {
        vec.b += imgSize.y;
    }
}

// Apply pseudo lens flare to a section of an image
// Assumes the image has already been through a highpass filter
void ApplyPsuedoLensFlare(
    long long start,
    long long n,
    LensFlareFilterData filterData,
    Coords imgSize,
    void* imgData,
    void* outData,
    ColorData colorData)
{
    long long x = start % imgSize.x;
    long long y = start / imgSize.x;

    for (long long i = start; i < start + n; i++)
    {
        Pixel baseColor = {0, 0, 0, 0, 0};
        Vect2 centerPosVec; // From (0,0) to center of image
        Vect2 centerDirVec; // From coordVec to center of image
        Vect2 coordVec;
        Vect2 scratchVec; // Memory on the stack just for computation
        centerPosVec.a = (double)(imgSize.x - 1) / 2;
        centerPosVec.b = (double)(imgSize.y - 1) / 2;
        coordVec.a = (double)imgSize.x - x - 1;
        coordVec.b = (double)imgSize.y - y - 1;
        centerDirVec = SubVect2(centerPosVec, coordVec);
        centerDirVec = ScaleVect2(centerDirVec, filterData.artifactDisplacement);
        // Sample light artifacts
        for (int j = 0; j < filterData.artifactCopies; j++)
        {
            Vect2 offset;
            scratchVec = ScaleVect2(centerDirVec, (double)j);
            offset = AddVect2(coordVec, scratchVec);
            // Check if offset is out of bounds and wrap
            WrapVector(offset, imgSize);
            Pixel newSample = {0, 0, 0, 0, 0};
            newSample = SampleAt(offset.a, offset.b, imgSize, imgData, colorData, filterData.bilinearFilter);
            scratchVec = SubVect2(offset, centerPosVec);
            double alpha = newSample.a / GetColorSpaceMax(colorData);
            double weight = LenVect(scratchVec) / LenVect(centerPosVec);
            weight = 1 - weight;
            weight = pow(weight, 10);
            newSample = ScalePixel(newSample, weight);
            newSample = ScalePixel(newSample, alpha);
            baseColor = AddPixel(baseColor, newSample);
        }
        // Sample halo effect
        Vect2 haloVec;
        haloVec = ScaleVect2(centerDirVec, 1.0 / LenVect(centerDirVec));
        haloVec = ScaleVect2(haloVec, filterData.haloDisplacement);
        haloVec = AddVect2(coordVec, haloVec);
        WrapVector(haloVec, imgSize);
        scratchVec = SubVect2(haloVec, centerPosVec);
        double haloWeight = LenVect(scratchVec) / LenVect(centerPosVec);
        haloWeight = 1 - haloWeight;
        haloWeight = pow(haloWeight, 5);
        Pixel haloSample = {0, 0, 0, 0, 0};
        haloSample = SampleAt(haloVec.a, haloVec.b, imgSize, imgData, colorData, filterData.bilinearFilter);
        double haloAlpha = haloSample.a / GetColorSpaceMax(colorData);
        haloSample = ScalePixel(haloSample, haloWeight);
        haloSample = ScalePixel(haloSample, haloAlpha);
        baseColor = AddPixel(baseColor, haloSample);
        // Power, clamp, then return
        baseColor = ScalePixel(baseColor, filterData.power);
        ClampToColorSpace(baseColor, colorData);
        baseColor.a = GetColorSpaceMax(colorData);
        WritePixel(i, baseColor, outData, colorData);

        x++;
        if (x >= imgSize.x)
        {
            x = 0;
            y++;
        }
        if (y >= imgSize.y) break;
    }
}

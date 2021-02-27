/**
 * LensFlare.c
 * Contains functions for applying cinematic lens flares to an image
 **/

#include <stdlib.h>
#include <math.h>
#include "LensFlare.h"

// Helper function for wrapping vectors around edges
// such that it stays on the same line.
// This only works on vectors that go through the center
void WrapVector(
    double* vec,
    Coords imgSize,
    double vecSlope)
{
    if (vecSlope <= 1 && vecSlope >= -1)
    {
        while (vec[0] >= imgSize.x)
        {
            vec[0] -= imgSize.x;
            vec[1] -= imgSize.x * vecSlope;
        }
        while (vec[0] < 0)
        {
            vec[0] += imgSize.x;
            vec[1] += imgSize.x * vecSlope;
        }
    }
    else 
    {
        while (vec[1] >= imgSize.y)
        {
            vec[1] -= imgSize.y;
            vec[0] -= imgSize.y * (1 / vecSlope);
        }
        while (vec[1] < 0)
        {
            vec[1] += imgSize.y;
            vec[0] += imgSize.y * (1 / vecSlope);
        }
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
    void* outData)
{
    Pixel* pixelData = (Pixel*)imgData;
    Pixel* pixelOut = (Pixel*)outData;

    long long x = start % imgSize.x;
    long long y = start / imgSize.x;

    for (long long i = start; i < start + n; i++)
    {
        double baseColor[4];
        double centerPosVec[2]; // From (0,0) to center of image
        double centerDirVec[2]; // From coordVec to center of image
        double coordVec[2];
        double scratchVec[2]; // Memory on the stack just for computation
        centerPosVec[0] = (double)(imgSize.x - 1) / 2;
        centerPosVec[1] = (double)(imgSize.y - 1) / 2;
        coordVec[0] = (double)imgSize.x - x - 1;
        coordVec[1] = (double)imgSize.y - y - 1;
        GetColorAt(x, y, imgSize.x, imgData, baseColor);
        ScaleVect2(coordVec, -1.0, scratchVec);
        AddVect2(centerPosVec, scratchVec, centerDirVec);
        ScaleVect2(centerDirVec, filterData.artifactDisplacement, centerDirVec);
        double vecSlope = centerDirVec[1] / centerDirVec[0]; // used for coordinate wrapping
        // Sample light artifacts
        for (int j = 0; j < filterData.artifactCopies; j++)
        {
            double offset[2];
            ScaleVect2(centerDirVec, (double)j, scratchVec);
            AddVect2(coordVec, scratchVec, offset);
            // Check if offset is out of bounds and wrap
            WrapVector(offset, imgSize, vecSlope);
            double newSample[4];
            SampleAt(offset[0], offset[1], imgSize, pixelData, filterData.bilinearFilter, newSample);
            ScaleVect2(centerPosVec, -1.0, scratchVec);
            AddVect2(offset, scratchVec, scratchVec);
            double weight = LenVect(scratchVec) / LenVect(centerPosVec);
            weight = 1 - weight;
            weight *= weight;
            weight *= weight;
            ScaleVect4(newSample, weight, newSample);
            AddVect4(baseColor, newSample, baseColor);
        }
        // Sample halo effect
        double haloVec[2];
        ScaleVect2(centerDirVec, 1.0 / LenVect(centerDirVec), haloVec);
        ScaleVect2(haloVec, filterData.haloDisplacement, haloVec);
        AddVect2(coordVec, haloVec, haloVec);
        WrapVector(haloVec, imgSize, vecSlope);
        ScaleVect2(haloVec, -1.0, scratchVec);
        AddVect2(centerPosVec, scratchVec, scratchVec);
        double haloWeight = LenVect(scratchVec) / LenVect(centerPosVec);
        haloWeight = 1 - haloWeight;
        haloWeight *= haloWeight;
        haloWeight *= haloWeight;
        haloWeight *= haloWeight;
        double haloSample[4];
        SampleAt(haloVec[0], haloVec[1], imgSize, pixelData, filterData.bilinearFilter, haloSample);
        ScaleVect4(haloSample, haloWeight, haloSample);
        AddVect4(baseColor, haloSample, baseColor);
        // Power, clamp, then return
        ScaleVect4(baseColor, filterData.power, baseColor);
        ClampVect4(baseColor);
        pixelOut[i].blue = (unsigned char)baseColor[0];
        pixelOut[i].green = (unsigned char)baseColor[1];
        pixelOut[i].red = (unsigned char)baseColor[2];
        pixelOut[i].alpha = (unsigned char)baseColor[3];

        x++;
        if (x >= imgSize.x)
        {
            x = 0;
            y++;
        }
        if (y >= imgSize.y) break;
    }
}

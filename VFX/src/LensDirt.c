/**
 * LensDirt.c
 * Contains functions for rendering shapes to give the effect of dirt
 **/

#include <stdlib.h>
#include <math.h>
#include "LensDirt.h"

void CreateDirtShapes(
    long long start,                // start index of shapes to generate
    long long n,                    // how many shapes to generate
    LensDirtFilterData filterData,  // what shapes to generate
    Coords imgSize,                 // Size of the image
    unsigned int seed,              // random seed, not time because granularity is in seconds
    void* outData)                  // list of floats (allocated by python)
{
    // Generating thousands of numbers is faster in C, that's why this is here
    float* out = (float*) outData;
    unsigned int floatsPerEntry = (filterData.shape * 2) + 2; // pair of points per side + 2 for other data
    Vect2 center = {(imgSize.x - 1) / 2.0, (imgSize.y - 1) / 2.0};
    // This is just useful
    double pi = acos(-1);
    // srand/rand is not thread safe in C because it's state is shared across threads
    // but I don't care about that so :P
    srand(seed);
    for (long long i = start; i < n + start; i++)
    {
        Vect2 vec = {0,0};
        Vect2 shapeCenter = {0,0};
        float size = filterData.size;
        float dir = DegreeToRadian(filterData.direction);
        float opacity = filterData.opacity;
        shapeCenter.a = rand() % imgSize.x;
        shapeCenter.b = rand() % imgSize.y;
        // Figure out the size of the shape
        if (filterData.sizeVarience != 0)
        {
            size = (float)filterData.size * ((100.0 - (rand() % filterData.sizeVarience)) / 100.0);
        }
        // Figure out opacity
        if (filterData.opacityVarience != 0)
        {
            opacity = filterData.opacity * ((100.0 - (rand() % filterData.opacityVarience)) / 100.0);
        }
        // If this is a circle, then that's all we need
        if (filterData.shape == 1)
        {
            out[i * floatsPerEntry] = shapeCenter.a;
            out[(i * floatsPerEntry) + 1] = shapeCenter.b;
            out[(i * floatsPerEntry) + 2] = size;
            out[(i * floatsPerEntry) + 3] = opacity;
            continue;
        }
        // Figure out the direction
        if (filterData.direction == -1) // towards center
        {
            vec = SubVect2(center, shapeCenter);
            dir = atan(vec.b / vec.a);
            if (vec.a >= 0) dir += pi;
            dir += pi / 2; // I dunno, there's this weird thing where it looks like a swirl
            vec = ScaleVect2(vec, size / LenVect(vec));
            vec = AddVect2(vec, shapeCenter);
            out[i * floatsPerEntry] = vec.a;
            out[(i * floatsPerEntry) + 1] = vec.b;
        }
        else
        {
            if (filterData.direction == -2) // random
            {
                dir = DegreeToRadian(rand() % 360);
            }
            out[i * floatsPerEntry] = shapeCenter.a + ((-1 * sin(dir)) * size);
            out[(i * floatsPerEntry) + 1] = shapeCenter.b + (cos(dir) * size);
        }
        // we have the first point, now fill out the rest of the points
        if (filterData.shape == 2) // Line, two points, and opacity
        {
            out[(i * floatsPerEntry) + 2] = shapeCenter.a - ((-1 * sin(dir)) * size);
            out[(i * floatsPerEntry) + 3] = shapeCenter.b - (cos(dir) * size);
            out[(i * floatsPerEntry) + 4] = opacity;
        }
        else // other monotone and regular polygon, simple formulas to draw point by point
        {
            float sidelen = size * 2 * sin(pi / filterData.shape);
            float angle = (2 * pi) / filterData.shape;
            float startAngle = dir + (pi / 2);
            // For as many sides as there are, get the next angle, travel len distance
            for (int j = 1; j < filterData.shape; j++)
            {
                long long idx = (i * floatsPerEntry) + (j * 2);
                startAngle += angle;
                out[idx] = out[idx - 2] + (sidelen * cos(startAngle));
                out[idx + 1] = out[idx - 1] + (sidelen * sin(startAngle));
            }
            out[(i * floatsPerEntry) + (2 * filterData.shape)] = opacity;
        }
    }
}

void RenderLensDirt(
    long long start,
    long long n,
    long long numShapes,
    LensDirtFilterData filterData,
    Coords imgSize,
    void* shapes,
    void* outData,
    ColorData colorData)
{
    float* shapeArray = (float*) shapes;
    unsigned int floatsPerEntry = (filterData.shape * 2) + 2; // pair of points per side + 2 for other data
    double colorMax = GetColorSpaceMax(colorData);
    for (long long i = start; i < n + start; i++)
    {
        Pixel color = {colorMax,colorMax,colorMax,colorMax,0};
        long long x = i % imgSize.x;
        long long y = i / imgSize.x;
        for (long long j = 0; j < numShapes; j++)
        {
            // Get index for shape
            long long shapeIdx = j * floatsPerEntry;
            Vect2 xpoint1 = {shapeArray[shapeIdx],shapeArray[shapeIdx + 1]};
            Vect2 xpoint2 = {0,0};
            Vect2 xpoint3 = {0,0};
            Vect2 xpoint4 = {0,0};
            char point1found = 0;
            float lerp1 = 0;
            float lerp2 = 0;
            // Quick sanity check to see if the shape is anywhere near this pixel
            if (shapeArray[shapeIdx] + (filterData.size * 2) < x
                || shapeArray[shapeIdx] - (filterData.size * 2) > x
                || shapeArray[shapeIdx + 1] + (filterData.size * 2) < y
                || shapeArray[shapeIdx + 1] - (filterData.size * 2) > y)
            {
                continue;
            }
            if (filterData.shape == 1) // circle is a simple manner of if point is in range of the center
            {
                xpoint2.a = x;
                xpoint2.b = y;
                xpoint2 = SubVect2(xpoint2, xpoint1);
                if (LenVect(xpoint2) <= shapeArray[shapeIdx + 2])
                {
                    color.a += (shapeArray[shapeIdx + 3] / 100.0) * colorMax;
                }
            }
            else if (filterData.shape == 2) // line, see if point is within 1 pixel of the line
            {
                xpoint2.a = shapeArray[shapeIdx + 2];
                xpoint2.b = shapeArray[shapeIdx + 3];
                xpoint3.a = x;
                xpoint3.b = y;
                // Check if this pixel is close to either end point
                if (LenVect(SubVect2(xpoint1, xpoint3)) <= 1 || LenVect(SubVect2(xpoint2, xpoint3)) <= 1)
                {
                    color.a += (shapeArray[shapeIdx + 4] / 100.0) * colorMax;
                    continue;
                }
                // Else see how close to the line it is
                // Skip if pixel not in the rectangle formed by the line as a diagonal
                if ((x > xpoint1.a + 1 && x > xpoint2.a + 1)
                    || (x < xpoint1.a - 1 && x < xpoint2.a - 1)
                    || (y > xpoint1.b + 1 && y > xpoint2.b + 1)
                    || (y < xpoint1.b - 1 && y < xpoint2.b - 1)) continue;
                // Now we know there will be an x intercept and y intercept
                lerp1 = ((double)y - xpoint1.b) / (xpoint2.b - xpoint1.b);
                xpoint4.a = (lerp1 * (xpoint2.a - xpoint1.a)) + xpoint1.a; // X coord of Y intercept
                lerp2 = ((double)x - xpoint1.a) / (xpoint2.a - xpoint1.a);
                xpoint4.b = (lerp2 * (xpoint2.b - xpoint1.b)) + xpoint1.b; // Y coord of X intercept
                if (abs(xpoint4.a - x) <= 1 || abs(xpoint4.b - y) <= 1)
                {
                    color.a += (shapeArray[shapeIdx + 4] / 100.0) * colorMax;
                }
            }
            else
            {
                // for each side, check if y height of point is crossed
                xpoint1.a = shapeArray[shapeIdx + ((filterData.shape - 1) * 2)];
                xpoint1.b = shapeArray[shapeIdx + ((filterData.shape - 1) * 2) + 1];
                for (unsigned int k = 0; k < filterData.shape; k++)
                {
                    if (point1found == 0)
                    {
                        xpoint2.a = shapeArray[shapeIdx + (k * 2)];
                        xpoint2.b = shapeArray[shapeIdx + (k * 2) + 1];
                        if ((xpoint1.b <= y && xpoint2.b > y) || (xpoint1.b > y && xpoint2.b <= y)) // This is one of the cross points
                        {
                            xpoint3.a = xpoint2.a;
                            xpoint3.b = xpoint2.b;
                            point1found = 1;
                        }
                        else
                        {
                            xpoint1.a = xpoint2.a;
                            xpoint1.b = xpoint2.b;
                        }
                    }
                    else
                    {
                        xpoint4.a = shapeArray[shapeIdx + (k * 2)];
                        xpoint4.b = shapeArray[shapeIdx + (k * 2) + 1];
                        if ((xpoint3.b <= y && xpoint4.b > y) || (xpoint3.b > y && xpoint4.b <= y)) // This is the other cross point
                        {
                            break;
                        }
                        else
                        {
                            xpoint3.a = xpoint4.a;
                            xpoint3.b = xpoint4.b;
                        }
                    }
                }
                // no sides that cross the point's y value means no intersect
                // both sides left or right of point means no intersect
                if (point1found == 0
                    || (xpoint1.a > x && xpoint2.a > x && xpoint3.a > x && xpoint4.a > x)
                    || (xpoint1.a < x && xpoint2.a < x && xpoint3.a < x && xpoint4.a < x))
                {
                    continue;
                }
                // Proving that the pixel is inside the shape
                lerp1 = ((double)y - xpoint1.b) / (xpoint2.b - xpoint1.b);
                lerp2 = ((double)y - xpoint3.b) / (xpoint4.b - xpoint3.b);
                lerp1 = (lerp1 * (xpoint2.a - xpoint1.a)) + xpoint1.a;
                lerp2 = (lerp2 * (xpoint4.a - xpoint3.a)) + xpoint3.a;
                if ((lerp1 <= x && lerp2 > x) || (lerp1 > x && lerp2 <= x)) // Congrats, we found it!
                {
                    color.a += (shapeArray[shapeIdx + (2 * filterData.shape)] / 100.0) * colorMax;
                }
            }
        }
        WritePixel(i, color, outData, colorData);
    }
}

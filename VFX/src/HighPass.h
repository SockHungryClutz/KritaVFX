/**
 * HighPass.h
 * Apply a simple highpass filter (not gaussian)
 * And some other misc functions...
 * Bias  = add colors
 * Power = integer multiply (not float multiply)
 **/

#ifndef _HIGHPASS_H_
#define _HIGHPASS_H_

#include "Utils.h"

void ApplyPower(
    long long start,
    long long n,
    Pixel power,
    Coords imgSize,
    void* imgData,
    void* outData);

void ApplyBias(
    long long start,
    long long n,
    Pixel bias,
    Coords imgSize,
    void* imgData,
    void* outData);

void ApplyHighPass(
    long long start,
    long long n,
    int threshold,
    Pixel bias,
    Coords imgSize,
    void* imgData,
    void* outData);

#endif // ifndef _HIGHPASS_H_

/**
 * HighPass.h
 * Apply a simple highpass filter (not gaussian)
 * And some other misc functions...
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

void ApplyHighPass(
    long long start,
    long long n,
    int threshold,
    Coords imgSize,
    void* imgData,
    void* outData);

#endif // ifndef _HIGHPASS_H_

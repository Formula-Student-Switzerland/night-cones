/*******************************************************************************/
/* 
 * File: color.c
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file is used to convert the transmitted 8 bit color and 4 bit brightness
 * This allowes to show 128 colors in 16 brightness levels. 
 */
/*******************************************************************************/

#ifndef COLOR_H
#define COLOR_H
#include <stdint.h>

#define COLOR_GREEN 96
#define COLOR_BLUE  32
#define COLOR_RED   192
#define COLOR_WHITE 255

void color_decode (uint8_t color, uint8_t brightness, uint8_t *decoded);

#endif
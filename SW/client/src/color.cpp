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
#include <stdint.h>
#include "color.h"

/**
 * Decode the received color field uint8_to RGB components

 * @param color: 8 bit color code from blue-green-red-white (see documentation)
 * @param brightness: LEFT (MSB) aligned 4 bit brightness code. Lower 4 bits
 *                  must be 0
 * @param decode 3 byte array pointer with the three components RGB
 */
void color_decode (uint8_t color, uint8_t brightness, uint8_t *decoded) {
	// Init variables.
	float red = 0;
	float green = 0;
	float blue = 0;
	
	if(brightness == 0){
		decoded[0] = 0;
		decoded[1] = 0;
		decoded[2] = 0;
		return;
	}

	// Set red component.
	if (color < 32) {
    	red = (31-color) / 32.0 * 30;
	} else if (color < 96) {
    	red = 0;
  	} else if (color < 128) {
    	red = (color-96) / 32.0 * 30;
  	} else {
    	red = 30;
  	}

	// Set green component.
  	if (color >= 64 && color <= 127) {
    	green = 30;
  	} else if (color >= 32 && color <= 63) {
    	green = (color - 31) / 32.0 * 30;
  	} else if (color >= 128 && color <= 191) {
    	green = (1 - (color - 127) / 64.0) * 30;
  	} else if (color >= 224) {
    	green = (color - 223) / 32.0 * 30;
  	} else {
    	green = 0;
  	}

  	// Set blue component.
  	if ((color <= 63) || (color >= 224)) {
    	blue = 30;
  	} else if (color >= 64 && color <= 95) {
    	blue = ((96-color ) / 32.0) * 30;
  	} else if (color >= 192 && color <= 223) {
    	blue = (color - 191) / 32.0 * 30;
  	} else {
    	blue = 0;
  	}

  	// Scale colors with brightness.
  	if (red >= green && red >= blue) {
    	decoded[0] = (uint8_t)brightness;  // red scaled
    	decoded[1] = (uint8_t)green / red * brightness;  // green scaled
    	decoded[2] = (uint8_t)blue / red * brightness;  // blue scaled
  	} else if (green >= blue) {
    	decoded[1] = (uint8_t) brightness;
    	decoded[0] = (uint8_t) red / green * brightness;
    	decoded[2] = (uint8_t) blue / green  * brightness;
  	} else {
    	decoded[2] = (uint8_t)brightness;
    	decoded[0] = (uint8_t)red / blue * brightness;
    	decoded[1] = (uint8_t)green / blue * brightness;
  	}
}
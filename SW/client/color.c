#include "color.h"

void decodeColors (int color, int brightness, int *decoded) {
	// Init variables.
	float red = 0;
	float green = 0;
	float blue = 0;

	// Set red component.
	if (color <= 95) {
    	red = 0;
	} else if (color <= 127) {
    	red = (color - 95) / 32.0 * 30;
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
  	if ((color >= 32 && color <= 63) || (color >= 224)) {
    	blue = 30;
  	} else if (color <= 31) {
    	blue = color / 31.0 * 30;
  	} else if (color >= 64 && color <= 95) {
    	blue = (1 - (color - 63) / 32.0) * 30;
  	} else if (color >= 192 && color <= 223) {
    	blue = (color - 191) / 32.0 * 30;
  	} else {
    	blue = 0;
  	}

  	// Scale colors with brightness.
  	if (red >= green && red >= blue) {
    	decoded[0] = 1.275 * brightness;  // red scaled
    	decoded[1] = green / red * 1.275 * brightness;  // green scaled
    	decoded[2] = blue / red * 1.275 * brightness;  // blue scaled
  	} else if (green >= blue) {
    	decoded[1] = 1.275 * brightness;
    	decoded[0] = red / green * 1.275 * brightness;
    	decoded[2] = blue / green * 1.275 * brightness;
  	} else {
    	decoded[2] = 1.275 * brightness;
    	decoded[0] = red / blue * 1.275 * brightness;
    	decoded[1] = green / blue * 1.275 * brightness;
  	}

}
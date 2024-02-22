#include<stdio.h>
#include<string.h>

void decodeColors (int color, int brightness, int *decoded);
void displayLeds (int *leds, int *colors);


int main() {
	// Define debug settings.
	int color = 130;
	int brightness = 50;

	// Decode colors and brightness.
	int decoded[3];
	decodeColors(color, brightness, decoded);

	printf("%d\n", decoded[0]);
	printf("%d\n", decoded[1]);
	printf("%d\n", decoded[2]);


	return 0;
}


void decodeColors (int color, int brightness, int *decoded) {
	// Init variables.
	float red = 0;
	float green = 0;
	float blue = 0;
	int red_scaled = 0;
	int green_scaled = 0;
	int blue_scaled = 0;

	// Set red component.
	if (color <= 95) {
    	red = 0;
	} else if (color <= 127) {
    	red = (color - 95) / 32.0 * 15;
  	} else {
    	red = 15;
  	}

	// Set green component.
  	if (color >= 64 && color <= 127) {
    	green = 15;
  	} else if (color >= 32 && color <= 63) {
    	green = (color - 31) / 32.0 * 15;
  	} else if (color >= 128 && color <= 191) {
    	green = (1 - (color - 127) / 64.0) * 15;
  	} else if (color >= 224) {
    	green = (color - 223) / 32.0 * 15;
  	} else {
    	green = 0;
  	}

  	// Set blue component.
  	if ((color >= 32 && color <= 63) || (color >= 224)) {
    	blue = 15;
  	} else if (color <= 31) {
    	blue = color / 31.0 * 15;
  	} else if (color >= 64 && color <= 95) {
    	blue = (1 - (color - 63) / 32.0) * 15;
  	} else if (color >= 192 && color <= 223) {
    	blue = (color - 191) / 32.0 * 15;
  	} else {
    	blue = 0;
  	}

	printf("%f\n", red);
	printf("%f\n", green);
	printf("%f\n", blue);

  	// Scale colors with brightness.
  	if (red >= green && red >= blue) {
    	red_scaled = 2.55 * brightness;
    	green_scaled = green / red * 2.55 * brightness;
    	blue_scaled = blue / red * 2.55 * brightness;
  	} else if (green >= blue) {
    	green_scaled = 2.55 * brightness;
    	red_scaled = red / green * 2.55 * brightness;
    	blue_scaled = blue / green * 2.55 * brightness;
  	} else {
    	blue_scaled = 2.55 * brightness;
    	red_scaled = red / blue * 2.55 * brightness;
    	green_scaled = green / blue * 2.55 * brightness;
  	}

	decoded[0] = red_scaled;
	decoded[1] = green_scaled;
	decoded[2] = blue_scaled;

}

/*
U8/L2	U9/L3	U10/L4	U11/L5	U12/L6

U7/L1	U22/L16			U23/L17	U13/L7

U6/L0							U14/L8

U21/L15	U25/19			U24/L18	U15/L9

U20/L14	U19/L13	U18/L12	U17/L11	U16/L10

X X X X X
X X   X X
X       X
X X   X X
X X X X X
*/
int displayLeds(int *leds, int *colors, int lastLen) {
	char displayStr[100];
	char illumChar[21];
	int stringLen;

	// Set array for LED on strings.
	for (int k=0; k<20; k++) {
		if (leds[k] == 1) {
			illumChar[k] = "X";
		} else {
			illumChar[k] = " ";
		}
	}
	illumChar[20] = "\0"

	// Add color header.
	displayStr = sprintf("R: %03d\nG: %03d\nB: %03d\n\n", colors[0], colors[1], colors[2]);

	// Add led representation.
	strcat(displayStr, sprintf("%c %c %c %c %c\n\n", illumChar[2], illumChar[3], illumChar[4], illumChar[5], illumChar[6]))
	strcat(displayStr, sprintf("%c %c   %c %c\n\n", illumChar[1], illumChar[16], illumChar[17], illumChar[7]))
	strcat(displayStr, sprintf("%c       %c\n\n", illumChar[0], illumChar[8]))
	strcat(displayStr, sprintf("%c %c   %c %c\n\n", illumChar[15], illumChar[19], illumChar[18], illumChar[9]))
	strcat(displayStr, sprintf("%c %c %c %c %c", illumChar[14], illumChar[13], illumChar[12], illumChar[11], illumChar[10]))

	// Calculate display string length.
	stringLen = sizeof(displayStr) / sizeof(displayStr[0])

}

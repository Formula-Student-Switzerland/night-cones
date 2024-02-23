#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define DEV 1
#define LED_NUMBER 20

void decodeColors (int color, int brightness, int *decoded);
void setup();
void loop();
void processLightModes (int lightMode, int color, int brightness, int repetitionTime, int *ledState);

#ifdef DEV
	int displayLeds(int *leds, int *colors);
#endif

#ifdef DEV
	int main() {
		
		setup();
		loop();

		return 0;
	}
#endif


void setup() {

	}


void loop() {
	// Receive and process serial data.
	int lightMode = 0;
	int color = 90;
	int brightness = 100;
	int repetitionTime = 500;  // ms

	// Process led representation.
	int ledState[LED_NUMBER*3] = {0};

	processLightModes(lightMode, color, brightness, repetitionTime, ledState);

	// Control LED.
	#ifndef DEV

	#else
		displayLeds(ledState);
	#endif

}

void processLightModes (int lightMode, int color, int brightness, int repetitionTime, int *ledState) {

	switch (lightMode) {
		case 0: 
			lightMode1(color, brightness, ledState);
			break;
		case 1:
			lightMode2(color, brightness, ledState)


	}

}

void lightMode1(int color, int brightness, int *ledState) {
	// Process colors.
	int colorDecoded[3];
	decodeColors(color, brightness, colorDecoded);

	// Assign colors to LED.
	for (int k=0; k<LED_NUMBER; k++) {
		ledState[k] = colorDecoded[0];
		ledState[k+1] = colorDecoded[1];
		ledState[k+2] = colorDecoded[2];
	}

}



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

#ifdef DEV
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
int displayLeds(int *ledState) {
	char displayStr[100];
	char illumChar[LED_NUMBER*3+1];

	// Delete the last conlose content.
	printf("\033[H\033[J");

	// Set array for LED on strings.
	for (int k=0; k<LED_NUMBER; k++) {
		if (ledState[k] > 50 || ledState[k+1] > 50 || ledState[k+2] > 50) {
			illumChar[k] = 'X';
		} else if (ledState[k] > 0 || ledState[k+1] > 0 || ledState[k+2] > 0) {
			illumChar[k] = 'x';
		} else {
			illumChar[k] = ' ';
		}
	}
	illumChar[20] = '\0';

	// Add color header.
	sprintf(displayStr, "R: %03d\nG: %03d\nB: %03d\n\n", ledState[0], ledState[1], ledState[2]);

	// Add led representation.
	sprintf(displayStr, "%s%c %c %c %c %c\n", displayStr, illumChar[2], illumChar[3], illumChar[4], illumChar[5], illumChar[6]);
	sprintf(displayStr, "%s%c %c   %c %c\n", displayStr, illumChar[1], illumChar[16], illumChar[17], illumChar[7]);
	sprintf(displayStr, "%s%c       %c\n", displayStr, illumChar[0], illumChar[8]);
	sprintf(displayStr, "%s%c %c   %c %c\n", displayStr, illumChar[15], illumChar[19], illumChar[18], illumChar[9]);
	sprintf(displayStr, "%s%c %c %c %c %c", displayStr, illumChar[14], illumChar[13], illumChar[12], illumChar[11], illumChar[10]);

	printf(displayStr);

	return 0;

}
#endif
#ifdef FLASH
	#include "WS2812.h"

	WS2812 LED(1);
	cRGB light_value;

	int controlLeds(int *ledState) {

		for (int k=0; k<LED_NUMBER; k++) {
			// Assign rgb values.
			light_value.r = ledState[k*3];
			light_value.g = ledState[k*3+1];
			light_value.b = ledState[k*3+2];

			// Set rgb value.
			LED.set_crgb_at(k, value);
		}

		// Send rgb to LEDs.
		LED.sync()

	}

#endif

#ifndef FLASH
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
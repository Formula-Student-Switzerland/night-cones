#ifdef OUTPUT_PIN
	#include <Adafruit_NeoPixel.h>

	Adafruit_NeoPixel leds(LED_NUMBER, OUTPUT_PIN, NEO_GRB + NEO_KHZ800);

	int initLeds() {
		leds.begin();
		leds.clear();
	}


	int controlLeds(int *ledState) {

		leds.clear();

		for (int k=0; k<LED_NUMBER; k++) {
			// Assign rgb values.
			leds.setPixelColor(k, leds.Color(ledState[k*3], ledState[k*3+1], ledState[k*3+2]));
			
		}

		// Send rgb to LEDs.
		leds.show();

	}

	int clearLeds() {
		leds.clear();
		leds.show();
	}

#else
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

	// Delete the last conlose content.
	printf("\033[H\033[J");

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
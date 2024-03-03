#include "lightmodes.h"

void processLightModes (int lightMode, int color, int brightness, int repetitionTime, int *ledState) {

	switch (lightMode) {
		case 0: 
			lightMode1(color, brightness, ledState);
			break;
		case 1:
			lightMode2(color, brightness, repetitionTime, ledState);


	}

}

void lightMode1(int color, int brightness, int *ledState) {
	// Process colors.
	int colorDecoded[3];
	decodeColors(color, brightness, colorDecoded);

	// Assign colors to LED.
	for (int k=0; k<LED_NUMBER; k++) {
		ledState[k*3] = colorDecoded[0];
		ledState[k*3+1] = colorDecoded[1];
		ledState[k*3+2] = colorDecoded[2];
	}

}

void lightMode2(int color, int brightness, int repetitionTime, int *ledState) {

}
#include <stdio.h>
#include <string.h>
#include <unistd.h>

//#define FLASH 1
#define LED_NUMBER 20

#ifdef FLASH
	#define OUTPUT_PIN 0
#endif

#include "colors.h"
#include "led.h"

void setup();
void loop();
void processLightModes (int lightMode, int color, int brightness, int repetitionTime, int *ledState);
void lightMode1(int color, int brightness, int *ledState);
void lightMode2(int color, int brightness, int repetitionTime, int *ledState);


#ifndef FLASH
	int main() {
		
		setup();
		while (1) {
			loop();
			sleep(0.1);
		}

		return 0;
	}
#endif


void setup() {
	#ifdef FLASH
		LED.setOutput(OUTPUT_PIN);

	#endif

	}


void loop() {
	// Receive and process serial data. (Currently static data for testing)
	// TODO: Implement actual serial data receiving.
	int lightMode = 0;
	int color = 90;
	int brightness = 100;
	int repetitionTime = 3000;  // ms

	// Process led representation.
	int ledState[LED_NUMBER*3] = {0};

	processLightModes(lightMode, color, brightness, repetitionTime, ledState);

	// Control LED.
	#ifdef FLASH
		controlLeds(ledState)
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


#include "main.h"

#include <string.h>
#include <unistd.h>

#include "color.h"
#include "led.h"

#ifdef OUTPUT_PIN
	#include "ota.h"
 	const char* ssid = STASSID;
	const char* password = STAPSK;
#endif



void setup() {
	#ifdef OUTPUT_PIN
		// OTA feature.
		ota_setup();
		
		
		initLeds();

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
	#ifdef OUTPUT_PIN
		controlLeds(ledState);
	#else
		displayLeds(ledState);
	#endif

}




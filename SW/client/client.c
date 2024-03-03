#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define LED_NUMBER 20

#include "main.h"


int main() {
	
	setup();
	while (1) {
		loop();
		sleep(0.1);
	}

	return 0;
}


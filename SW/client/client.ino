#include <WS2812.h>

#define LEDCount 20
#define outputPin 7

WS2812 LED(LEDCount); 
cRGB value;



// Debug settings.
#define lightMode 0
#define color 95
#define frequency 1
#define brightness 100



void setup() {
  LED.setOutput(outputPin);
}

void loop() {
  // Message Receive.



  // Message decode.

  // Decode color.
  int red = 0;
  int green = 0;
  int blue = 0;
  int red_scaled = 0;
  int green_scaled = 0;
  int blue_scaled = 0;

  // Set red component.
  if (color <= 95) {
    red = 0;
  } else if (color <= 127) {
    red = (color - 95) / 32 * 30;
  } else {
    red = 30;
  }

  // Set green component.
  if (color >= 64 && color <= 127) {
    green = 30;
  } else if (color >= 32 && color <= 63) {
    green = (color - 31) / 32 * 30;
  } else if (color >= 128 && color <= 191) {
    green = (1 - (color - 127) / 64) * 30;
  } else if (color >= 224) {
    green = (color - 223) / 32 * 30;
  } else {
    green = 0;
  }

  // Set blue component.
  if ((color >= 32 && color <= 63) || (color >= 224)) {
    blue = 30;
  } else if (color <= 31) {
    blue = color / 31 * 30;
  } else if (color >= 64 && color <= 95) {
    blue = (1 - (color - 63) / 32) * 30;
  } else if (color >= 192 && color <= 223) {
    blue = (color - 191) / 32 * 30;
  } else {
    blue = 0;
  }

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


  switch(lightMode) {


  }






  // Message Transmit.

}

/****************************)***************************************************/
/*
 * File: led.c
 * Author: Andreas Horat / Oliver Clemens
 */
/*******************************************************************************/
/*
 * This file is used to control the on-board LED and the led Strip on the
 * nightcone.
/*******************************************************************************/

#include <stdint.h>
#include "Adafruit_NeoPixel.h"
#include "led.h"
#include "Arduino.h"

#ifndef LED_EMULATION

uint8_t led_state[LED_COUNT * 3];
Adafruit_NeoPixel leds(LED_COUNT+1, -1, NEO_GRB + NEO_KHZ800);

/**
 * Setup the On-Board LED and the LED Strip. Turn off all LEDs.
 *
 */
void led_setup(uint8_t hw_revision)
{
  pinMode(LED_ESP_PIN, OUTPUT);
  switch (hw_revision)
  {
  case 1:
    leds.setPin(LED_PIN_NC1_1AA);
    Serial.print("Configured LED on PIN 15\n");
    break;
  case 2:
    leds.setPin(LED_PIN_NC1_1BB);
    break;

  default:
    leds.setPin(-1);
    break;
  }

  leds.begin();
  led_clear();
  leds.setPixelColor(20, leds.Color(255,255,255));
  
}

/**
 * Show the ledState on the LEDs. This procedure uses time.
 * @param ledState: uint8_t array with length 3*LED_COUNT which is used to define the LED colors.
 *
 */
void led_show(uint8_t *ledState)
{
  //leds.clear();
  //leds.setPixelColor(20, leds.Color(255, 255, 255));
  for (int k = 0; k < LED_COUNT; k++)
  {
    leds.setPixelColor(k, leds.Color(ledState[k * 3], ledState[k * 3 + 1], ledState[k * 3 + 2]));
  }
  leds.show();
}

/**
 * Turn off all LEDs
 *
 */
void led_clear()
{
  leds.clear();
  leds.setPixelColor(20, leds.Color(127, 127, 127));
  leds.show();
}

/**
 * Let the on-board LED blink for e specific amount of times. This function is blocking
 * with busy loop to realize the delay.
 *
 */
void led_esp_blink(int frequency, int blinks)
{
  for (int b = 0; b < blinks; b++)
  {
    digitalWrite(LED_ESP_PIN, 1);
    delay(frequency);
    digitalWrite(LED_ESP_PIN, 0);
    delay(frequency);
  }
  //digitalWrite(LED_ESP_PIN, 1);
}

/**
 * Show The temperature and voltage using the LEDs on top and bottom instead of the
 * normal lightmode.
 * @param temp temeprature in ADC Counts
 * @param voltage voltage in mV
 */
void led_show_status(int8_t temp, int16_t voltage)
{
  int led_temp_red;
  int led_temp_green;
  int led_temp_blue;

  leds.clear();

  // Show Temperature through LEDs on top
  if (temp < 20)
  {
    led_temp_red = 0;
    led_temp_green = 0;
    led_temp_blue = 100;
  }
  else if (temp > 80)
  {
    led_temp_red = 100;
    led_temp_green = 0;
    led_temp_blue = 0;
  }
  else
  {
    led_temp_red = 100 - (80 - temp);
    led_temp_green = 0;
    led_temp_blue = (80 - temp);
  }

  for (int n = 16; n < 20; n++)
  {
    leds.setPixelColor(n, led_temp_red, led_temp_green, led_temp_blue);
  }

  // Show voltage as series of LEDs on bottom
  int n_led_indicator;
  if (voltage > 4200)
  {
    n_led_indicator = 15;
  }
  else if (voltage < 3000)
  {
    n_led_indicator = 0;
  }
  else
  {
    n_led_indicator = (voltage - 2000) * 14 / 1200;
  }
  for (int n = 0; n <= n_led_indicator; n++)
  {
    leds.setPixelColor(n, LED_DEFAULT_BRIGHTNESS, LED_DEFAULT_BRIGHTNESS, LED_DEFAULT_BRIGHTNESS);
  }
  leds.show();
}

#else
#include "HardwareSerial.h"
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
int displayLeds(int *ledState)
{
  char displayStr[100];
  char illumChar[LED_COUNT * 3 + 1];

  // Set array for LED on strings.
  for (int k = 0; k < LED_COUNT; k++)
  {
    if (ledState[k] > 50 || ledState[k + 1] > 50 || ledState[k + 2] > 50)
    {
      illumChar[k] = 'X';
    }
    else if (ledState[k] > 0 || ledState[k + 1] > 0 || ledState[k + 2] > 0)
    {
      illumChar[k] = 'x';
    }
    else
    {
      illumChar[k] = ' ';
    }
  }
  illumChar[20] = '\0';

  // Delete the last conlose content.
  Serial.printf("\033[H\033[J");

  // Add color header.
  sprintf(displayStr, "R: %03d\nG: %03d\nB: %03d\n\n", ledState[0], ledState[1], ledState[2]);

  // Add led representation.
  sprintf(displayStr, "%s%c %c %c %c %c\n", displayStr, illumChar[2], illumChar[3], illumChar[4], illumChar[5], illumChar[6]);
  sprintf(displayStr, "%s%c %c   %c %c\n", displayStr, illumChar[1], illumChar[16], illumChar[17], illumChar[7]);
  sprintf(displayStr, "%s%c       %c\n", displayStr, illumChar[0], illumChar[8]);
  sprintf(displayStr, "%s%c %c   %c %c\n", displayStr, illumChar[15], illumChar[19], illumChar[18], illumChar[9]);
  sprintf(displayStr, "%s%c %c %c %c %c", displayStr, illumChar[14], illumChar[13], illumChar[12], illumChar[11], illumChar[10]);

  Serial.printf(displayStr);

  return 0;
}
#endif
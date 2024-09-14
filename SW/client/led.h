/****************************)***************************************************/
/* 
 * File: led.h
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file is used to control the LED strip and the on-board LED
 */
/*******************************************************************************/
#ifndef LED_H
#define LED_H
#include <stdint.h>

#define LED_COUNT 20
#define LED_BOTTOM_COUNT 16

#define LED_PIN    4
#define LED_ESP_PIN 2

#define LED_ESP_FREQ_ON 250
#define LED_ESP_FREQ_READY 500
#define LED_ESP_FREQ_LIGHT 1000
#define LED_ESP_FREQ_LOOP 3000

#define DEFAULT_BRIGHTNESS 127

//#define LED_EMULATION

#ifndef LED_EMULATION
    extern uint8_t led_state[LED_COUNT*3];


    int led_setup();
    int led_show(uint8_t *ledState);
    int led_clear();
    
    void led_esp_blink(int frequency, int blinks);
    void led_show_status(int16_t temp, int16_t voltage);
#else
    int displayLeds(int *ledState);
#endif

#endif
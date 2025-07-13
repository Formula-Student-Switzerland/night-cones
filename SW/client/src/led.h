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

#define LED_PIN_NC1_1AA 15
#define LED_PIN_NC1_1BB 4
#define LED_ESP_PIN 2

#define LED_ESP_FREQ_ON 250
#define LED_ESP_FREQ_CONNECTED 50

#define LED_DEFAULT_BRIGHTNESS 127

//#define LED_EMULATION

#ifndef LED_EMULATION
    extern uint8_t led_state[LED_COUNT*3];

    void led_setup(uint8_t hw_revision);
    void led_show(uint8_t *ledState);
    void led_clear(void);
    
    void led_esp_blink(int frequency, int blinks);
    void led_show_status(int8_t temp, int16_t voltage);
#else
    int displayLeds(int *ledState);
#endif

#endif
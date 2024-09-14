/****************************)***************************************************/
/* 
 * File: lightmodes.h
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file is used to calculate the different lightmodes decoded from the 
 * received frame.
 *
 * All Lightmodes must have the same signature: 
 * void lightmode_xxx(uint32_t time, lightmode* current_lm, uint8_t *ledState);
 *  inputs: 
 *      time: current time in milliseconds. This value is correctly phaseshifted
 *            against the carrier in the timing module. 
 *      current_lm: The current lightmode structure containing all needed information
 *      ledState: array of 3*LED_COUNT to set all LED colors. 
 * otherwise they will not work as intended.
 */
/*******************************************************************************/
#ifndef LIGHTMODES_H
#define LIGHTMODES_H
#include <stdint.h>

typedef struct {
    uint8_t base_color;
    uint8_t brightness;
    uint8_t repetition_time;
    
    uint8_t color[9];
    void (*lightmode_handler)(); 
} lightmode;


void lightmode_setup(void);
void lightmode_switch(uint8_t color, uint8_t brightness_mode, uint8_t repetition_time);
void lightmode_step (int32_t time, uint8_t *ledState);

// Light Modes
void lightmode_continuous(uint32_t time, lightmode* current_lm, uint8_t *ledState);
void lightmode_blink(uint32_t time, lightmode* current_lm, uint8_t *ledState);
void lightmode_blink_short(uint32_t time, lightmode* current_lm, uint8_t *ledState);
void lightmode_blink_long(uint32_t time, lightmode* current_lm, uint8_t *ledState);
void lightmode_circ(uint32_t time, lightmode* current_lm, uint8_t *ledState);
void lightmode_circ_smooth(uint32_t time, lightmode* current_lm, uint8_t *ledState);
void lightmode_fade(uint32_t time, lightmode* current_lm, uint8_t *ledState);
void lightmode_ident(uint32_t time, lightmode* current_lm, uint8_t *ledState);


#endif
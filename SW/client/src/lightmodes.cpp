/****************************)***************************************************/
/* 
 * File: lightmodes.c
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
#include <stdint.h>
#include "Arduino.h"
#include "lightmodes.h"
#include "color.h"
#include "led.h"
#include "config_store.h"

#define LIGHTMODE_COUNT 16
#define LIGHTMODE_IDENT 0x9
lightmode lightmode_current;

typedef void (*lightmode_function)(uint32_t, lightmode* , uint8_t *) ;
lightmode_function lightmode_current_handler; 

uint8_t lightmode_ident_active;

uint8_t COLOR_DARK[3] = {0,0,0};

const lightmode_function lightmodes[LIGHTMODE_COUNT] =
{ 
  lightmode_continuous, // 00
  lightmode_blink, // 01
  lightmode_blink_short, // 02
  lightmode_blink_long, // 03
  lightmode_circ, // 04
  lightmode_circ_smooth, // 05
  lightmode_fade, // 06
  lightmode_rainbow_fade, // 07
  lightmode_rainbow_circle, // 08
  lightmode_ident, // 09
  lightmode_continuous, // 10
  lightmode_continuous, // 11
  lightmode_continuous, // 12
  lightmode_continuous, // 13
  lightmode_continuous, // 14
  lightmode_continuous // 15
};

/**
 * Initialise the initial light mode. Change settings here. (or later in Header File)
 */
void lightmode_setup(void)
{
    lightmode_switch(config_store.user_settings.fallback_color, config_store.user_settings.fallback_lightmode, 
        config_store.user_settings.fallback_repetition_time);
    lightmode_ident_active = 0;
}

/**
 * Activates the ident mode, which has priority against general lightmode.
 */
void lightmode_activate_ident(void){
    lightmode_switch(0,9,0);
    lightmode_ident_active = 1;
}

/**
 * Deactivates the ident mode, which has priority against general lightmode.
 */
void lightmode_deactivate_ident(void){
    lightmode_ident_active = 0;   
    lightmode_switch(config_store.user_settings.fallback_color, 
    config_store.user_settings.fallback_lightmode, 
    config_store.user_settings.fallback_repetition_time);
}

/**
 * Sets the current mode as fallback (Startup mode)
 */
void lightmode_setAsFallback(void){
    config_store.user_settings.fallback_color = lightmode_current.base_color;
    config_store.user_settings.fallback_lightmode = lightmode_current.brightness | lightmode_current.mode;
    config_store.user_settings.fallback_repetition_time = lightmode_current.repetition_time;
    config_store.user_settings.fallback_phase = 0;
}

/**
 * Switches the new light mode on. This is used to reduce the calculation-
 * amount per iteration to step the color. 
 *
 * @param color              Color code from Frame
 * @param brightness_mode    encoded brightness and mode in one field
 * @param repetition_time    time steps needed for each repetition.         
 * 
 */
void lightmode_switch(uint8_t color, uint8_t brightness_mode, 
                        uint8_t repetition_time){
    if(lightmode_ident_active == 0){
        lightmode_current.repetition_time = repetition_time;
        lightmode_current.mode = (brightness_mode & 0x0F);
        lightmode_current.base_color = color;
        lightmode_current_handler = lightmodes[lightmode_current.mode];
    } 
    lightmode_dim(brightness_mode);
}

/**
 * Dims the current lightmode by reducing the brightness. Does not work with all modes currently
 * @param brightness Current brightness value
 */
void lightmode_dim(uint8_t brightness) {    
    lightmode_current.brightness = (brightness & 0xF0);
    color_decode(lightmode_current.base_color, lightmode_current.brightness, lightmode_current.color);
    
    switch(lightmode_current.mode){
        case 5:
            color_decode(lightmode_current.base_color, lightmode_current.brightness/3*2, &lightmode_current.color[3]);
            color_decode(lightmode_current.base_color, lightmode_current.brightness/3, &lightmode_current.color[6]);
            break;
        case 9: 
            color_decode(COLOR_RED, 0xF0, &lightmode_current.color[0]);
            color_decode(COLOR_GREEN, 0xF0, &lightmode_current.color[3]);
            color_decode(COLOR_GREEN, 0, &lightmode_current.color[6]);
            break;   
        default:
            color_decode(lightmode_current.base_color, 0, &lightmode_current.color[3]);
            color_decode(lightmode_current.base_color, 0, &lightmode_current.color[6]);
    }
}


/**
 * This procedure advances the lightmode pattern by one step. it must be called
 * with 10 Hz frequency. Deviation causes devitation in the pattern. 
 * The phase shift of the pattern must be calculated in the timing block.
 * @param Time       Current Time in millis seconds. This value needs to be phase_shifted.
 * @param ledState   Array of values to define each LED Color.
 */
void lightmode_step (int32_t time, uint8_t *ledState) {

	lightmode_current_handler(time, &lightmode_current, ledState);
}

/**
 * Set all LEDs in ledState to the specified color (arraycopy)
 * @param color      Three value uint8_t array containing the color components.
 * @param ledState   Array of values to define each LED Color.
 */
void lightmode_set_all_led(uint8_t* colors, uint8_t* ledState){
    for (uint8_t k=0; k<LED_COUNT; k++) {
		ledState[k*3] = colors[0];
		ledState[k*3+1] = colors[1];
		ledState[k*3+2] = colors[2];
	}    
}

/**
 * Lightmode 0: continuous illumination in 1 single color. 
 */
void lightmode_continuous(uint32_t time, lightmode* current_lm, uint8_t *ledState) {
	// Assign colors to LED.
    lightmode_set_all_led(current_lm->color, ledState);

}

/**
 * Lightmode 1: 50% Duty blinking
 */
void lightmode_blink(uint32_t time, lightmode* current_lm, uint8_t *ledState) {
    uint32_t current_step;
    if(current_lm->repetition_time == 0)
        current_step = 0;
    else
        current_step = time/50/current_lm->repetition_time;

    if(current_step %2 == 0)
        lightmode_set_all_led(current_lm->color,ledState);
    else
        lightmode_set_all_led(&current_lm->color[3],ledState);
}

/**
 * Lightmode 2: 25% Duty blinking
 */
void lightmode_blink_short(uint32_t time, lightmode* current_lm, uint8_t *ledState) {
    uint32_t current_step;
    if(current_lm->repetition_time == 0)
        current_step = 0;
    else
        current_step = time/25/current_lm->repetition_time;
    
    if(current_step %4 == 0)
        lightmode_set_all_led(current_lm->color,ledState);
    else
        lightmode_set_all_led(&current_lm->color[3],ledState);
    
}

/**
 * Lightmode 3: 75% Duty blinking
 */
void lightmode_blink_long(uint32_t time, lightmode* current_lm, uint8_t *ledState) {
    uint32_t current_step;
    if(current_lm->repetition_time == 0)
        current_step = 0;
    else
        current_step = time/25/current_lm->repetition_time;
    
    if(current_step %4 != 3)
        lightmode_set_all_led(current_lm->color,ledState);
    else
        lightmode_set_all_led(&current_lm->color[3],ledState);
  
}

/**
 * Lightmode 4: Circulating 3 LEDs
 */
void lightmode_circ(uint32_t time, lightmode* current_lm, uint8_t *ledState) {
    uint32_t current_step;
    if(current_lm->repetition_time == 0)
        current_step = 0;
    else
        current_step = time/(100/LED_BOTTOM_COUNT)/current_lm->repetition_time;
    
    lightmode_set_all_led(COLOR_DARK,ledState);
    for(int col=0; col<3; col++)
        for(int i=-1; i<2; i++)
            ledState[3*((current_step+i)%LED_BOTTOM_COUNT)+col] = current_lm->color[col];
}

/**
 * Lightmode 5: Circulating Smooth 3 LEDs
 */
// ToDo: Check here, how to do it smoother... Same Problem as with lighthouse
void lightmode_circ_smooth(uint32_t time, lightmode* current_lm, uint8_t *ledState) {
    uint32_t current_step;
    if(current_lm->repetition_time == 0)
        current_step = 0;
    else
        current_step = time/(100/LED_BOTTOM_COUNT)/current_lm->repetition_time;
    
    lightmode_set_all_led(COLOR_DARK,ledState);
    for(int col=0; col<3; col++){
        ledState[3*((current_step)%LED_BOTTOM_COUNT)+col] = current_lm->color[col];
        ledState[3*((current_step-1)%LED_BOTTOM_COUNT)+col] = current_lm->color[col+3];
        ledState[3*((current_step+1)%LED_BOTTOM_COUNT)+col] = current_lm->color[col+3];
        ledState[3*((current_step-2)%LED_BOTTOM_COUNT)+col] = current_lm->color[col+6];
        ledState[3*((current_step+2)%LED_BOTTOM_COUNT)+col] = current_lm->color[col+6];
    }
}

/**
 * Lightmode 6: Fade Single Color
 */
void lightmode_fade(uint32_t time, lightmode* current_lm, uint8_t *ledState) {
    float current_step;
    if(current_lm->repetition_time == 0)
        current_step = 0;
    else
        current_step = ((time/current_lm->repetition_time)%100)/50.0;
    
    if(current_step > 1)
        current_step = 2-current_step;
    
    color_decode(current_lm->base_color, current_lm->brightness*current_step, current_lm->color);
        
    lightmode_set_all_led(current_lm->color,ledState);
}

/**
 * Lightmode 7: Rainbow fade
 */
void lightmode_rainbow_fade(uint32_t time, lightmode* current_lm, uint8_t *ledState) {
    uint8_t current_step;
    if(current_lm->repetition_time == 0)
        current_step = 0;
    else
        current_step = (224*time/100/current_lm->repetition_time)%224;
    

    color_decode(current_step, current_lm->brightness, current_lm->color);
        
    lightmode_set_all_led(current_lm->color,ledState);
}

/**
 * Lightmode 8: Rainbow circle
 */
void lightmode_rainbow_circle(uint32_t time, lightmode* current_lm, uint8_t *ledState) {
    uint8_t current_step;
    if(current_lm->repetition_time == 0)
        current_step = 0;
    else
        current_step = (224*time/100/current_lm->repetition_time)%224;

    for(int i=0; i<LED_BOTTOM_COUNT; i++){
        current_step = (current_step + 11)%224;
        color_decode(current_step, current_lm->brightness, current_lm->color);
        ledState[3*i+0] = current_lm->color[0];
        ledState[3*i+1] = current_lm->color[1];
        ledState[3*i+2] = current_lm->color[2];
        ledState[3*(16+i/4)+0] = current_lm->color[0];
        ledState[3*(16+i/4)+1] = current_lm->color[1];
        ledState[3*(16+i/4)+2] = current_lm->color[2];
    }
}

/**
 * Lightmode 9: Identification
 */
void lightmode_ident(uint32_t time, lightmode* current_lm, uint8_t *ledState) {
    uint32_t current_step;
    current_step = time/250;
    
    if(current_step %2 == 0)
        lightmode_set_all_led(current_lm->color,ledState);
    else
        lightmode_set_all_led(&current_lm->color[6],ledState);

    ledState[3*4+0] = current_lm->color[3];
    ledState[3*4+1] = current_lm->color[4];
    ledState[3*4+2] = current_lm->color[5];
}




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
#include "lightmodes.h"
#include "color.h"
#include "led.h"

//LED_COUNT
//LED_BOTTOM_COUNT

#define LIGHTMODE_COUNT 16

lightmode lightmode_current;
lightmode_function lightmode_current_handler; 

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
  lightmode_continuous, // 07
  lightmode_continuous, // 08
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
 *
 *
 */
void lightmode_setup(void)
{
    lightmode_current.base_color=0;
    lightmode_current.brightness=0;
    lightmode_current.repetition_time=0;
    for(int i=0; i<9; i++)
      lightmode_current.color[i]=0;
    lightmode_current_handler = lightmodes[0];
}

/**
 * Switches the new light mode on. This is used to reduce the calculation-
 * amount per iteration to step the color. 
 *
 * Inputs: 
 *      color:              Color code from Frame
 *      brightness_mode:    encoded brightness and mode in one field
 *      repetition_time:    time steps needed for each repetition.         
 *      
 * 
 * 
 */
void lightmode_switch(uint8_t color, uint8_t brightness_mode, 
                        uint8_t repetition_time){
    lightmode_current.repetition_time = repetition_time;
    lightmode_current.mode = brightness_mode & 0x0F
    lightmode_current.base_color = color;
    lightmode_current_handler = lightmodes[lightmode_current.mode];
    
    lightmode_dim(brightness_mode);
    
}

/**
 * Dims the current lightmode by reducing the brightness. Does not work with all modes currently
 * @param brightness Current brightness value
 */
void lightmode_dim(uint8_t brightness) {    
    lightmode_current.brightness = brightness & 0xF0;
    color_decode(color, lightmode_current.brightness, lightmode_current.color);
    
    switch(lightmode_current.mode){
        case 5:
            color_decode(color, lightmode_current.brightness/3*2, &lightmode_current.color[3]);
            color_decode(color, lightmode_current.brightness/3, &lightmode_current.color[6]);
            break;
        case 9: 
            color_decode(48, 0xF0, &lightmode_current.color[3]);            
        default:
            color_decode(color, 0, &lightmode_current.color[3]);
            color_decode(color, 0, &lightmode_current.color[6]);
    }
}


/**
 * This procedure advances the lightmode pattern by one step. it must be called
 * with 10 Hz frequency. Deviation causes devitation in the pattern. 
 * The phase shift of the pattern must be calculated in the timing block.
 * Inputs: 
 *      Time:       Current Time in millis seconds. This value needs to be phase_shifted.
 *      ledState:   Array of values to define each LED Color.
 */
void lightmode_step (int32_t time, uint8_t *ledState) {

	lightmode_current_handler(time, &lightmode_current, ledState);
}

/**
 * Set all LEDs in ledState to the specified color (arraycopy)
 *      color:      Three value uint8_t array containing the color components.
 *      ledState:   Array of values to define each LED Color.
 *
 *
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
        current_step = time/400/current_lm->repetition_time;
    
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
        current_step = time/200/current_lm->repetition_time;
    
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
        current_step = time/200/current_lm->repetition_time;
    
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
        current_step = ((uint32_t)(time/100.0/current_lm->repetition_time))%2;
    
    if(current_step > 1)
        current_step = 2-current_step;
    
    color_decode(current_lm->base_color, current_lm->brightness*current_step, current_lm->color);
        
    lightmode_set_all_led(current_lm->color,ledState);
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
        lightmode_set_all_led(&current_lm->color[3],ledState);
        ledState[3*3+0] = current_lm->color[0];
        ledState[3*3+1] = current_lm->color[1];
        ledState[3*3+2] = current_lm->color[2];
}




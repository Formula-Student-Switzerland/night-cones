/****************************)***************************************************/
/* 
 * File: sync.h
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file is used to to synchronize the cones to the server and introduce the
 * necessary phase shift. 
 */
/*******************************************************************************/
#include <stdint.h>
#include <arduino.h>
#include "sync.h"

typedef struct{    
    uint16_t led_period;
    uint32_t time;
    int32_t time_offset;
    int32_t phase_increment;
} sync_settings;


sync_settings sync_setting;

/**
 * Initializes the synchronization module
 *  Inputs:
 *      led_period: LED Period in millisecods
 */
void sync_setup(uint16_t led_period){
    sync_setting.led_period = led_period;

}

/**
 * Gets the current time and checks if the lightmode task must be executed.
 *
 * Outputs: 
 *      time: The current local time for use with lightmodes
 * Return: True if the lightmode task shall be executed. 
 */
bool sync_loop(uint32_t* time){
    
    sync_setting.time = millis()-sync_setting.time_offset;
    *time = sync_setting.time;
    return (sync_setting.time%sync_setting.led_period ==0);
}

/**
 * Reconfigure the sync module with new lightmode settings. 
 *  Inputs: 
 *      repetition_time: Repetition time from frame header. 
 *      phase_shift:     Phase shift from frame header
 */
void sync_reconfigure(uint8_t repetition_time, uint8_t phase_shift){
    sync_setting.phase_increment = phase_shift*repetition_time*100/255;
}

/**
 * Synchronize the local timer with the received time stamp
 *  Inputs: 
 *      rx_timestamp:   32 Bit milli seconds time stamp from received frame. 
 *
 * TODO: Check if filtering of time_offset is necessary.
 */
void sync_synchronize(uint32_t rx_timestamp){
    sync_setting.time_offset = millis()-rx_timestamp-sync_setting.phase_increment;
}
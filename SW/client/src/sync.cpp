
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
} sync_settings_t;


sync_settings_t sync_setting;

/**
 * Initializes the synchronization module
 * 
 *  @param led_period: LED Period in millisecods
 */
void sync_setup(uint16_t led_period){
    sync_setting.led_period = led_period;
    sync_setting.time_offset = 0;
    sync_setting.time = 0;
    sync_setting.phase_increment = 0;

}

/**
 * Gets the current time and checks if the lightmode task must be executed.
 *
 * @param  time The current local time for use with lightmodes
 * @return True if the lightmode task shall be executed. 
 */
bool sync_loop(uint32_t* time){
    
    sync_setting.time = millis()-sync_setting.time_offset;
    *time = sync_setting.time;
    return (sync_setting.time%sync_setting.led_period ==0);
}

/**
 * Reconfigure the sync module with new lightmode settings. 
 * @param repetition_time  Repetition time from frame header. 
 * @param  phase_shift     Phase shift from frame header
 */
void sync_reconfigure(uint8_t repetition_time, uint8_t phase_shift){
    sync_setting.phase_increment = phase_shift*repetition_time*100/255;
}

/**
 * Synchronize the local timer with the received time stamp
 * @param rx_timestamp   32 Bit milli seconds time stamp from received frame. 
 *
 * TODO: Check if filtering of time_offset is necessary.
 */
void sync_synchronize(uint32_t rx_timestamp){
    sync_setting.time_offset = millis()-(uint32_t)rx_timestamp-sync_setting.phase_increment;
}

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
#include <ESP1588.h>

typedef struct{    
    uint16_t led_period;
    uint32_t time;
    int32_t time_offset;
    int32_t phase_increment;
} sync_settings_t;

// SmoothTimeLoop timeloop(1000*NUM_LEDS,20);
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

    esp1588.SetDomain(0);
    esp1588.Begin();
}

/**
 * Gets the current time and checks if the lightmode task must be executed.
 *
 * @param  time The current local time for use with lightmodes
 * @return True if the lightmode task shall be executed. 
 */
bool sync_loop(uint32_t* time){
    esp1588.Loop();
    sync_print_PTP_status();
    sync_setting.time = esp1588.GetMillis()-sync_setting.time_offset;
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
    sync_setting.time_offset = /*millis()-(uint32_t)rx_timestamp*/-sync_setting.phase_increment;
}

void PrintPTPInfo(ESP1588_Tracker &t)
{
    const PTP_ANNOUNCE_MESSAGE &msg = t.GetAnnounceMessage();
    const PTP_PORTID &pid = t.GetPortIdentifier();

    Serial.printf("    %s: ID ", t.IsMaster() ? "Master   " : "Candidate");
    for (int i = 0; i < (int)(sizeof(pid.clockId) / sizeof(pid.clockId[0])); i++)
    {
        Serial.printf("%02x ", pid.clockId[i]);
    }

    Serial.printf(" Prio %3d ", msg.grandmasterPriority1);

    Serial.printf(" %i-step", t.IsTwoStep() ? 2 : 1);

    Serial.printf("\n");
}

void sync_print_PTP_status(void){
    static uint32_t last_millis = 0;
    if (((esp1588.GetMillis() + 250) / 4000) != ((last_millis + 250) / 4000)) // print a status message every four seconds, slightly out of sync with the LEDs blinking for improved blink accuracy.
    {
        last_millis = esp1588.GetMillis();

        ESP1588_Tracker &m = esp1588.GetMaster();
        ESP1588_Tracker &c = esp1588.GetCandidate();

        Serial.printf("PTP status: %s   Master %s, Candidate %s\n", esp1588.GetLockStatus() ? "LOCKED" : "UNLOCKED", m.Healthy() ? "OK" : "no", c.Healthy() ? "OK" : "no");

        // this function is defined below, prints out the master and candidate clock IDs and some other info.
        PrintPTPInfo(m);
        PrintPTPInfo(c);

        Serial.printf("\n");
    }
}


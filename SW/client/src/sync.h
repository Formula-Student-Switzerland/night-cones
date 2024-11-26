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
#ifndef SYNC_H
#define SYNC_H

#include <stdint.h>
#include <arduino.h>

void sync_setup(uint16_t led_period);

bool sync_loop(uint32_t* time);
void sync_reconfigure(uint8_t repetition_time, uint8_t phase_shift);
void sync_synchronize(uint64_t rx_timestamp);


#endif
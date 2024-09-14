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

void sync_setup(void);

bool sync_loop(void);
void sync_reconfigure(uint8_t repetition_time, uint8_t phase_shift);
void sync_synchronize(uint32_t rx_timestamp);


#endif
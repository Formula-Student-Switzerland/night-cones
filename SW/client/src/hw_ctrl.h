/****************************)***************************************************/
/* 
 * File: hw_ctrl.h
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file contains a simple driver for hardware functions (Turnoff and Hall)
 */
/*******************************************************************************/
#ifndef HW_CTRL
#define HW_CTRL
#include <stdint.h>
#define KILL_PIN_NC1_1AA 13
#define HALL_PIN_NC1_1AA 14
#define KILL_PIN_NC1_1BB 12
#define HALL_PIN_NC1_1BB 16

void hw_ctrl_setup(uint8_t hw_revision);

/**
 * Get the state of the hall sensor
 * 
 * @return True if Hall sensor is used.
 */
uint8_t hw_ctrl_get_hall_state(void);

/**
 * Turn off the Cone
 */
void hw_ctrl_turn_off(void);




#endif
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

#define KILL_PIN  12
#define HALL_PIN  16

void hw_ctrl_setup(void);

/**
 * Get the state of the hall sensor
 * 
 * @return True if Hall sensor is used.
 */
#define hw_ctrl_get_hall_state(void) digitalRead(HALL_PIN);

/**
 * Turn off the Cone
 */
#define hw_ctrl_turn_off(void) digitalWrite(KILL_PIN,1)


#endif
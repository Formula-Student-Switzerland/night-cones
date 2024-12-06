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
#include "hw_ctrl.h"
#include "Arduino.h"

/**
 * Setups the HW Ctrl pins
 */
void hw_ctrl_setup(void){
  pinMode(KILL_PIN, OUTPUT);
  pinMode(HALL_PIN, INPUT);
}


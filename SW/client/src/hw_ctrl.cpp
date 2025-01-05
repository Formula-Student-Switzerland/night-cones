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
void hw_ctrl_setup(void)
{
  pinMode(KILL_PIN, OUTPUT);
  pinMode(HALL_PIN, INPUT);
}

uint8_t hw_ctrl_get_hall_state(void)
{
  return digitalRead(HALL_PIN);
}

/**
 * Turn off the Cone
 */
void hw_ctrl_turn_off(void)
{
  analogWriteFreq(10000);
  analogWrite(KILL_PIN, 128);
}

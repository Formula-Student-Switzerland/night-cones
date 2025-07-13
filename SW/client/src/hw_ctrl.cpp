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

uint8_t hw_ctrl_kill_pin;
uint8_t hw_ctrl_hall_pin;

/**
 * Setups the HW Ctrl pins
 */
void hw_ctrl_setup(uint8_t hw_revision)
{
  switch (hw_revision)
  {
  case 1:
    hw_ctrl_hall_pin = HALL_PIN_NC1_1AA;
    hw_ctrl_kill_pin = KILL_PIN_NC1_1AA;
    break;
  case 2:
    hw_ctrl_hall_pin = HALL_PIN_NC1_1BB;
    hw_ctrl_kill_pin = KILL_PIN_NC1_1BB;
    break;

  default:
    break;
  }
  pinMode(hw_ctrl_kill_pin, OUTPUT);
  pinMode(hw_ctrl_hall_pin, INPUT);
}

uint8_t hw_ctrl_get_hall_state(void)
{
  return digitalRead(hw_ctrl_hall_pin);
}

/**
 * Turn off the Cone
 */
void hw_ctrl_turn_off(void)
{
  analogWriteFreq(10000);
  analogWrite(hw_ctrl_kill_pin, 128);
}

#include "hw_ctrl.h"
#include "Arduino.h"

/**
 * Setups the HW Ctrl pins
 */
void hw_Ctrl_setup(void){
  pinMode(KILL_PIN, OUTPUT);
  pinMode(HALL_PIN, INPUT);
}

/**
 * Get the state of the hall sensor
 * 
 * @return True if Hall sensor is used.
 */
bool hw_ctrl_get_hall_state(void){
    return digitalRead(HALL_PIN);
}

/**
 * Turn off the Cone
 */
void hw_ctrl_turn_off(void) {
  digitalWrite(KILL_PIN,1);
}

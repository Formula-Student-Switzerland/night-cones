

#include "hw_ctrl.h"
#include "Arduino.h"

void hw_Ctrl_setup(void){
  pinMode(KILL_PIN, OUTPUT);
  pinMode(HALL_PIN, INPUT);
}

bool hw_ctrl_get_hall_state(void){
    return digitalRead(HALL_PIN);
}

void hw_ctrl_turn_off(void) {
  digitalWrite(KILL_PIN,1);
}

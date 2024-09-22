#ifndef HW_CTRL
#define HW_CTRL

#define KILL_PIN  12
#define HALL_PIN  16

void hw_Ctrl_setup(void);

bool hw_ctrl_get_hall_state(void);
void hw_ctrl_turn_off(void);


#endif
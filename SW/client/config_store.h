/****************************)***************************************************/
/* 
 * File: config_store.h
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file is used to access the emulated EEPROM on the Nightcone Device.
 */
/*******************************************************************************/
#ifndef CONFIG_STORE_H
#define CONFIG_STORE_H
#include <stdint.h>

#define CONFIG_STORE_SW_REV_MAJ 0x0
#define CONFIG_STORE_SW_REV_MIN 0x99

enum config_store_ids{
    HARDWARE_REVISION, 
    CONE_SERIAL_NUMBER,
    CONE_ID,
    FALLBACK_LIGHTMODE,
    FALLBACK_COLOR, 
    
};




void config_store_setup(void);

int config_store_read(void);

int config_store_store(void);

int config_store_get(int id);


#endif
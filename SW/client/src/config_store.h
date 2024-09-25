/****************************)***************************************************/
/* 
 * File: config_store.h
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file is used to access the EEPROM on the Nightcone Device.
 */
/*******************************************************************************/
#ifndef CONFIG_STORE_H
#define CONFIG_STORE_H
#include <stdint.h>

#define CONFIG_STORE_SW_REV_MAJ 0x0
#define CONFIG_STORE_SW_REV_MIN 0x99

#define CONFIG_STORE_PSVN 0x1 // Version of the persistant storage

#define CONFIG_STORE_HARDWARE_DATA_SIZE 20
#define CONFIG_STORE_USER_SETTINGS_SIZE 28

typedef struct{
    uint8_t hardware_revision;
    uint16_t serial_number;
} hardware_data_t;

typedef struct{
    uint16_t cone_id;
    uint8_t fallback_lightmode;
    uint8_t fallback_color;
    uint8_t fallback_phase;
    uint8_t fallback_repetition_time;
    uint8_t fallback_config; 
} user_settings_t;



typedef struct{
    uint8_t psvn;
    uint8_t header_reserved[7]; // Used to align to page size
    hardware_data_t hardware_data;
    uint8_t hardware_data_reserved[CONFIG_STORE_HARDWARE_DATA_SIZE-sizeof(hardware_data_t)];
    uint32_t hardware_data_crc;
    user_settings_t user_settings;
    uint8_t user_settings_reserved[CONFIG_STORE_HARDWARE_DATA_SIZE-sizeof(user_settings_t)];
    uint32_t user_settings_crc;
}  config_store_t;


enum config_store_ids{
  CONFIG_ID_HW_REV = 0,
  CONFIG_ID_SERIAL_NO,
  CONFIG_ID_CONE_ID,
  CONFIG_ID_FALLBACK_LM,
  CONFIG_ID_TURN_OFF,
  CONFIG_ID_ADC_VOLTAGE,
  CONFIG_ID_ADC_TEMP,
  CONFIG_ID_DEBUG1,
  CONFIG_ID_DEBUG2,
  CONFIG_ID_DEBUG3,
  CONFIG_ID_DEBUG4,
  CONFIG_ID_END
};





extern config_store_t config_store;
//ToDo: Add CRC

void config_store_setup(void);

int config_store_read(void);

int config_store_store(void);

#endif
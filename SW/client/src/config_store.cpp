#include "i2ceeprom.h"
#include "config_store.h"

config_store_t config_store;

/**
 * Configure Config store with defaults and load data from EEPROM.
 *
 */
void config_store_setup(void){
    config_store.hardware_data.hardware_revision=0x2;
    config_store.hardware_data.serial_number = 0x00;

    config_store.user_settings.cone_id = 0x0;
    config_store.user_settings.fallback_lightmode = 0x0;
    config_store.user_settings.fallback_color = 0x0;
    config_store.user_settings.fallback_phase = 0x0;
    config_store.user_settings.fallback_repetition_time = 0x0;
    config_store.user_settings.fallback_config = 0x0;
}

/**
 * Read the config store from EEPROM
 *
 */
int config_store_read(void){
    config_store_t temp;
    
    // Read storage from EEPROM
    
    // Check Version
    
    // Check CRC
    
    // Handle old version / Upgrade
    
        return -1;
}

/**
 * Store the config to the EEPROM
 *
 */
int config_store_store(void){
    
    // Write the config store to the EEPROM
    
    // Check that the hardware information can not be read.
    return -1;
}

/**
 * Calculate the CRC for specific message.
 *
 */
uint32_t config_store_crc32b(uint8_t *message, uint16_t length) {
   uint32_t byte, crc, mask;

   crc = 0xFFFFFFFF;
  for(int i = 0; i<length; i++) {
      byte = message[i];            // Get next byte.
      crc = crc ^ byte;
      for (int j = 7; j >= 0; j--) {    // Do eight times.
         mask = -(crc & 1);
         crc = (crc >> 1) ^ (0xEDB88320 & mask);
      }
   }
   return ~crc;
}






#include "i2ceeprom.h"
#include "config_store.h"

config_store_t config_store;

void config_store_setup(void){
    config_store.hardware_data.hardware_revision=0x2;
    config_store.hardware_data.serial_number = 0x00;

    config_store.user_settings.cone_id = 0x0;
    config_store.user_settings.fallback_lightmode = 0x0;
    config_store.user_settings.fallback_color = 0x0;
    config_store.user_settings.fallback_phase = 0x0;
    config_store.user_settings.fallback_repetition_time = 0x0;
    config_store.user_settings.fallback_config = 0x0;
} user_settings_t;
}

int config_store_read(void){
    config_store_t temp;
    
    // Read storage from EEPROM
    
    // Check Version
    
    // Check CRC
    
    // Handle old version / Upgrade
    
    
}


int config_store_store(void){
    
    // Write the config store to the EEPROM
    
    // Check that the hardware information can not be read.
}

void config_store_set_wifi(uint16_t id, uint32_t value){
    
}

void config_store_get_wifi(uint32_t *out_values) {
    
    
}





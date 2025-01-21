#include "i2cEeprom.h"
#include "config_store.h"
#include "Arduino.h"
#include "Wire.h"
#include "HardwareSerial.h"
#include <EEPROM.h>
#define DEBUG

#define CONFIG_STORE_SDA_PIN 2
#define CONFIG_STORE_SCL_PIN 14

#define CONFIG_STORE_EEPROM_HEADER_BASE_ADDRESS 0
#define CONFIG_STORE_EEPROM_HEADER_SIZE 8
#define CONFIG_STORE_EEPROM_HARDWARE_DATA_BASE_ADDRESS 8
#define CONFIG_STORE_EEPROM_USER_SETTIGS_BASE_ADDRESS 32
#define CONFIG_STORE_EEPROM_SIZE 256
#define CONFIG_STORE_EEPROM_PAGE_SIZE 8
#define CONFIG_STORE_EEPROM_ADDRESS 0xA0

#define CONFIG_STORE_EEPROM_USED_SIZE (CONFIG_STORE_EEPROM_HEADER_SIZE + CONFIG_STORE_HARDWARE_DATA_SIZE + \
                                       4 + CONFIG_STORE_USER_SETTINGS_SIZE + 4)

config_store_t config_store;
TwoWire I2C;
bool externalEEprom;

/**
 * Configure Config store with defaults and load data from EEPROM.
 *
 */
void config_store_setup(void)
{
    I2C = TwoWire();
    I2C.begin(CONFIG_STORE_SDA_PIN, CONFIG_STORE_SCL_PIN);
    I2C.setClock(5000);
    i2c_eeprom_init(&I2C);
    i2c_eeprom_set_address(CONFIG_STORE_EEPROM_ADDRESS);
    i2c_eeprom_set_memory_size(CONFIG_STORE_EEPROM_SIZE);
    i2c_eeprom_set_page_size(CONFIG_STORE_EEPROM_PAGE_SIZE);

    if(i2c_eeprom_is_ready()){
        externalEEprom = true;
    } else {
        externalEEprom = false;
        EEPROM.begin(CONFIG_STORE_EEPROM_USED_SIZE);
    }
    config_store_read();

}

/**
 * Upgrades the Input config_store_t to the current version by
 * using default values.
 *
 * @param temp Reference to config_store_t to upgrade.
 */
void config_store_upgrade(config_store_t *temp)
{

    // Check if Storage of the Hardware part is necessary.
    // Write Version Number
#ifdef DEBUG
    Serial.printf("Upgrade Storage with from Version 0x%X to 0x%X\r\n", temp->psvn, CONFIG_STORE_PSVN);
#endif
    switch (temp->psvn)
    {
    case 0x6:
        memset(temp, 0, sizeof(config_store_t));
        temp->hardware_data.hardware_revision = 0x0;
        temp->hardware_data.serial_number = 0x7777;
        temp->user_settings.cone_id = 0x0;
        temp->user_settings.fallback_lightmode = 0x20;
        temp->user_settings.fallback_color = 0x8A;
        temp->user_settings.fallback_phase = 0x0;
        temp->user_settings.fallback_repetition_time = 0x0;
        break;
    default:
        break;
    }
    temp->psvn = CONFIG_STORE_PSVN;
}

/**
 * Calculate the CRC for specific message.
 *
 * @param message Pointer to the message to be CRCed
 * @param length  Number of bytes to calculate
 *
 * @return Returns the CRC value.
 *
 */
uint32_t config_store_crc32b(uint8_t *message, uint16_t length)
{
    uint32_t byte, crc, mask;

    crc = 0xFFFFFFFF;
    for (int i = 0; i < length; i++)
    {
        byte = message[i]; // Get next byte.
        crc = crc ^ byte;
        for (int j = 7; j >= 0; j--)
        { // Do eight times.
            mask = -(crc & 1);
            crc = (crc >> 1) ^ (0xEDB88320 & mask);
        }
    }
    return ~crc;
}

/**
 * Read the config store from EEPROM
 *
 * @return Returns 0 when the storage is correctly loaded. Error code otherwise
 *
 */
int config_store_read(void)
{
    config_store_t temp;
    uint32_t crc;
    if(externalEEprom){
        if (i2c_eeprom_read(CONFIG_STORE_EEPROM_HEADER_BASE_ADDRESS, (uint8_t *)&temp,
                        CONFIG_STORE_EEPROM_USED_SIZE))
        {
#ifdef DEBUG
            printf("Reading EEPROM failed\n!");
#endif
            return -1;
        }
    } else {
        EEPROM.get(CONFIG_STORE_EEPROM_HEADER_BASE_ADDRESS, temp);
    }

    if (temp.psvn != CONFIG_STORE_PSVN)
    {
#ifdef DEBUG
        printf("PSVN not matching. Upgrade will be performed.\r\n");
#endif
        config_store_upgrade(&temp);
        memcpy(&config_store, &temp, sizeof(config_store_t));
        config_store_storeHW();
        config_store_store();
        return 0;
    }

    crc = config_store_crc32b((uint8_t *)&temp.hardware_data, CONFIG_STORE_HARDWARE_DATA_SIZE);

    if (crc != temp.hardware_data_crc)
    {
#ifdef DEBUG
        printf("Hardware Data CRC not matching!\r\n %x != %x\r\n", crc, temp.hardware_data_crc);
#endif
        memcpy(&config_store, &temp, sizeof(config_store_t));
        return -2;
    }

    crc = config_store_crc32b((uint8_t *)&temp.user_settings, CONFIG_STORE_USER_SETTINGS_SIZE);

    if (crc != temp.user_settings_crc)
    {
#ifdef DEBUG
        printf("User Settings CRC not matching!\r\n");
#endif
        return -3;
    }
    memcpy(&config_store, &temp, sizeof(config_store_t));

#ifdef DEBUG
    printf("EEPROM Read Successful!\n");
#endif

    return 0;
}

/**
 * Store the config to the EEPROM. This function only stores the
 * user settings part.
 *
 * @return Returns 0, if sucessful, otherwise returns error code.
 *
 */
int config_store_store(void)
{
    uint8_t buffer[8];
    uint8_t result = 0;
    config_store.user_settings_crc = config_store_crc32b((uint8_t *)&config_store.user_settings, CONFIG_STORE_USER_SETTINGS_SIZE);

    if(externalEEprom){
        for (uint8_t i = 0; i < CONFIG_STORE_USER_SETTINGS_SIZE + 4; i += 8)
        {
        
            result += i2c_eeprom_read(CONFIG_STORE_EEPROM_USER_SETTIGS_BASE_ADDRESS + i, buffer, 8);
        
            // Only write page if needed.
            if (memcmp(buffer, ((uint8_t *)&config_store.user_settings) + i, 8) != 0)
            {
#ifdef DEBUG
                printf("EEPROM Write page %i!\n", i);
#endif
                result += i2c_eeprom_write(CONFIG_STORE_EEPROM_USER_SETTIGS_BASE_ADDRESS + i, ((uint8_t *)&config_store.user_settings) + i, 8);
            }
        } 
    } else {
        EEPROM.put(CONFIG_STORE_EEPROM_USER_SETTIGS_BASE_ADDRESS, config_store.user_settings);
        EEPROM.put(CONFIG_STORE_EEPROM_USER_SETTIGS_BASE_ADDRESS + CONFIG_STORE_USER_SETTINGS_SIZE, config_store.user_settings_crc);
        EEPROM.commit();
    }
 
    return result;
}

/**
 * Stores the Hardware Information in the EEPROM.
 * THIS FUNCTION MUST ONLY BE CALLED BY COMMANDLINE!
 *
 * @return Returns 0, if sucessful, otherwise returns error code.
 *
 */
int config_store_storeHW(void)
{
    uint8_t buffer[8];
    uint8_t result = 0;
    config_store.hardware_data_crc = config_store_crc32b((uint8_t *)&config_store.hardware_data, CONFIG_STORE_HARDWARE_DATA_SIZE);

    if(externalEEprom) {
        for (uint8_t i = 0; i < CONFIG_STORE_EEPROM_HEADER_SIZE + CONFIG_STORE_HARDWARE_DATA_SIZE + 4; i += 8)
        {
            result += i2c_eeprom_read(CONFIG_STORE_EEPROM_HEADER_BASE_ADDRESS + i, buffer, 8);
            // Only write page if needed.
            if (memcmp(buffer, ((uint8_t *)&config_store) + i, 8) != 0)
            {
                result += i2c_eeprom_write(CONFIG_STORE_EEPROM_HEADER_BASE_ADDRESS + i, ((uint8_t *)&config_store) + i, 8);
            }
        }
    } else {
        EEPROM.put(CONFIG_STORE_EEPROM_HEADER_BASE_ADDRESS, config_store.psvn);
        EEPROM.put(CONFIG_STORE_EEPROM_HARDWARE_DATA_BASE_ADDRESS, config_store.hardware_data);
        EEPROM.put(CONFIG_STORE_EEPROM_HARDWARE_DATA_BASE_ADDRESS + CONFIG_STORE_HARDWARE_DATA_SIZE, config_store.hardware_data_crc);
        EEPROM.commit();
    }
    return result;
}

/**
 * Used to query, if an external EEPROM is detected.
 * Returns 1 of an external EEPROM is fitted. 
 * Returns 0 if the internal EEPROM is used.
 *
 * @return Returns EEPROM selection
 *
 */
int config_store_get_external(void)
{
    return externalEEprom;    
}

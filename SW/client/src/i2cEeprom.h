/****************************)***************************************************/
/* 
 * File: i2cEeprom.h
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file contains a simple driver for the external i2c EEPROM
 */
/*******************************************************************************/
#ifndef I2CEEPROM_H
#define I2CEEPROM_H
#include <stdint.h>
#include "Arduino.h"
#include "Wire.h"


#define I2C_EEPROM_BASE_ADDRESS 0x50

struct i2c_eeprom_settings_struct{
  uint8_t i2c_address;
  uint32_t memory_size;
  uint32_t page_size;
  uint8_t write_delay_ms;
  bool write_complete_polling;
};

class i2c_eeprom{
  public: 
    i2c_eeprom(TwoWire *w);    

    void set_address(uint8_t addr);
    uint8_t read(uint16_t addr);
    uint8_t read(uint16_t addr, uint8_t* data_out, uint8_t count);

    uint8_t write(uint16_t addr, uint8_t data);
    uint8_t write(uint16_t addr, uint8_t* data, uint8_t count);

    bool is_ready(uint8_t i2c_addr = 255);

    uint32_t length();

    void erase(uint8_t value = 0);
    void set_memory_size(uint32_t size);
    void set_page_size(uint32_t size);
    void set_write_delay_ms(uint8_t time);

    void enable_write_complete_polling();
    void disable_write_complete_polling();
  private: 
    TwoWire *wire;

    i2c_eeprom_settings_struct i2c_eeprom_settings = {
      .i2c_address  = I2C_EEPROM_BASE_ADDRESS, // 0x30 - 0x39
      .memory_size=256,
      .page_size = 8,
      .write_delay_ms = 5,
      .write_complete_polling=true
    };
};

#endif
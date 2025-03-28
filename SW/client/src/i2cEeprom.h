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

  void i2c_eeprom_init(TwoWire *w);

  void i2c_eeprom_set_address(uint8_t addr);
  uint8_t i2c_eeprom_read(uint16_t addr);
  uint8_t i2c_eeprom_read(uint16_t addr, uint8_t *data_out, uint8_t count);

  uint8_t i2c_eeprom_write(uint16_t addr, uint8_t data);
  uint8_t i2c_eeprom_write(uint16_t addr, uint8_t *data, uint8_t count);

  bool i2c_eeprom_is_ready(uint8_t i2c_addr = 255);

  uint32_t i2c_eeprom_length();

  void i2c_eeprom_erase(uint8_t value = 0);
  void i2c_eeprom_set_memory_size(uint32_t size);
  void i2c_eeprom_set_page_size(uint32_t size);
  void i2c_eeprom_set_write_delay_ms(uint8_t time);

  void i2c_eeprom_enable_write_complete_polling();
  void i2c_eeprom_disable_write_complete_polling();

#endif
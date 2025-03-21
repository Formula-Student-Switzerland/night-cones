/****************************)***************************************************/
/* 
 * File: i2cEeprom.cpp
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file contains a simple driver for the external i2c EEPROM
 */
/*******************************************************************************/
#include "i2cEeprom.h"
#include <stdint.h>
#include "Wire.h"
#include "Arduino.h"
#include "HardwareSerial.h"

TwoWire *i2c_interface_wire;

i2c_eeprom_settings_struct i2c_eeprom_settings;

/**
 * Initialise EEPROM structure with I2C (TwoWire)
 * 
 * @param w Reference to the TwoWire Class
 */
void i2c_eeprom_init(TwoWire *w){
  i2c_interface_wire = w;
  i2c_eeprom_settings.i2c_address = I2C_EEPROM_BASE_ADDRESS;
  i2c_eeprom_settings.memory_size = 256;
  i2c_eeprom_settings.page_size = 8;
  i2c_eeprom_settings.write_delay_ms = 5;
  i2c_eeprom_settings.write_complete_polling = true;
}

/**
 * Sets the I2C Adress of the Memory. 
 * Attention: Address must be left aligned. 
 * 
 * @param addr Left aligned address of the EEPROM
 *
 */
void i2c_eeprom_set_address(uint8_t addr){
  i2c_eeprom_settings.i2c_address = addr>>1;
}

/**
 * Check if the EEPROM is ready to receive commands
 * 
 * @param i2c_addr Optional address. Default 0xFF will use preconfigured address
 * 
 * @return Returns true, if the EEPROM is ready to receive commands.
 *
 */
bool i2c_eeprom_is_ready(uint8_t i2c_addr){
  uint8_t status;
  if (i2c_addr == 255)
    i2c_addr = i2c_eeprom_settings.i2c_address;

  i2c_interface_wire->beginTransmission((uint8_t)i2c_addr);
  status = i2c_interface_wire->endTransmission();
  return (status == 0);
}

/**
 * Read one single byte from the EEPROM at addr
 * 
 * @param address of the byte to be read.
 * 
 * @return Value at addr
 *
 */
uint8_t i2c_eeprom_read(uint16_t addr)
{
  uint8_t data;
  i2c_eeprom_read(addr, &data, 1);
  return data;
}

/**
 * Read multiple consequtive bytes from the EEPROM
 * 
 * @param addr Adress of the first byte
 * @param data_out reference to the byte array to store the read data
 * @param count Number of bytes to read.
 * 
 * @return Returns 0, if sucessful, otherwise returns error code
 *
 */
uint8_t i2c_eeprom_read(uint16_t addr, uint8_t* data_out, uint8_t count){

  while (!i2c_eeprom_is_ready())
  {
    delayMicroseconds(100);
  }

  if(addr+count > i2c_eeprom_settings.memory_size ||count == 0)
    return -1;
  
  i2c_interface_wire->beginTransmission(i2c_eeprom_settings.i2c_address);
  i2c_interface_wire->write(addr);
  uint8_t status = i2c_interface_wire->endTransmission(true);

  if(count != i2c_interface_wire->requestFrom(i2c_eeprom_settings.i2c_address,(uint8_t) count))
    return -2;    

  while (i2c_interface_wire->available())
    *(data_out++) =  i2c_interface_wire->read();
  return status;
}

/**
 * Writes a single byte to EEPROM, if it is not already there
 * 
 * @param addr Adress to write the byte to. 
 * @param data Data to write
 * 
 * @return Returns 0, if sucessful, otherwise returns error code 
 *
 */
uint8_t i2c_eeprom_write(uint16_t addr, uint8_t data){

  // If data is already there, return.
  if (i2c_eeprom_read(addr) == data)
    return 0;

  return i2c_eeprom_write(addr, &data, 1);
}

/**
 * Writes a multiple bytes to EEPROM. This function uses page writes
 * 
 * @param addr Adress to start the write
 * @param data Reference array of data to write
 * @param count Number of bytes to write
 * 
 * @return Returns 0, if sucessful, otherwise returns error code 
 *
 */
uint8_t i2c_eeprom_write(uint16_t addr, uint8_t* data, uint8_t count){
  uint8_t status = 0;
  if(addr+count>i2c_eeprom_settings.memory_size)
    count = i2c_eeprom_settings.memory_size-addr;
  
  uint8_t transferred = 0;
  uint8_t write_count = 0;

  // Check page crossing
  while(transferred < count)
  {
    if((uint32_t)(count - transferred) < i2c_eeprom_settings.page_size)
      write_count = count - transferred;
    else
      write_count = i2c_eeprom_settings.page_size;
    
    if(write_count>1)
    {
      uint16_t addr1=(addr+write_count-1)/i2c_eeprom_settings.page_size;
      if(addr1 > addr/i2c_eeprom_settings.page_size)
        write_count = (addr1+1) * i2c_eeprom_settings.page_size-addr;
    }
    while (!i2c_eeprom_is_ready())
      delayMicroseconds(100);

    i2c_interface_wire->beginTransmission(i2c_eeprom_settings.i2c_address);
    i2c_interface_wire->write(addr);
    
    for(int i=0; i<write_count; i++)
      i2c_interface_wire->write(*(data++));
    
    addr += write_count;
    transferred += write_count;
    status = i2c_interface_wire->endTransmission();

    if(i2c_eeprom_settings.write_complete_polling)
      delay(i2c_eeprom_settings.write_delay_ms);
  }

  return status;
}

/**
 * Get the size of the EEPROM
 * 
 * @return Returns the number of bytes in the memory
 *
 */
uint32_t i2c_eeprom_length(){
  return i2c_eeprom_settings.memory_size;
}

/**
 * Erases the whole EEPROM with the specified value.
 * 
 * @param value Default value to write to all memory locations
 *
 */
void i2c_eeprom_erase(uint8_t value){
  uint8_t zero [i2c_eeprom_settings.page_size];
  for(uint8_t i=0; i<i2c_eeprom_settings.page_size; i++)
    zero[i] = value; 

  for(uint16_t i=0; i<i2c_eeprom_settings.memory_size; i+=i2c_eeprom_settings.page_size)
  {
    i2c_eeprom_write(i, zero, i2c_eeprom_settings.page_size);
  }
}

/**
 * Set the size of the memory
 * 
 * @param size Number of bytes in the EEPROM
 *
 */
void i2c_eeprom_set_memory_size(uint32_t size){
  i2c_eeprom_settings.memory_size = size;
}

/**
 * Set the page size of the memory
 * 
 * @param size Number of bytes in one page
 *
 */
void i2c_eeprom_set_page_size(uint32_t size){
  i2c_eeprom_settings.page_size = size;

}

/**
 * Set the write delay according to datasheet
 * 
 * @param size Number of millisecconds delay when writing one page
 *
 */
void i2c_eeprom_set_write_delay_ms(uint8_t time){
  i2c_eeprom_settings.write_delay_ms = time;

}

/**
 * Enables write polling, which loads the I2C Bus instead of waiting. 
 *
 */
void i2c_eeprom_enable_write_complete_polling(){
  i2c_eeprom_settings.write_complete_polling = true;
}

/**
 * Disables write polling
 */
void i2c_eeprom_disable_write_complete_polling(){
  i2c_eeprom_settings.write_complete_polling = false;
}



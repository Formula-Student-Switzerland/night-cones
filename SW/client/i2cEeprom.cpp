#include "i2cEeprom.h"
#include <stdint.h>

#include "Wire.h"


/* INIT and BASIC FUNCTIONS */

i2c_eeprom::i2c_eeprom(TwoWire *w){
  wire = w;
}

void i2c_eeprom::set_address(uint8_t addr){
  i2c_eeprom_settings.i2c_address = addr;
}


bool i2c_eeprom::is_ready(uint8_t i2c_addr){
  if (i2c_addr == 255)
    i2c_addr = i2c_eeprom_settings.i2c_address;

  wire->beginTransmission((uint8_t)i2c_addr);
  if (wire->endTransmission() == 0)
    return (true);
  return (false);
}

uint8_t i2c_eeprom::read(uint16_t addr)
{
  uint8_t data;
  read(addr,&data,1);
  return data;
}

uint8_t i2c_eeprom::read(uint16_t addr, uint8_t* data_out, uint8_t count){
    
    while(!is_ready())
      delayMicroseconds(100);

    if(addr+count > i2c_eeprom_settings.memory_size)
      return -1;
    
    wire->beginTransmission(i2c_eeprom_settings.i2c_address);
    wire->write(addr);
    uint8_t status = wire->endTransmission(true);
    status += wire->requestFrom(i2c_eeprom_settings.i2c_address,(uint8_t) count);
    for(int i=0; i<count; i++)
      *(data_out++) =  wire->read();
  return status;
}

uint8_t i2c_eeprom::write(uint16_t addr, uint8_t data){

  // If data is already there, return.
  if(read(addr)== data)
    return 0;

  return write(addr,&data,1);
}


uint8_t i2c_eeprom::write(uint16_t addr, uint8_t* data, uint8_t count){
  uint8_t status = 0;
  if(addr+count>i2c_eeprom_settings.memory_size)
    count = i2c_eeprom_settings.memory_size-addr;
  
  uint8_t transferred = 0;
  uint8_t write_count = 0;
  // Check page crossing
  while(transferred < count)
  {
    if(count - transferred < i2c_eeprom_settings.page_size)
      write_count = count - transferred;
    else
      write_count = i2c_eeprom_settings.page_size;
    
    if(write_count>1)
    {
      uint16_t addr1=(addr+write_count-1)/i2c_eeprom_settings.page_size;
      if(addr1 > addr/i2c_eeprom_settings.page_size)
        write_count = (addr1+1) * i2c_eeprom_settings.page_size-addr;
    }
    while(!is_ready())
      delayMicroseconds(100);

    wire->beginTransmission(addr);
    wire->write(addr);
    
    for(int i=0; i<write_count; i++)
      wire->write(*(data++));
    
    addr += write_count;

    status = wire->endTransmission();

    if(i2c_eeprom_settings.write_complete_polling)
      delay(i2c_eeprom_settings.write_delay_ms);
  }

  return status; // 0 if success
}

uint32_t i2c_eeprom::length(){
  return i2c_eeprom_settings.memory_size;
}


void i2c_eeprom::erase(uint8_t value){
  uint8_t zero [i2c_eeprom_settings.page_size];
  for(int i=0; i<i2c_eeprom_settings.page_size; i++)
    zero[i] = value; 

  for(uint16_t i=0; i<i2c_eeprom_settings.memory_size; i+=i2c_eeprom_settings.page_size)
  {
    write(i,zero,i2c_eeprom_settings.page_size);
  }
}

void i2c_eeprom::set_memory_size(uint32_t size){
  i2c_eeprom_settings.memory_size = size;
}

void i2c_eeprom::set_page_size(uint32_t size){
  i2c_eeprom_settings.page_size = size;

}

void i2c_eeprom::set_write_delay_ms(uint8_t time){
  i2c_eeprom_settings.write_delay_ms = time;

}

void i2c_eeprom::enable_write_complete_polling(){
  i2c_eeprom_settings.write_complete_polling = true;
}

void i2c_eeprom::disable_write_complete_polling(){
  i2c_eeprom_settings.write_complete_polling = false;
}



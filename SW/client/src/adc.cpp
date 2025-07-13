/*******************************************************************************/
/*
 * File: adc.h
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file contains the ADC Interface with corresponding conversions
 */
/*******************************************************************************/
#include <stdint.h>
#include <arduino.h>
#include "adc.h"

int16_t adc_volt_meas;
int16_t adc_temp_meas;
uint8_t adc_soc;
uint8_t adc_temp_deg;
uint8_t adc_mux_state;

const float adc_temp_diff[16] = 
    {-0.7812,
     -0.538901768212441,
     -0.291908189390367,
     -0.202393344636474,
     -0.157356458469665,
     -0.131005872085277,
     -0.114310580130207,
     -0.103345139068369,
     -0.0961807998478870,
     -0.0918207417325689,
     -0.0897827048910918,
     -0.0899392673948034,
     -0.0925010234946466,
     -0.0981457831032513,
     -0.108437452951584};
    
const float adc_temp_lookup[16] = 
{
    180,
    138.3070,
    103.8173,
    85.1352,
    72.1820,
    62.1112,
    53.7268,
    46.4110,
    39.7969,
    33.6413,
    27.7648,
    22.0187,
    16.262,
    10.3425,
    4.0612,
    -2.8788    
};

/**
 * Convert the ADC Value to Temperature
 *
 * @param value ADC Value
 *
 * @return Temperature in Degrees
 *
 */
int8_t adc_calc_temp(uint16_t value)
{
    uint8_t selection = value >> 6;
    return int8_t(adc_temp_lookup[selection] + adc_temp_diff[selection] * (value & 0x3F));
};

/**
 * Converts the ADC value to the Voltage in milliVolt
 *
 * @param value ADC Value
 *
 * @return Voltage in millivolt
 *
 */
uint16_t adc_calc_voltage(uint16_t value)
{
    uint32_t temp;
    temp = value * 7625;
    return temp / 1405; // 122/22*1000/1024
}

/**
 * Calculate the SoC based on the voltage
 * 
 * @param voltage Voltage in Millivolt
 * 
 * @return SoC in percent
 *
 */
uint8_t adc_calc_soc(uint16_t voltage)
{
    return (voltage - 3000) / 12;
}

/*
* Setup ADC Mux
*
*/
void adc_setup(void){    
  pinMode(ADC_MUX_PIN, OUTPUT);    
  adc_mux_state = 0;
  adc_volt_meas = 0;
  adc_temp_meas = 0;
  adc_soc = 255;
  digitalWrite(ADC_MUX_PIN, adc_mux_state); 
  // Run for one time to properly init ADC  
  adc_loop();  
}

/*
* Read one ADC channel and switch Mux to the other channel.
*/
void adc_loop(void){
    if(adc_mux_state == ADC_MUX_VOLT){
        adc_volt_meas = adc_calc_voltage(analogRead(ADC_IN));
        adc_soc = adc_calc_soc(adc_volt_meas);
    }
    else{
        adc_temp_meas = analogRead(ADC_IN);
        adc_temp_deg = adc_calc_temp(adc_temp_meas);        
    }
    adc_mux_state ^= 0x1;
    digitalWrite(ADC_MUX_PIN, adc_mux_state);  
}





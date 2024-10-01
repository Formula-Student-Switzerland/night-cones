#include <stdint.h>
#include <arduino.h>
#include "adc.h"

int16_t adc_volt_meas;
int16_t adc_temp_meas;
uint8_t adc_soc;
uint8_t adc_temp_deg;
uint8_t adc_mux_state;

const float adc_temp_diff[16] = 
    { -50,
    -34.4897,
    -18.6821,
    -12.9532,
    -10.0708 ,
    -8.3844,
    -7.3159,
    -6.6141,
    -6.1556,
    -5.8765,
    -5.7461,
    -5.7561,
   -5.9201,
    -6.2813,
    -6.940};
    
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
}

/*
* Read one ADC channel and switch Mux to the other channel.
*/
void adc_loop(void){
    if(adc_mux_state == ADC_MUX_VOLT){
        adc_volt_meas = analogRead(ADC_IN);
    }
    else{
        adc_temp_meas = analogRead(ADC_IN);
        adc_temp_deg = adc_calc_temp(adc_temp_meas);        
    }
    adc_mux_state ^= 0x1;
    digitalWrite(ADC_MUX_PIN, adc_mux_state);  
}


uint8_t adc_calc_temp(uint16_t value) {
    uint8_t selection = value >>6;
    return uint8_t(adc_temp_lookup[selection] + adc_temp_diff[selection]*(value & 0x3F));
};




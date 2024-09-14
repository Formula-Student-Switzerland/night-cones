#include <stdint.h>
#include <arduino.h>
#include "adc.h"

int16_t adc_volt_meas;
int16_t adc_temp_meas;
uint8_t adc_soc;
uint8_t adc_mux_state;

/*
* Setup ADC Mux
*
*/
void adc_setup(void){    
  pinMode(ADC_MUX_PIN, OUTPUT);    
  adc_mux_state = 0;
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
    }
    adc_mux_state ^= 0x1;
    digitalWrite(ADC_MUX_PIN, adc_mux_state);  
}




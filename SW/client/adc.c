
#include "adc.h"

int adc_volt_meas;
int adc_temp_meas;

int adc_mux_state

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
        volt_meas = analogRead(ADC_IN);
    }
    else{
        temp_meas = analogRead(ADC_IN);        
    }
    adc_mux_state ^= 0x1;
    digitalWrite(ADC_MUX_PIN, adc_mux_state);  
}




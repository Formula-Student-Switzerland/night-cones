#ifndef ADC_H
#define ADC_H

#define ADC_MUX_PIN 13
#define ADC_IN   A0

#define ADC_MUX_VOLT 0
#define ADC_MUX_TEMP 1

extern int adc_volt_meas;
extern int adc_temp_meas;


void adc_setup(void);

int adc_loop(void);



#endif
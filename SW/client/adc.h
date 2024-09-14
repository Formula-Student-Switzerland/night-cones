#ifndef ADC_H
#define ADC_H
#include <stdint.h>
#include <arduino.h>

#define ADC_MUX_PIN 13
#define ADC_IN   A0

#define ADC_MUX_VOLT 0
#define ADC_MUX_TEMP 1

extern int16_t adc_volt_meas;
extern int16_t adc_temp_meas;
extern uint8_t adc_soc;

void adc_setup(void);

void adc_loop(void);

#endif
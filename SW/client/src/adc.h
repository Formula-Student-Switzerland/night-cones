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
#ifndef ADC_H
#define ADC_H
#include <stdint.h>
#include <arduino.h>

#define ADC_MUX_PIN 13
#define ADC_IN   A0

#define ADC_MUX_VOLT 0
#define ADC_MUX_TEMP 1

extern int16_t adc_volt_meas;
extern uint8_t adc_temp_deg;
extern uint8_t adc_soc;
extern int16_t adc_temp_meas;

void adc_setup(void);

void adc_loop(void);

#endif
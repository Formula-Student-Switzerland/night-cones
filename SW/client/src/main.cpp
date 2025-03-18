/*******************************************************************************/
/*
 * File: main.cpp
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * Main file for nightcones
 */
/*******************************************************************************/
#include "Arduino.h"
#include "HardwareSerial.h"
#include "adc.h"
#include "cli.h"
#include "color.h"
#include "config_store.h"
#include "hw_ctrl.h"
#include "led.h"
#include "lightmodes.h"
#include "sync.h"
#include "wifi.h"

#define BRIGHTNESS_DEFAULT 0x70



#define WIFI_DELAY_MS 100
#define WIFI_LOOPS    50

const long LED_UPDATE_INTERVAL = 25;  // initial interval at which to blink (milliseconds)

void setup() {
  // Setup Hardware
  Serial.begin(115200);
  delay(2000);
  config_store_setup();
  hw_ctrl_setup(config_store.hardware_data.hardware_revision);
  adc_setup();
  sync_setup(LED_UPDATE_INTERVAL);

  // LED setup
  led_setup(config_store.hardware_data.hardware_revision);
  lightmode_setup();

  // Init LEDs with blue
  // In case the Default mode would turn off everything, we first need to
  // wake the failsafe by switching shortly to blue and then go to black.
  lightmode_switch(COLOR_BLUE, 0x20, 0);
  lightmode_step(0, led_state); // Is used to activate the lightmode
  led_show(led_state);

  delay(500);
  wifi_setup();
  // Switch to default lightmode
  led_show(led_state);
  lightmode_switch(config_store.user_settings.fallback_color,
                   config_store.user_settings.fallback_lightmode,
                   config_store.user_settings.fallback_repetition_time);
  lightmode_step(0, led_state);
  led_show(led_state);
  cli_init();
}

void loop()
{

  wifi_loop();

  cli_loop();

  uint32_t currentMillis;
  if (sync_loop(&currentMillis))
  {

    lightmode_step(currentMillis, led_state);
    // ToDo Implement Dimming here. 
    /*if (adc_temp_deg < 20)
    {
      // lightmode_dim(BRIGHTNESS_DEFAULT);
    }
    else if (adc_temp_deg > 60)
    {
      //lightmode_dim(0x10);
    }
    else
    {
      //lightmode_dim((16 + ((60-adc_temp_deg) * )) & 0xF0);
    }*/

    if (hw_ctrl_get_hall_state())
    {
      led_show_status(adc_temp_deg, adc_volt_meas);
    }
    else
    {
      led_show(led_state);
    }
  }
  
  if(currentMillis % 1000==0){
    // Measure temperature and battery voltage
    adc_loop();
    // if the voltage measured is smaller than the turn off threshold, it is turned off. 
    if(config_store.user_settings.turn_off_voltage_mv > adc_volt_meas)
        hw_ctrl_turn_off();
  }
  
  if (config_store.user_settings.status_refresh_period_ms != 0 && (currentMillis % config_store.user_settings.status_refresh_period_ms == 0))
  { // Transmit the status frame
    wifi_status_transmit();
  }
}

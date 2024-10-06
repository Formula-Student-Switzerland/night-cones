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


#define SDA_PIN    2
#define SCL_PIN   14

#define WIFI_DELAY_MS 100
#define WIFI_LOOPS    50

unsigned long previousMillis = 0;  // will store last time LED was updated
const long LED_UPDATE_INTERVAL = 25;  // interval at which to blink (milliseconds)

void setup() {
  // Init pins.
  Serial.begin(115200);
  delay(2000);
  config_store_setup();
  hw_Ctrl_setup();
  adc_setup();
  adc_loop();

  sync_setup(LED_UPDATE_INTERVAL);

  // LED setup
  led_setup();
  lightmode_setup();
 
  // Init LEDs with red
  lightmode_switch(COLOR_BLUE, 0x20, 0);
  lightmode_step(0, led_state);
  led_show(led_state);

  delay(500);
  wifi_setup();
  // In case the Default mode would turn off everything, we first need to 
  // wake the failsafe by switching shortly to blue and then go to black. 
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

  cli_work();

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

    if (digitalRead(HALL_PIN))
    {
      led_show_status(adc_temp_deg, adc_volt_meas);
    }
    else
    {
      led_show(led_state);
    }
  }
  if (currentMillis % 5000 == 0)
  {
    // Measure temperature and battery voltage
    adc_loop();
    wifi_status_transmit();
  }
}

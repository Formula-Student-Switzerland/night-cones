//#include <WiFi.h>
#include <ESP8266WiFi.h>
//#include <ESPmDNS.h>
#include <ESP8266mDNS.h>
//#include <NetworkUdp.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

#include <Adafruit_NeoPixel.h>

/*#include "lightmodes.h"
#include "wifi.h"*/
#include "adc.h"
/*#include "led.h"
#include "sync.h"*/
#include "color.h"
#include "hw_ctrl.h"
#include "config_store.h"

//#include "..\..\..\Adafruit_NeoPixel\Adafruit_NeoPixel.h"
//#include "D:\git\FSCH\Adafruit_NeoPixel\Adafruit_NeoPixel.h"
#define BRIGHTNESS_DEFAULT 0x70


#define SDA_PIN    2
#define SCL_PIN   14

#define WIFI_DELAY_MS 100
#define WIFI_LOOPS    50

bool wifi_configure = true;
bool wifi_connected = false;

unsigned long previousMillis = 0;  // will store last time LED was updated
const long LED_UPDATE_INTERVAL = 100;  // interval at which to blink (milliseconds)

void setup() {
  // Init pins.
    config_store_setup();
    hw_Ctrl_setup();
    adc_setup();

  // LED setup
  led_setup();
  lightmode_setup();

  // Init LEDs with red
  lightmode_switch(COLOR_RED, 0xF0, 0);
  led_show();
  
  bool wifi_loop_continue = false;
  bool hall_status;
  unsigned int wifi_loop_cnt = 0;
  delay(500);
  while (wifi_loop_cnt < WIFI_LOOPS & wifi_configure) {
    delay(WIFI_DELAY_MS);
    hall_status = hw_ctrl_get_hall_state();
    if(hall_status == false) {
      wifi_configure = false;
    }
    if ((wifi_loop_cnt % 10) >= 5) {
      for (int n = 0; n<LED_COUNT; n++) {
        lightmode_switch(COLOR_GREEN, BRIGHTNESS_DEFAULT, 0);
      }
    } else {
      for (int n = 0; n<LED_COUNT; n++) {
        lightmode_switch(COLOR_BLUE, BRIGHTNESS_DEFAULT, 0);
      }
    }
    led_show();
    wifi_loop_cnt++;
  }
  if (wifi_configure) {
    wifi_connected = !(bool) wifi_setup();
  }
  led_esp_blink(LED_ESP_FREQ_READY, 4);
  
}

void loop() {

  int adc_volt_meas;
  int adc_temp_meas;

  // OTA loop
  wifi_loop();

  uint32_t currentMillis;
  if (sync_loop(&currentMillis)) {
    
    // Measure temperature and battery voltage
    adc_loop();
    lightmode_step(currentMillis, led_state);
    
    if (adc_temp_meas > 374) 
        //lightmode_dim(BRIGHTNESS_DEFAULT);
     else if (adc_temp_meas < 337) {
        lightmode_dim(0x10);
    } else {
      lightmode_dim((16 + ((adc_temp_meas - 337) * 3))&0xF0);
    }

    if (digitalRead(HALL_PIN))
        led_show_status(adc_temp_meas, adc_volt_meas);
    else{
        led_show(led_state);
    }
  }
}



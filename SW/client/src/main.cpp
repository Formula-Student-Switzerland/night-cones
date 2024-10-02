#include "Arduino.h"
#include "lightmodes.h"
#include "wifi.h"
#include "adc.h"
#include "led.h"
#include "sync.h"
#include "color.h"
#include "hw_ctrl.h"
#include "config_store.h"

#define BRIGHTNESS_DEFAULT 0x70


#define SDA_PIN    2
#define SCL_PIN   14

#define WIFI_DELAY_MS 100
#define WIFI_LOOPS    50

bool wifi_connected = false;

unsigned long previousMillis = 0;  // will store last time LED was updated
const long LED_UPDATE_INTERVAL = 25;  // interval at which to blink (milliseconds)

void setup() {
  // Init pins.
  Serial.begin(115200);
  config_store_setup();
  hw_Ctrl_setup();
  adc_setup();
  sync_setup(LED_UPDATE_INTERVAL);

  // LED setup
  led_setup();
  lightmode_setup();
 
  // Init LEDs with red
  lightmode_switch(COLOR_BLUE, 0x70, 0);
  lightmode_step(0, led_state);
  led_show(led_state);

  delay(500);
  wifi_connected = !(bool) wifi_setup();
  if(wifi_connected){    
    lightmode_switch(COLOR_BLUE, 0x70, 0);
  } else {
    lightmode_switch(COLOR_RED, 0x70, 0);
  }

}

void loop() {

  // OTA loop
  wifi_loop();
  
  uint32_t currentMillis;
  if (sync_loop(&currentMillis)) {

    // Measure temperature and battery voltage
    adc_loop();
    lightmode_step(currentMillis, led_state);
    
    if (adc_temp_meas > 374) {
        //lightmode_dim(BRIGHTNESS_DEFAULT);
     } else if (adc_temp_meas < 337) {
        lightmode_dim(0x10);
    } else {
      lightmode_dim((16 + ((adc_temp_meas - 337) * 3))&0xF0);
    }

    if (digitalRead(HALL_PIN)){
        printf("Hall Active");
        led_show_status(adc_temp_meas, adc_volt_meas);
    }
    else{
        led_show(led_state);
    }
  }
  if(currentMillis%20000 == 0){
      wifi_status_transmit();
  }
}



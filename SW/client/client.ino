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


//#include "..\..\..\Adafruit_NeoPixel\Adafruit_NeoPixel.h"
//#include "D:\git\FSCH\Adafruit_NeoPixel\Adafruit_NeoPixel.h"


#define KILL_PIN  12
#define HALL_PIN  16
#define SDA_PIN    2
#define SCL_PIN   14


#define RED_DEFAULT 127
#define GREEN_DEFAULT 127
#define BLUE_DEFAULT 127

#define WIFI_DELAY_MS 100
#define WIFI_LOOPS    50


const int DELAY = 3000;

bool wifi_configure = true;
bool wifi_connected = false;

unsigned long previousMillis = 0;  // will store last time LED was updated
const long LED_UPDATE_INTERVAL = 100;  // interval at which to blink (milliseconds)

void setup() {
  // Init pins.

  pinMode(KILL_PIN, OUTPUT);
  pinMode(HALL_PIN, INPUT);

  //adc_setup();

  // LED setup
  //led_setup();
  //lightmode_setup();

  // Init LEDs with red
  /*for (int n = 0; n<LED_COUNT; n++) {
    strip.setPixelColor(n, 50, 0, 0);
  };
  strip.show();*/
  
  bool wifi_loop_continue = false;
  bool hall_status;
  unsigned int wifi_loop_cnt = 0;
  delay(500);
  while (wifi_loop_cnt < WIFI_LOOPS & wifi_configure) {
    delay(WIFI_DELAY_MS);
    hall_status = digitalRead(HALL_PIN);
    if(hall_status == false) {
      wifi_configure = false;
    }
    if ((wifi_loop_cnt % 10) >= 5) {
      /*for (int n = 0; n<LED_COUNT; n++) {
        strip.setPixelColor(n, 0, 50, 0);
      }*/
    } else {
      /*for (int n = 0; n<LED_COUNT; n++) {
        strip.setPixelColor(n, 0, 0, 50);
      }*/
    }
    //strip.show();
    wifi_loop_cnt++;
  }
  if (wifi_configure) {
    //wifi_connected = !(bool) wifi_setup();
  }
  //led_esp_blink(LED_ESP_FREQ_READY, 4);
  
}

void loop() {

  int adc_volt_meas;
  int adc_temp_meas;
  int brightness_red;
  int brightness_green;
  int brightness_blue;

  // OTA loop
  //wifi_loop();

  uint32_t currentMillis;
  /*if (sync_loop(&currentMillis)) {
    
    // Measure temperature and battery voltage
    adc_loop();
    lightmode_step(currentMillis, led_state);
    
    // Exchange this piece of code
    //if (adc_temp_meas > 374) {
    //  lightMode1(0, RED_DEFAULT, led_state);
    //} else if (adc_temp_meas < 337) {
    //  lightMode1(0, 10, led_state);
    //} else {
    //  lightMode1(0, 10 + ((adc_temp_meas - 337) * 3), led_state);
    //}

    if (digitalRead(HALL_PIN))
        led_show_status(adc_temp_meas, adc_volt_meas);
    else{
        led_show(led_state);
    }
  }*/
}



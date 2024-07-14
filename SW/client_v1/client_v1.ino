//#include <WiFi.h>
#include <ESP8266WiFi.h>
//#include <ESPmDNS.h>
#include <ESP8266mDNS.h>
//#include <NetworkUdp.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

#include <Adafruit_NeoPixel.h>

//#include "..\..\..\Adafruit_NeoPixel\Adafruit_NeoPixel.h"
//#include "D:\git\FSCH\Adafruit_NeoPixel\Adafruit_NeoPixel.h"

#define LED_PIN    4
#define KILL_PIN  12
#define ADC_MUX_PIN 13
#define HALL_PIN  16
#define SDA_PIN    2
#define SCL_PIN   14
#define LED_ESP_PIN 2
#define ADC_IN   A0


#define LED_COUNT 20
#define LED_BOTTOM_COUNT 16

#define ADC_MUX_VOLT 0
#define ADC_MUX_TEMP 1

#define RED_DEFAULT 127
#define GREEN_DEFAULT 127
#define BLUE_DEFAULT 127

#define FREQ_ON 250
#define FREQ_READY 500
#define FREQ_LIGHT 1000
#define FREQ_LOOP 3000

#define WIFI_ATTEMPTS 3
#define WIFI_DELAY_MS 100
#define WIFI_LOOPS    50

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

const int PIN = 2;

const int DELAY = 3000;

const char *ssid = "FSCH_NightCone";
const char *password = "I_R4C3@night";
const char *ota_pwd = "NC_update";

bool wifi_configure = true;
bool wifi_connected = false;

unsigned long previousMillis = 0;  // will store last time LED was updated
const long loop_interval = 10;  // interval at which to blink (milliseconds)

void setup() {
  // Init pins.
  pinMode(LED_ESP_PIN, OUTPUT);
  pinMode(ADC_MUX_PIN, OUTPUT);
  pinMode(KILL_PIN, OUTPUT);
  pinMode(HALL_PIN, INPUT);

  // LED setup
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'

  // Init LEDs with red
  for (int n = 0; n<LED_COUNT; n++) {
    strip.setPixelColor(n, 50, 0, 0);
  };
  strip.show();
  
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
      for (int n = 0; n<LED_COUNT; n++) {
        strip.setPixelColor(n, 0, 50, 0);
      }
    } else {
      for (int n = 0; n<LED_COUNT; n++) {
        strip.setPixelColor(n, 0, 0, 50);
      }
    }
    strip.show();
    wifi_loop_cnt++;
  }
  if (wifi_configure) {
    // Wifi Setup
    Serial.begin(115200);
    Serial.println("Booting");
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    int wifi_attempt = 0;

    esp_led_blink(FREQ_ON, 4);

    delay(1000);

    while (WiFi.waitForConnectResult() != WL_CONNECTED && wifi_attempt < WIFI_ATTEMPTS) {
      Serial.println("Connection Failed! Rebooting...");
      delay(5000);
      ESP.restart();
      wifi_attempt++;
    }


    // Check Wifi and init OTA.
    if (WiFi.waitForConnectResult() == WL_CONNECTED) {
      Serial.println("WiFi connected");
      wifi_connected = true;

      // Port defaults to 3232
      // ArduinoOTA.setPort(3232);

      // Hostname defaults to esp3232-[MAC]
      // ArduinoOTA.setHostname("myesp32");

      // OTA setup
      // Set password.
      ArduinoOTA.setPassword(ota_pwd);

      // Password can be set with it's md5 value as well
      // MD5(admin) = 21232f297a57a5a743894a0e4a801fc3
      // ArduinoOTA.setPasswordHash("21232f297a57a5a743894a0e4a801fc3");

      ArduinoOTA.onStart([]() {
          String type;
          if (ArduinoOTA.getCommand() == U_FLASH) {
            type = "sketch";
          } else {  // U_SPIFFS
            type = "filesystem";
          }

          // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
          Serial.println("Start updating " + type);
        });

        ArduinoOTA.onEnd([]() {
          Serial.println("\nEnd");
        });

        ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
          Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
        });

        ArduinoOTA.onError([](ota_error_t error) {
          Serial.printf("Error[%u]: ", error);
          if (error == OTA_AUTH_ERROR) {
            Serial.println("Auth Failed");
          } else if (error == OTA_BEGIN_ERROR) {
            Serial.println("Begin Failed");
          } else if (error == OTA_CONNECT_ERROR) {
            Serial.println("Connect Failed");
          } else if (error == OTA_RECEIVE_ERROR) {
            Serial.println("Receive Failed");
          } else if (error == OTA_END_ERROR) {
            Serial.println("End Failed");
          }
        });

      ArduinoOTA.begin();

      Serial.println("Ready");
      Serial.print("IP address: ");
      Serial.println(WiFi.localIP());

    } else {
      wifi_connected = false;
    }
  }
  esp_led_blink(FREQ_READY, 4);
  
}

void loop() {

  int volt_meas;
  int temp_meas;
  int brightness_red;
  int brightness_green;
  int brightness_blue;

  // OTA loop
  ArduinoOTA.handle();

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= loop_interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;

    // Measure temperature and battery voltage
    digitalWrite(ADC_MUX_PIN, ADC_MUX_TEMP);
    delay(1);
    temp_meas = analogRead(ADC_IN);
    digitalWrite(ADC_MUX_PIN, ADC_MUX_VOLT);
    delay(1);
    volt_meas = analogRead(ADC_IN);

    if (temp_meas > 374) {
      brightness_red   = RED_DEFAULT;
      brightness_green = GREEN_DEFAULT;
      brightness_blue  = BLUE_DEFAULT;
    } else if (temp_meas < 337) {
      brightness_red   = 10;
      brightness_green = 10;
      brightness_blue  = 10;
    } else {
      brightness_red   = 10 + ((temp_meas - 337) * 3);
      brightness_green = brightness_red;
      brightness_blue  = brightness_red;
      // ToDo Daniel Check here, if you missed the other brightnesses
    }

    // Setup light mode 1, white, 100 brightness.
    for (int n = 0; n<LED_COUNT; n++) {
      strip.setPixelColor(n, brightness_red, brightness_green, brightness_blue);
      //if (digitalRead(HALL_PIN)) {
      //  strip.setPixelColor(n, n*16, n*16, n*16);
      //}
    };

    //if (wifi_connected == true && wifi_configure == true) {
    //  strip.setPixelColor(16, 40, 0, 0);
    //  strip.setPixelColor(17, 40, 0, 0);
    //}
    //else {
      //for (int n = 16; n<18; n++) {
      //  strip.setPixelColor(n, brightness_red, brightness_green, brightness_blue);
      //};
    //};
    int led_temp_red;
    int led_temp_green;
    int led_temp_blue;
    if (digitalRead(HALL_PIN)) {
      if (temp_meas > 550) {
        //strip.setPixelColor(18, 0, 0, 100);
        led_temp_red   = 0;
        led_temp_green = 0;
        led_temp_blue  = 100;
      }
      else if (temp_meas < 350) {
        //strip.setPixelColor(18, 100, 0, 0);
        led_temp_red   = 100;
        led_temp_green = 0;
        led_temp_blue  = 0;
      }
      else {
        //strip.setPixelColor(18, 100-(temp_meas-350)/2, 0, ((temp_meas-350)/2));
        led_temp_red   = 100-(temp_meas-350)/2;
        led_temp_green = 0;
        led_temp_blue  = (temp_meas-350)/2;
      }

      for (int n = 16;n<20; n++) {
        strip.setPixelColor(n, led_temp_red, led_temp_green, led_temp_blue);
      }
      //strip.setPixelColor(19, 255-volt_meas/4, volt_meas/4, 0);

      int n_led_indicator;
      if (volt_meas > 775) {
        n_led_indicator = 15;
      } else if (volt_meas < 553) {
        n_led_indicator = 0;
      } else {
        n_led_indicator = (volt_meas - 553) / 14;
      }
      for (int n = 0; n<16; n++) {
        if (n > n_led_indicator) {
          strip.setPixelColor(n, 0, 0, 0);
        } else {
          strip.setPixelColor(n, brightness_red, brightness_green, brightness_blue);
        }
      }
    }

    strip.show();

    //delay(10);
  }
}


void esp_led_blink(int frequency, int blinks) {
  for (int b=0; b < blinks; b++) {
    digitalWrite(LED_ESP_PIN, 1);
    delay(frequency);
    digitalWrite(LED_ESP_PIN, 0);
    delay(frequency);
  }

}
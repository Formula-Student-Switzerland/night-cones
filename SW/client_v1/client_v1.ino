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

#define LED_COUNT 20
#define LED_BOTTOM_COUNT 16

#define ADC_MUX_VOLT 0
#define ADC_MUX_TEMP 1

#define RED_DEFAULT 100
#define GREEN_DEFAULT 100
#define BLUE_DEFAULT 100

#define FREQ_ON 250
#define FREQ_READY 500
#define FREQ_LIGHT 1000
#define FREQ_LOOP 3000

#define WIFI_ATTEMPTS 3


Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

const int PIN = 2;

const int DELAY = 3000;

const char *ssid = "NIGHT_CONES";
const char *password = "I_R4C3@night";
const char *ota_pwd = "NC_update";

bool wifi_connected = false;

void setup() {
  // Init pins.
  pinMode(LED_ESP_PIN, OUTPUT);
  pinMode(ADC_MUX_PIN, OUTPUT);
  pinMode(KILL_PIN, OUTPUT);
  pinMode(HALL_PIN, INPUT);

  // LED setup
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'

  
  // Wifi Setup
  Serial.begin(115200);
  Serial.println("Booting");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  int wifi_attempt = 0;

  esp_led_blink(FREQ_ON, 4);

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

  esp_led_blink(FREQ_READY, 4);
  
}

void loop() {

  
  // OTA loop
  if (wifi_connected == true) {
    ArduinoOTA.handle();
  }
  
  
  
  // Setup light mode 1, white, 100 brightness.
  for (int n = 0; n<LED_BOTTOM_COUNT; n++) {
  strip.setPixelColor(n, RED_DEFAULT, GREEN_DEFAULT, BLUE_DEFAULT);
  //strip.setPixelColor(n, n*10, n*10, n*10);
  //strip.setPixelColor(n, n*10, 0, 0);
  };

  strip.show();

  delay(10);
  

}


void esp_led_blink(int frequency, int blinks) {
  for (int b=0; b < blinks; b++) {
    digitalWrite(LED_ESP_PIN, 1);
    delay(frequency);
    digitalWrite(LED_ESP_PIN, 0);
    delay(frequency);
  }

}
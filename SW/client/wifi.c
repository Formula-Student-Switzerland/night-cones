/****************************)***************************************************/
/* 
 * File: wifi.c
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file is used to handle all WIFI communication. This includes OTA, 
 * Handling of any communication to server. 
 */
/*******************************************************************************/
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

#include "led.h"
#include "wifi.h"
#include "credentials.h"

/**
 * Sets up the WIFI Module and connects to the specified WLAN
 *
 */
void wifi_setup(void) {
    // Wifi Setup
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    int wifi_attempt = 0;
    // Signal start of connection
    led_esp_blink(LED_ESP_FREQ_ON, 4);
    
    delay(1000);

    // Check what this code excatly does and if it works as intended
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
      ota_setup();
      return 0;
    }
    // Failed somewhere
    return 1;
}

/*
* Receive frame, unpack and call function to handle it. Could be: 
* - Set light mode
* - Respond to config request
* - Set config values
* - send status frame
*/
void wifi_rx_frame()
{
    
    
}

/**
 * Transmits a Status message
 *
 */
void wifi_tx_status()
{
    
    
}


/**
 * Worker function which needs to be called periodically. 
 *
 */
void wifi_loop() {
   ota_loop();
}


//esp_wifi_get_mac(WIFI_IF_STA, baseMac);
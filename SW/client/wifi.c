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

struct {
    uint8_t version;
    uint8_t type;
    uint8_t frame_number;
    uint8_t reserved;
    uint32_t reserved1;
    uint64_t timestamp;   
} wifi_frame_header;


union {
    uint8_t frame[30];
    struct{
        struct wifi_frame_header header;
        uint16_t cone_id;
        uint8_t SoC;
        uint8_t rssi;
        uint8_t mac[6];
        uint8_t sw_rev_maj;
        uint8_t sw_rev_min;
        uint8_t hw_rev;
        uint8_t hall_state;        
    } data;
} wifi_cts_status_frame_def;
    
struct wifi_frame_header wifi_frame_header;

struct wifi_cts_status_frame_def wifi_tx_status_frame;



IPAddress wifi_server_ip;

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
    
    Udp.begin(WIFI_UDP_RX_PORT);
    
    
    wifi_frame_header.version = WIFI_COM_VERSION;
    wifi_frame_header.type = WIFI_CTS_STATUS_TYPE;
    wifi_frame_header.frame_number = 0;
    wifi_frame_header.reserved=0;
    wifi_frame_header.reserved1=0;
    wifi_frame_header.timestamp=0;
    
    
    
    wifi_cts_status_frame.data.header = header;
   esp_wifi_get_mac(WIFI_IF_STA, &wifi_cts_status_frame.data.mac[6]); 
   wifi_cts_status_frame.data.sw_rev_maj=CONFIG_STORE_SW_REV_MAJ;
   wifi_cts_status_frame.data.sw_rev_min=CONFIG_STORE_SW_REV_MIN;
   wifi_cts_status_frame.data.hw_rev = config_store[config_store_ids.HARDWARE_REVISION];
    
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
   
    server_ip = Udp.remoteIP();
    
}

/**
 * Transmits a Status message
 *
 */
void wifi_tx_status(){
    
   wifi_cts_status_frame.data.cone_id = config_store[config_store_ids.CONE_ID];
   wifi_cts_status_frame.data.SoC = adc_soc;
   wifi_cts_status_frame.data.rssi = WIFI.RSSI();
   //wifi_cts_status_frame.data.hall_state = ;     
    
    Udp.beginPacket(wifi_server_ip, WIFI_UDP_TX_PORT);
    Udp.write(wifi_cts_status_frame,30);
    Udp.endPacket();
}


/**
 * Worker function which needs to be called periodically. 
 *
 */
void wifi_loop() {
   ota_loop();
}


//esp_wifi_get_mac(WIFI_IF_STA, baseMac);
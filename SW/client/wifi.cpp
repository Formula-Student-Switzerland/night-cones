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
#include <stdint.h>

#include "led.h"
#include "wifi.h"
#include "credentials.h"
#include "ota.h"
#include "config_store.h"
#include "adc.h"

typedef struct {
    uint8_t version;
    uint8_t type;
    uint8_t frame_number;
    uint8_t reserved;
    uint32_t reserved1;
    uint64_t timestamp;   
} wifi_frame_header_struct;


union {
    uint8_t frame[30];
    struct{
        wifi_frame_header_struct header;
        uint16_t cone_id;
        uint8_t SoC;
        uint8_t rssi;
        uint8_t mac[6];
        uint8_t sw_rev_maj;
        uint8_t sw_rev_min;
        uint8_t hw_rev;
        uint8_t hall_state;        
    } data;
} wifi_cts_status_frame;
    
wifi_frame_header_struct wifi_frame_header;

IPAddress wifi_server_ip;
WiFiUDP Udp;

/**
 * Sets up the WIFI Module and connects to the specified WLAN
 *
 */
int wifi_setup(void) {
    // Wifi Setup
    WiFi.mode(WIFI_STA);
    WiFi.begin(CRED_WIFI_SSID, CRED_WIFI_PW);
    
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
    
    
    
    wifi_cts_status_frame.data.header = wifi_frame_header;
    WiFi.macAddress(wifi_cts_status_frame.data.mac); 
    wifi_cts_status_frame.data.sw_rev_maj=CONFIG_STORE_SW_REV_MAJ;
    wifi_cts_status_frame.data.sw_rev_min=CONFIG_STORE_SW_REV_MIN;
    wifi_cts_status_frame.data.hw_rev = config_store_get(HARDWARE_REVISION);
    
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
   
    wifi_server_ip = Udp.remoteIP();
    
}

/**
 * Transmits a Status message
 *
 */
void wifi_tx_status(){
    
   wifi_cts_status_frame.data.cone_id = config_store_get(CONE_ID);
   wifi_cts_status_frame.data.SoC = adc_soc;
   wifi_cts_status_frame.data.rssi = WiFi.RSSI();
   //wifi_cts_status_frame.data.hall_state = ;     
    
    Udp.beginPacket(wifi_server_ip, WIFI_UDP_TX_PORT);
    Udp.write(wifi_cts_status_frame.frame,30);
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
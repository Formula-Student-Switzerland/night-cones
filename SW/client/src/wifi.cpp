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
#include <stdio.h>

#include "led.h"
#include "lightmodes.h"
#include "wifi.h"
#include "credentials.h"
#include "ota.h"
#include "config_store.h"
#include "adc.h"
#include "sync.h"

typedef struct {
    uint8_t version;
    uint8_t type;
    uint8_t frame_number;
    uint8_t reserved;
    uint32_t reserved1;
    uint64_t timestamp;   
} wifi_frame_header_t;

typedef struct {
    uint8_t color;
    uint8_t brightness_mode;
    uint8_t repetition_time;
    uint8_t phase_shift;
} wifi_frame_rx_data_field_t;


union {
    uint8_t frame[30];
    struct{
        wifi_frame_header_t header;
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
    
wifi_frame_header_t wifi_frame_header;

IPAddress wifi_server_ip;
WiFiUDP Udp;

uint8_t wifi_rx_buffer[WIFI_RX_BUFFER_SIZE];
wifi_frame_header_t * const wifi_rx_header = (wifi_frame_header_t *)wifi_rx_buffer;
wifi_frame_rx_data_field_t * const wifi_rx_stc_data = (wifi_frame_rx_data_field_t *)&wifi_rx_buffer[16];

void wifi_rx_handle_data(wifi_frame_rx_data_field_t * wifi_rx_stc_data, uint16_t max_cone_id);
void wifi_rx_handle_config(uint8_t* rx_frame, uint16_t length);
void wifi_tx_settings(void);
void wifi_tx_status(void);


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
      led_esp_blink(LED_ESP_FREQ_ON/5, 4);
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
    wifi_cts_status_frame.data.hw_rev = config_store.hardware_data.hardware_revision;
    
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
    int packetSize = Udp.parsePacket();
    if (packetSize)
    {
        // receive incoming UDP packets
        printf("Received %d bytes from %s, port %d\n", packetSize, Udp.remoteIP().toString().c_str(), Udp.remotePort());
        int len = Udp.read(wifi_rx_buffer, 255);
        if(len == 0) {
            printf("Received Empty Frame");
            return;
        }
        wifi_server_ip = Udp.remoteIP(); 
        
    
        if(wifi_rx_header->version != WIFI_COM_VERSION){
            // Error, Frame has the wrong Version
            printf("Wrong WIFI_COM_Version Got: %x, Local: %x", wifi_rx_buffer[0],WIFI_COM_VERSION);
            return;
        }

        switch(wifi_rx_header->type) {
            case WIFI_STC_DATA_TYPE:
                wifi_rx_handle_data(wifi_rx_stc_data, (len-16)/4);
                break;            
            case WIFI_STC_CONFIG_TYPE:
                wifi_rx_handle_config(&wifi_rx_buffer[16], len-16);
                
            case WIFI_STC_SET_REQ_TYPE:
                wifi_tx_settings();
                break;
            case WIFI_STC_STAT_REQ_TYPE:
                wifi_tx_status();
                break;    
        }
        sync_synchronize(wifi_rx_header->timestamp);
    }
}

void wifi_rx_handle_data(wifi_frame_rx_data_field_t * wifi_rx_stc_data, uint16_t max_cone_id) {
    if(max_cone_id<=config_store.user_settings.cone_id)
        return;
    
    lightmode_switch(wifi_rx_stc_data[config_store.user_settings.cone_id].color,  
        wifi_rx_stc_data[config_store.user_settings.cone_id].brightness_mode, 
        wifi_rx_stc_data[config_store.user_settings.cone_id].repetition_time);
    sync_reconfigure(wifi_rx_stc_data[config_store.user_settings.cone_id].repetition_time,  
        wifi_rx_stc_data[config_store.user_settings.cone_id].phase_shift); 
}

void wifi_rx_handle_config(uint8_t* rx_frame, uint16_t length) {
    // Same as below think about this...
    
}


void wifi_tx_settings(void) {
    // think about how to handle these things. Current method of config storage is optimized for EEPROM
    // Making everything 32 bit would be optimized for this. Probably do translation in Config Storage
    
}


/**
 * Transmits a Status message
 *
 */
void wifi_tx_status(void){
    
   wifi_cts_status_frame.data.cone_id = config_store.user_settings.cone_id;
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
void wifi_loop(void) {
    //wifi_rx_frame();
    ota_loop();
}


//esp_wifi_get_mac(WIFI_IF_STA, baseMac);
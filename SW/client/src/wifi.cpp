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
#include "HardwareSerial.h"

#include "adc.h"
#include "config_store.h"
#include "credentials.h"
#include "hw_ctrl.h"
#include "led.h"
#include "lightmodes.h"
#include "sync.h"
#include "ota.h"
#include "wifi.h"

/*
 * Frame definitions
 */
typedef struct {
    uint8_t version;
    uint8_t type;
    uint8_t frame_number;
    uint8_t reserved;
    uint32_t timestamp;   
} wifi_frame_header_t;

// Station to cone data frame
typedef struct {
    uint8_t color;
    uint8_t brightness_mode;
    uint8_t repetition_time;
    uint8_t phase_shift;
} wifi_stc_data_frame_field_t;

// cone to station status frame
typedef union {
    uint8_t frame[sizeof(wifi_frame_header_t)+8];
    struct{
        wifi_frame_header_t header;
        uint16_t cone_id;
        uint8_t SoC;
        uint8_t rssi;
        int8_t temp;
        uint8_t hall_state;  
        uint16_t reserved;      
    } data;
} wifi_cts_status_frame_t;

enum wifi_config_store_ids
{
    WIFI_CONFIG_ID_HW_REV = 0,
    WIFI_CONFIG_ID_SW_REV,
    WIFI_CONFIG_ID_SERIAL_NO,
    WIFI_CONFIG_ID_CONE_ID,
    WIFI_CONFIG_ID_FALLBACK_LM,
    WIFI_CONFIG_ID_TURN_OFF,
    WIFI_CONFIG_ID_ADC_VOLTAGE,
    WIFI_CONFIG_ID_ADC_TEMP,
    WIFI_CONFIG_ID_STATUS_FREQUENCY,
    WIFI_CONFIG_ID_DEBUG1,
    WIFI_CONFIG_ID_DEBUG2,
    WIFI_CONFIG_ID_DEBUG3,
    WIFI_CONFIG_ID_DEBUG4,
    WIFI_CONFIG_ID_SAVE_EEPROM,
    WIFI_CONFIG_ID_END
};

typedef union {
    uint8_t frame[sizeof(wifi_frame_header_t)+8*WIFI_CONFIG_ID_END];
    struct{
        wifi_frame_header_t header;
        uint32_t values[2*WIFI_CONFIG_ID_END];
    } data;
} wifi_xtx_config_frame_t;

/*
 * Frame Variable definitions
 */

uint8_t wifi_rx_buffer[WIFI_RX_BUFFER_SIZE];
uint8_t wifi_tx_buffer[WIFI_TX_BUFFER_SIZE];

wifi_frame_header_t * const wifi_rx_header = (wifi_frame_header_t *)wifi_rx_buffer;
wifi_stc_data_frame_field_t * const wifi_rx_stc_data = (wifi_stc_data_frame_field_t *)&wifi_rx_buffer[sizeof(wifi_frame_header_t)];

wifi_cts_status_frame_t * const wifi_cts_status_frame = (wifi_cts_status_frame_t *)wifi_tx_buffer;
wifi_xtx_config_frame_t * const wifi_cts_config_frame = (wifi_xtx_config_frame_t *)wifi_tx_buffer;

/*
 * Variables
 */
IPAddress wifi_server_ip;
WiFiUDP Udp;

uint32_t wifi_frame_errors;
uint32_t wifi_frame_order_error;
uint32_t wifi_current_frame_id;


/*
 * Methods
 */
void wifi_rx_handle_data(wifi_stc_data_frame_field_t * wifi_rx_stc_data, uint16_t max_cone_id);
uint32_t wifi_rx_handle_config(wifi_xtx_config_frame_t *rx_frame, uint16_t length);
void wifi_tx_settings(IPAddress server_ip);
void wifi_tx_status(IPAddress server_ip);


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
    led_esp_blink(LED_ESP_FREQ_ON, 2);
    
    //delay(1000);

    // Check what this code excatly does and if it works as intended
    while (WiFi.waitForConnectResult() != WL_CONNECTED && wifi_attempt < WIFI_ATTEMPTS) {
      Serial.printf("Connection Failed! Rebooting...\r\n");
      Serial.flush();
      delay(5000);
      ESP.restart();
      wifi_attempt++;
    }

    // Check Wifi and init OTA.
    if (WiFi.isConnected() != true) {
      return 1;
    }
    
    Serial.printf("WiFi connected\r\n");
    ota_setup();
    //led_esp_blink(LED_ESP_FREQ_CONNECTED, 8);
    
    Udp.begin(WIFI_UDP_RX_PORT);
    
    // Initialise default TX Frame
    wifi_cts_status_frame->data.header.version = WIFI_COM_VERSION;
    wifi_cts_status_frame->data.header.frame_number = 0;
    wifi_cts_status_frame->data.header.reserved=0;
    wifi_cts_status_frame->data.header.timestamp=0;    

    return 0;
}

/*
* Receive frame, unpack and call function to handle it. Could be: 
* - Set light mode
* - Respond to config request
* - Set config values
* - send status frame
*/
void wifi_rx_frame(void)
{
    IPAddress server_ip;
    int packetSize = Udp.parsePacket();

    if (packetSize)
    {
        // receive incoming UDP packets
#ifdef DEBUG
        Serial.printf("Received %d bytes from %s, port %d\r\n", packetSize, Udp.remoteIP().toString().c_str(), Udp.remotePort());
#endif
        int len = Udp.read(wifi_rx_buffer, 255);
        if(len == 0) {
#ifdef DEBUG
            printf("Received Empty Frame\r\n");
#endif
            return;
        }
        server_ip = Udp.remoteIP();
    
        if(wifi_rx_header->version != WIFI_COM_VERSION){
            // Error, Frame has the wrong Version
#ifdef DEBUG      
            printf("Wrong WIFI_COM_Version Got: %x, Local: %x\r\n", wifi_rx_buffer[0],WIFI_COM_VERSION);
#endif            
            return;
        }

        switch(wifi_rx_header->type) {
            case WIFI_STC_DATA_TYPE:
#ifdef DEBUG
                printf("Handle WIFI_STC_DATA_TYPE\r\n");
#endif
                //ToDo Implement lost package detection here!
                wifi_rx_handle_data(wifi_rx_stc_data, (len-sizeof(wifi_frame_header_t))/4);
                wifi_server_ip = server_ip;
                break;            
            case WIFI_STC_CONFIG_TYPE:
#ifdef DEBUG
                printf("Handle WIFI_STC_CONFIG_TYPE\r\n");
#endif
                wifi_rx_handle_config((wifi_xtx_config_frame_t*)wifi_rx_buffer, (len-sizeof(wifi_frame_header_t))/4);
                
            case WIFI_STC_SET_REQ_TYPE:
#ifdef DEBUG
                printf("Handle WIFI_STC_SET_REQ_TYPE\r\n");
#endif
                wifi_tx_settings(server_ip);
                break;
            case WIFI_STC_STAT_REQ_TYPE:
#ifdef DEBUG
                printf("Handle WIFI_STC_STAT_REQ_TYPE\r\n");
#endif
                wifi_tx_status(server_ip);
                break;    
        }
        sync_synchronize(wifi_rx_header->timestamp);
    }
}

/**
 * Extract lightmode from data frame according to current cone ID.
 *
 * @param wifi_rx_stc_data Pointer to received frames first data field
 * @param max_cone_id maximum number of data fields the frame contains
 */
void wifi_rx_handle_data(wifi_stc_data_frame_field_t * wifi_rx_stc_data, uint16_t max_cone_id) {
    // Check if data for current cone is delivered.
    if(max_cone_id<=config_store.user_settings.cone_id)
        return;
    
    lightmode_switch(wifi_rx_stc_data[config_store.user_settings.cone_id].color,  
        wifi_rx_stc_data[config_store.user_settings.cone_id].brightness_mode, 
        wifi_rx_stc_data[config_store.user_settings.cone_id].repetition_time);
        
    sync_reconfigure(wifi_rx_stc_data[config_store.user_settings.cone_id].repetition_time,  
        wifi_rx_stc_data[config_store.user_settings.cone_id].phase_shift); 
}

/**
 * Handle the server to cone config message. Decodes all available values and sets them. 
 *
 * @param rx_frame pointer to config_frame struct
 * @param length length of the uint32_t array (number of id+keys
 */
uint32_t wifi_rx_handle_config(wifi_xtx_config_frame_t* rx_frame, uint16_t length) {
    uint32_t id = 0;
    uint32_t value = 0;

    for(int i=0; i<length;i+=2){
        id = rx_frame->data.values[i];
        value = rx_frame->data.values[i + 1];
        if(id >= WIFI_CONFIG_ID_END)
            return 1;
    
        switch(id)
        {
            case WIFI_CONFIG_ID_HW_REV:
                return 1;
            case WIFI_CONFIG_ID_SERIAL_NO:
                return 1;
            case WIFI_CONFIG_ID_CONE_ID:
                config_store.user_settings.cone_id = value;
                break;
            case WIFI_CONFIG_ID_FALLBACK_LM:
                *((uint32_t*)&config_store.user_settings.fallback_lightmode) = value;
                break;
            case WIFI_CONFIG_ID_TURN_OFF:
                if(value == 1)
                    ESP.restart();
                else
                    hw_ctrl_turn_off();

                break;

            case WIFI_CONFIG_ID_STATUS_FREQUENCY:
                config_store.user_settings.status_refresh_period_ms = value;
                break;
            case WIFI_CONFIG_ID_SAVE_EEPROM:
                config_store_store();
                break;
            default: 
                return 1;
        }
    }
    return 0;
}

/**
 * Transmits all settings to the specified IP
 *
 * @param server_ip IP Address of the server
 *
 */
void wifi_tx_settings(IPAddress server_ip) {

    wifi_cts_config_frame->data.header.type = WIFI_CTS_SET_TYPE;
  
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_HW_REV] = config_store.hardware_data.hardware_revision;
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_SW_REV]=CONFIG_STORE_SW_REV_MAJ<<8 | CONFIG_STORE_SW_REV_MIN;
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_SERIAL_NO] = config_store.hardware_data.serial_number;
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_CONE_ID] = config_store.user_settings.cone_id;
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_FALLBACK_LM] = *((uint32_t*)&config_store.user_settings.fallback_lightmode);
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_TURN_OFF] = 0;
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_ADC_VOLTAGE] = adc_volt_meas;
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_ADC_TEMP] = adc_temp_deg;
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_STATUS_FREQUENCY] = config_store.user_settings.status_refresh_period_ms;
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_DEBUG1] = 111;
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_DEBUG2] = 0;
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_DEBUG3] = 0;
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_DEBUG4] = 0;  
    wifi_cts_config_frame->data.values[WIFI_CONFIG_ID_SAVE_EEPROM] = 0;
  
    Udp.beginPacket(server_ip, WIFI_UDP_TX_PORT);
    Udp.write(wifi_cts_config_frame->frame,sizeof(wifi_frame_header_t)+4*WIFI_CONFIG_ID_END);
    Udp.endPacket();
}


/**
 * Transmits a Status message
 *
 * @param server_ip IP Address of the server
 *
 */
void wifi_tx_status(IPAddress server_ip){
    // Update static information, if header is changed
    wifi_cts_status_frame->data.header.type = WIFI_CTS_STATUS_TYPE;
    wifi_cts_status_frame->data.cone_id = config_store.user_settings.cone_id;
    wifi_cts_status_frame->data.SoC = adc_soc;
    wifi_cts_status_frame->data.rssi = WiFi.RSSI();
    wifi_cts_status_frame->data.temp = adc_temp_deg;
    wifi_cts_status_frame->data.hall_state = hw_ctrl_get_hall_state();     
    
    Udp.beginPacket(server_ip, WIFI_UDP_TX_PORT);
    Udp.write(wifi_cts_status_frame->frame, sizeof(wifi_cts_status_frame_t));
    Udp.endPacket();
}


/**
 * Worker function which needs to be called periodically. 
 *
 */
void wifi_loop(void) {
    wifi_rx_frame();
    ota_loop();
}

/*
 * Transmit the status to the default IP address.
 */
void wifi_status_transmit(void){
    wifi_tx_status(wifi_server_ip);
}

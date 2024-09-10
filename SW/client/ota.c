/****************************)***************************************************/
/* 
 * File: ota.c
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file is used to abstract the ArduinoOTA Module for usage in the night-
 * cones. 
 */
/*******************************************************************************/
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

#include "ota.h"
#include "credentials.h"

/**
* Sets the OTA library ip with all handlers. 
*/
void ota_setup(void) {
  // Port defaults to 8266
  // ArduinoOTA.setPort(8266);

  // Hostname defaults to esp8266-[ChipID]
  // ArduinoOTA.setHostname("myesp8266");

#ifdef CRED_OTA_PW_MD5
    ArduinoOTA.setPasswordHash(CRED_OTA_PW_MD5);
#else    
  ArduinoOTA.setPassword(CRED_OTA_PW);
#endif

  // Connect to handler
  ArduinoOTA.onStart(ota_handle_start); 
  ArduinoOTA.onEnd(ota_handle_end);
  ArduinoOTA.onProgress(ota_handle_progress);  
  ArduinoOTA.onError(ota_handle_error);
  // Start OTA Task
  ArduinoOTA.begin();
#ifdef DEBUG
  Serial.println("Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
#endif
}

/**
* Handler Task for OTA Module.
*
*/
void ota_loop(void) {    
  ArduinoOTA.handle();
}

/****************** OTA Handler Procedures ********************************/

/**
 * Handler when OTA Update starts.
 *
 */
void ota_handle_start(void){
#ifdef DEBUG
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "sketch";
    } else { // U_SPIFFS
      type = "filesystem";
    }

    // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
    Serial.println("Start updating " + type);
#endif
}

/**
 * Handler to print out progress (only debug)
 * 
 */
void ota_handle_progress(unsigned int progress, unsigned int total) {
#ifdef DEBUG
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
#endif
}

/**
 * Handler when the OTA Update is finished.
 *
 */
void ota_handle_end(void){    
#ifdef DEBUG
    Serial.println("\nEnd");
#endif
}

/**
 * Handler to handle failed OTA Update.
 *
 */
void ota_handle_error(ota_error_t error) {
#ifdef DEBUG    
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
#endif
}


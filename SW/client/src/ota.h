/****************************)***************************************************/
/* 
 * File: ota.h
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file is used to abstract the ArduinoOTA Module for usage in the night-
 * cones. 
 */
/*******************************************************************************/

#ifndef OTA_H
#define OTA_H
#include <ArduinoOTA.h>
void ota_setup(void);
void ota_loop(void);

void ota_handle_start(void);
void ota_handle_progress(unsigned int progress, unsigned int total);
void ota_handle_end(void);
void ota_handle_error(ota_error_t error);



#endif
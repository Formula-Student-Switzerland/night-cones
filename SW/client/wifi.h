/****************************)***************************************************/
/* 
 * File: wifi.h
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file is used to handle all WIFI communication. This includes OTA, 
 * Handling of any communication to server. 
 */
/*******************************************************************************/
#ifndef WIFI_H
#define WIFI_H
#include <stdint.h>

#define WIFI_UDP_RX_PORT 5005
#define WIFI_UDP_TX_PORT 5006

int wifi_setup(void) ;
void wifi_loop(void);


#endif
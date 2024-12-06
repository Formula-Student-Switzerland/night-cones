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

#define WIFI_UDP_RX_PORT 5250
#define WIFI_UDP_TX_PORT 5251
#define WIFI_ATTEMPTS 3

#define WIFI_MAX_CONE_ID 60
#define WIFI_RX_BUFFER_SIZE (WIFI_MAX_CONE_ID*4+16-1)
#define WIFI_TX_BUFFER_SIZE 80

#define WIFI_COM_VERSION 1

#define WIFI_STC_DATA_TYPE 0
#define WIFI_STC_CONFIG_TYPE 1
#define WIFI_STC_SET_REQ_TYPE 2
#define WIFI_STC_STAT_REQ_TYPE 3
#define WIFI_CTS_STATUS_TYPE 128
#define WIFI_CTS_SET_TYPE 129

int wifi_setup(void);
void wifi_loop(void);
void wifi_status_transmit(void);


#endif
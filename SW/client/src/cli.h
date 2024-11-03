/*******************************************************************************/
/* 
 * File: cli.c
 * Author: Andreas Horat
 */
/*******************************************************************************/
/*
 * This file contains a very simple command line interface.
 */
/*******************************************************************************/
#ifndef CLI_H
#define CLI_H

#define LINE_BUF_SIZE 128
#define MAX_NUM_ARGS 8

#define CLI_ENABLED

void cli_init();
void cli_work();

#endif
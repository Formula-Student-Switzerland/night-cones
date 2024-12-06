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

#include "cli.h"
#include "Arduino.h"
#include "HardwareSerial.h"
#include "lightmodes.h"
#include "config_store.h"

#ifdef CLI_ENABLED


char line_buffer[LINE_BUF_SIZE];
char *arg_locs[MAX_NUM_ARGS];
uint8_t number_of_args;
uint8_t line_buffer_index;

// Function declarations
void cmd_help(void);
void cmd_led(void);
void cmd_saveEEPROM(void);
void cmd_readEEPROM(void);
void cmd_setSerialNo(void);
void cmd_led_fallback_store(void);

// List of functions pointers corresponding to each command
void (*cmd_func[])(void){
    &cmd_help,
    &cmd_led,
    &cmd_led_fallback_store,
    &cmd_saveEEPROM,
    &cmd_readEEPROM,
    &cmd_setSerialNo};

// List of command names
const char *cmd_str[] = {
    "help",
    "LED",
    "setLEDFallback",
    "saveEEPROM",
    "readEEPROM",
    "setSerialNo"};

int num_commands = sizeof(cmd_str) / sizeof(char *);
#endif

/**
 * Initialises the CLI
 */
void cli_init(void)
{
#ifdef CLI_ENABLED
    line_buffer_index = 0;
    number_of_args = 0;
    memset(line_buffer, 0, LINE_BUF_SIZE);
    Serial.printf("Serial Interface enabled.\r\n");
#endif
}

#ifdef CLI_ENABLED
/**
 * Read the line from the buffer
 *
 * @return Returns true if line is available in buffer.
 */
bool readline(void)
{
    if (Serial.available() == 0)
        return false;

    while (Serial.available())
    {
        line_buffer[line_buffer_index] = Serial.read();
        Serial.write(line_buffer[line_buffer_index]);
        Serial.flush();

        if (line_buffer[line_buffer_index] == '\n')
        {
            line_buffer[line_buffer_index] = 0;
            return line_buffer_index > 0;
        }

        if (++line_buffer_index == LINE_BUF_SIZE)
        {
            Serial.printf("Input String too long. Deleted.\r\n>");
            line_buffer_index = 0;
            memset(line_buffer, 0, LINE_BUF_SIZE);
        }
    }
    return false;
}

/**
 * Parse the line into the arguments
 *
 * @return Returns the number of available arguments
 */
int parseline(void)
{
    number_of_args = 0;

    arg_locs[number_of_args] = strtok(line_buffer, " ");
    while (arg_locs[number_of_args] != NULL)
    {
        if (++number_of_args >= MAX_NUM_ARGS)
        {
            Serial.printf("Input String contains too much arguments!\r\n>");
            return 0;
        }
        arg_locs[number_of_args] = strtok(NULL, " ");
    }

    return number_of_args;
}

/**
 * Executes the Command according to first argument
 */
void execute(void)
{
    for (int i = 0; i < num_commands; i++)
    {
        if (strcmp(arg_locs[0], cmd_str[i]) == 0)
        {
            (*cmd_func[i])();
            return;
        }
    }

    Serial.printf("Invalid Command.\r\n");
}
#endif

/**
 * CLI Worker function that executes the command if correct
 */
void cli_loop(void)
{
#ifdef CLI_ENABLED
    if (!readline())
        return;
    if (!parseline())
        return;
    execute();
    line_buffer_index = 0;
    memset(line_buffer, 0, LINE_BUF_SIZE);
#endif
}

#ifdef CLI_ENABLED
/**
 * Print Help Message
 */
void cmd_help(void)
{
    Serial.printf("Simple Interface for configuration only.\r\n");
}

/*********************** Functions ************************************/
/**
 * Set an LED State
 */
void cmd_led(void)
{
    uint8_t numbers[4];
    if (number_of_args != 5)
        return;

    char *end;
    for (uint8_t i = 0; i < 4; i++)
    {
        numbers[i] = strtol(arg_locs[i + 1], &end, 10);
    }
    lightmode_switch(numbers[0], numbers[1] << 4 | numbers[2], numbers[3]);
}

/**
 * Save the current lightmode as fallback
 */
void cmd_led_fallback_store(void)
{
    lightmode_setAsFallback();
}

/**
 * Saves the EEPROM including Hardware Part
 */
void cmd_saveEEPROM(void)
{
    Serial.printf("Saving Hardware Area: %d\r\n", config_store_storeHW());
    Serial.printf("Saving User Area: %d\r\n", config_store_store());
}

/**
 * Reads the value of the EEPROM and prints it to the Serial Port
 */
void cmd_readEEPROM(void)
{
    config_store_read();
    Serial.printf("Serial Number: %06d\r\n", config_store.hardware_data.serial_number);
    Serial.printf("Hardware Revision: %d\r\n", config_store.hardware_data.hardware_revision);
    Serial.printf("Hardware Data CRC: %d\r\n", config_store.hardware_data_crc);
    Serial.printf("Cone ID: %d\r\n", config_store.user_settings.cone_id);
    Serial.printf("Fallback Color: %d\r\n", config_store.user_settings.fallback_color);
    Serial.printf("Fallback Mode: %d\r\n", config_store.user_settings.fallback_lightmode);
    Serial.printf("Fallback Repetition Time: %d\r\n", config_store.user_settings.fallback_repetition_time);
    Serial.printf("Fallback Phase: %d\r\n", config_store.user_settings.fallback_phase);
    Serial.printf("User Settings CRC: %d\r\n", config_store.user_settings_crc);

    Serial.printf("Hex View\r\n");
    for (uint8_t i = 0; i < sizeof(config_store_t); i += 16)
    {
        Serial.printf("0x%02x ", i);
        for (uint8_t j = 0; j < 16; j += 4)
        {
            Serial.printf("%02x%02x%02x%02x\t", *(((uint8_t *)&config_store) + i + j),
                   *(((uint8_t *)&config_store) + i + j + 1),
                   *(((uint8_t *)&config_store) + i + j + 2),
                   *(((uint8_t *)&config_store) + i + j + 3));
            if (j == 12)
                Serial.printf(" \r\n");
        }
    }
}

/**
 * Set the Serial Number for the cone.
 */
void cmd_setSerialNo(void)
{
    uint16_t numbers[2];
    if (number_of_args != 3)
        return;

    char *end;
    for (uint8_t i = 0; i < 2; i++)
    {
        numbers[i] = strtol(arg_locs[i + 1], &end, 10);
    }

    config_store.hardware_data.serial_number = numbers[0];
    config_store.hardware_data.hardware_revision = numbers[1];
}
#endif
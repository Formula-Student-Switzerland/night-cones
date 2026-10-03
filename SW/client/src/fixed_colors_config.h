/*******************************************************************************/
/*
 * File: fixed_colors_config.h
 */
/*******************************************************************************/
/*
 * Configuration of the fixed color cones.
 *
 * Cones whose cone ID is listed below show the given light mode right after
 * switching them on, with or without WiFi. They connect to the WiFi in the
 * background, so they can be updated over the air and answer status requests,
 * but colors sent by the server are ignored. All other cones work as usual.
 *
 * The cone ID is the one stored in the EEPROM of the cone (e.g. set with
 * NumberAllCones in the server CLI). IDs set without saving to the EEPROM
 * are lost when the cone is switched off.
 *
 * Rebuild and flash the cones after changing this file.
 */
/*******************************************************************************/
#ifndef FIXED_COLORS_CONFIG_H
#define FIXED_COLORS_CONFIG_H

#include "color.h"
#include "fixed_colors.h"

// Set to 1 to enable the fixed color cones listed below, 0 to run all cones with WiFi
#define FIXED_COLORS_ENABLED 1

/*
 * One line per range of cone IDs. If an ID is in several lines, the first one is used.
 *
 *  first ID, last ID:  range of cone IDs, both included. Use the same ID twice for a single cone.
 *  color:              COLOR_RED, COLOR_YELLOW, COLOR_GREEN, COLOR_BLUE, COLOR_WHITE or 0-255
 *  brightness:         0 (off) - 15 (brightest)
 *  mode:               0 continuous, 1 blinking, 2 blinking short, 3 blinking long,
 *                      4 circulating, 5 circulating smooth, 6 fade, 7 rainbow fade,
 *                      8 rainbow circle
 *  repetition time:    cycle time of the mode in 0.1 s (1-255), 0 for continuous
 *
 * Blinking and fading cones are not synchronized to each other without WiFi.
 */
const fixed_color_t fixed_colors[] = {
//   first ID   last ID   color         brightness   mode   repetition time
    {0,         35,       COLOR_YELLOW,    15,          0,     0},
    {36,        70,       COLOR_BLUE,      15,          0,     0},
    {71,        105,      COLOR_RED,       15,          0,     0},
};

#endif

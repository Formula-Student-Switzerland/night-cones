/*******************************************************************************/
/*
 * File: fixed_colors.h
 */
/*******************************************************************************/
/*
 * This file is used to run cones with a fixed color that works without WiFi. The cones
 * are configured in fixed_colors_config.h.
 */
/*******************************************************************************/
#ifndef FIXED_COLORS_H
#define FIXED_COLORS_H
#include <stdint.h>

typedef struct {
    uint16_t first_id;
    uint16_t last_id;
    uint8_t color;
    uint8_t brightness;
    uint8_t mode;
    uint8_t repetition_time;
} fixed_color_t;

bool fixed_colors_setup(void);

#endif

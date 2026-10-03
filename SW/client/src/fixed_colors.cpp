/*******************************************************************************/
/*
 * File: fixed_colors.cpp
 */
/*******************************************************************************/
/*
 * This file is used to run cones with a fixed color that works without WiFi. The cones
 * are configured in fixed_colors_config.h.
 */
/*******************************************************************************/
#include "HardwareSerial.h"

#include "config_store.h"
#include "fixed_colors.h"
#include "fixed_colors_config.h"
#include "lightmodes.h"

/**
 * Checks if this cone is configured as fixed color cone. If so, its light mode
 * is set.
 *
 * @return True if the cone runs as fixed color cone.
 */
bool fixed_colors_setup(void)
{
#if FIXED_COLORS_ENABLED
    uint16_t cone_id = config_store.user_settings.cone_id;

    for (const fixed_color_t &entry : fixed_colors)
    {
        if (cone_id < entry.first_id || cone_id > entry.last_id)
            continue;

        lightmode_switch(entry.color, (entry.brightness << 4) | (entry.mode & 0x0F), entry.repetition_time);
        Serial.printf("Fixed color cone %d\r\n", cone_id);
        return true;
    }
#endif
    return false;
}

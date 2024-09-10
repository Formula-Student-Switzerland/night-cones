#ifndef CONFIG_STORE_H
#define CONFIG_STORE_H


enum config_store_ids{
    HARDWARE_REVISION
    CONE_ID,
    FALLBACK_LIGHTMODE,
    FALLBACK_COLOR
};




void config_store_setup(void);

int config_store_read(void);

int config_store_store(void);

int config_store_get(int id);


#endif
#ifndef LED_H
#define LED_H

#define LED_COUNT 20
#define LED_BOTTOM_COUNT 16

#define LED_PIN    4
#define LED_ESP_PIN 2

#define LED_ESP_FREQ_ON 250
#define LED_ESP_FREQ_READY 500
#define LED_ESP_FREQ_LIGHT 1000
#define LED_ESP_FREQ_LOOP 3000


#ifdef OUTPUT_PIN
    extern uint8_t led_state[LED_COUNT*3];


    int initLeds();
    int controlLeds(int *ledState);
    int clearLeds()
    
    void led_esp_blink(int frequency, int blinks);
    void led_show_status(uint8_t temp, uint8_t voltage);
#else
    int displayLeds(int *ledState);
#endif

#endif
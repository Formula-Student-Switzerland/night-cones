#ifdef OUTPUT_PIN
    int initLeds();
    int controlLeds(int *ledState);
    int clearLeds()
#else
    int displayLeds(int *ledState);
#endif
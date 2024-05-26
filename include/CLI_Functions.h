// CLI_Functions.h

#ifndef CLIFUNCTIONS_H
#define CLIFUNCTIONS_H

#include <FastLED.h>

void handleSendMessage(String msg, painlessMesh& mesh);
void handleBroadcastMessage(String msg, painlessMesh& mesh);
void changeLEDColor(String hexColorId, CRGB leds[], int numLeds);

#endif

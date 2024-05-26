// CLI_Functions.cpp

#include "CLI_Functions.h"

void handleSendMessage(String msg, painlessMesh& mesh) {
  int firstSpace = msg.indexOf(' ', 13);
  int secondSpace = msg.indexOf(' ', firstSpace + 1);  // Send_Message NodeID 1234567890123456 #FF000 //format
  String nodeId = msg.substring(13, firstSpace);
  String message = msg.substring(firstSpace + 1, secondSpace);
  String hexColorId = msg.substring(secondSpace + 1);
  String fullMessage = "NodeID " + nodeId + " says: " + message + "|Color:" + hexColorId;
  Serial.printf("nodeId = %s", nodeId.c_str());
  
  mesh.sendSingle(nodeId.toInt(), fullMessage);
  Serial.printf("Message %s with color %s to nodeID %d\n", message.c_str(), hexColorId.c_str(), nodeId.toInt());
}

void handleBroadcastMessage(String msg, painlessMesh& mesh) {
  int firstSpace = msg.indexOf(' ', 18);
  String message = msg.substring(18, firstSpace);
  String hexColorId = msg.substring(firstSpace + 1);
  String fullMessage = "Broadcast: " + message + "|Color:" + hexColorId;
  mesh.sendBroadcast(fullMessage);
  Serial.println("Broadcast Sent Successfully");
  Serial.println(fullMessage);
}

void changeLEDColor(String hexColorId, CRGB leds[], int numLeds) {
  long number = strtol(&hexColorId[1], NULL, 16);  // Convert hex to long
  int r = number >> 16;                            // First 2 digits of long
  int g = number >> 8 & 0xFF;                      // Middle 2 digits of long
  int b = number & 0xFF;                           // Last 2 digits of long
  for (int i = 0; i < numLeds; i++) {
    leds[i] = CRGB(r, g, b);
  }
  FastLED.show();
}

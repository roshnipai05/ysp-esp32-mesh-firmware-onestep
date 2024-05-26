#include <painlessMesh.h>
#include <FastLED.h>
#include "CLI_Functions.h"

// some gpio pin that is connected to an LED
#ifdef LED_BUILTIN
#define LED LED_BUILTIN
#else
#define LED 2
#endif

#define LED_PIN 13
#define NUM_LEDS 12

#define BLINK_PERIOD 3000   // milliseconds until cycle repeat
#define BLINK_DURATION 100  // milliseconds LED is on for

#define MESH_SSID "whateverYouLike"
#define MESH_PASSWORD "somethingSneaky"
#define MESH_PORT 5555

// Prototypes
void sendMessage();
void receivedCallback(uint32_t from, String& msg);
void newConnectionCallback(uint32_t nodeId);
void changedConnectionCallback();
void nodeTimeAdjustedCallback(int32_t offset);
void delayReceivedCallback(uint32_t from, int32_t delay);
void displayJsonTopology();
void handleSendMessage(String msg);
void handleBroadcastMessage(String msg);
void ChangeLEDcolor(String HexColorID);

Scheduler     userScheduler; // to control your personal task
painlessMesh  mesh;


bool calc_delay = false;
SimpleList<uint32_t> nodes;

// FastLED setup
CRGB leds[NUM_LEDS];

void sendMessage();                                                 // Prototype
Task taskSendMessage(TASK_SECOND * 1, TASK_FOREVER, &sendMessage);  // start with a one second interval

// Task to blink the number of nodes
Task blinkNoNodes;
bool onFlag = false;

void setup() {
  Serial.begin(115200);

  pinMode(LED, OUTPUT);

  FastLED.addLeds<NEOPIXEL, LED_PIN>(leds, NUM_LEDS);
  FastLED.clear();
  FastLED.show();

  mesh.setDebugMsgTypes(ERROR | DEBUG);  // set before init() so that you can see error messages
  mesh.setContainsRoot(true);            // root node: central point
  mesh.init(MESH_SSID, MESH_PASSWORD, &userScheduler, MESH_PORT);
  mesh.onReceive(&receivedCallback);
  mesh.onNewConnection(&newConnectionCallback);
  mesh.onChangedConnections(&changedConnectionCallback);
  mesh.onNodeTimeAdjusted(&nodeTimeAdjustedCallback);
  mesh.onNodeDelayReceived(&delayReceivedCallback);

  userScheduler.addTask(taskSendMessage);
  taskSendMessage.enable();

  blinkNoNodes.set(BLINK_PERIOD, (mesh.getNodeList().size() + 1) * 2, []() {
    // If on, switch off, else switch on
    if (onFlag)
      onFlag = false;
    else
      onFlag = true;
    blinkNoNodes.delay(BLINK_DURATION);

    if (blinkNoNodes.isLastIteration()) {
      // Finished blinking. Reset task for next run
      // blink number of nodes (including this node) times
      blinkNoNodes.setIterations((mesh.getNodeList().size() + 1) * 2);
      // Calculate delay based on current mesh time and BLINK_PERIOD
      // This results in blinks between nodes being synced
      blinkNoNodes.enableDelayed(BLINK_PERIOD - (mesh.getNodeTime() % (BLINK_PERIOD * 1000)) / 1000);
    }
  });
  userScheduler.addTask(blinkNoNodes);
  blinkNoNodes.enable();

  randomSeed(analogRead(A0));
}

void loop() {
  mesh.update();
  digitalWrite(LED, !onFlag);

  if (Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');
    Serial.printf("Received from serial: %s\n", msg.c_str());
    if (msg.startsWith("Send_Message")) {
      handleSendMessage(msg);
    } else if (msg.startsWith("Broadcast_Message")) {
      Serial.println("Broadcast Incoming");
      handleBroadcastMessage(msg);
    } else if (msg.equalsIgnoreCase("topology")) {
      displayJsonTopology();
    }
  }

  // Turn the appropriate number of LEDs to white
  int numNodes = mesh.getNodeList().size();
  for (int i = 0; i < NUM_LEDS; i++) {
    if (i < numNodes) {
      leds[i] = CRGB::White;
    } else {
      leds[i] = CRGB::Black;
    }
  }
  FastLED.show();
}

void sendMessage() {
  String msg = "Hello from Tarush's 2nd node ";
  msg += mesh.getNodeId();
  msg += " myFreeMemory: " + String(ESP.getFreeHeap());
  mesh.sendBroadcast(msg);

  if (calc_delay) {
    SimpleList<uint32_t>::iterator node = nodes.begin();
    while (node != nodes.end()) {
      mesh.startDelayMeas(*node);
      node++;
    }
    calc_delay = false;
  }

  Serial.printf("Sending message: %s\n", msg.c_str());

  taskSendMessage.setInterval(random(TASK_SECOND * 1, TASK_SECOND * 5));  // between 1 and 5 seconds
}

void receivedCallback(uint32_t from, String& msg) {
  Serial.printf("Received from %u msg=%s\n", from, msg.c_str());
  int colorIndex = msg.indexOf("|Color:");
  if (colorIndex != -1) {
    String hexColorId = msg.substring(colorIndex + 7);  // Skip over "|Color:"
    changeLEDColor(hexColorId);
  }
}

void newConnectionCallback(uint32_t nodeId) {
  // Reset blink task
  onFlag = false;
  blinkNoNodes.setIterations((mesh.getNodeList().size() + 1) * 2);
  blinkNoNodes.enableDelayed(BLINK_PERIOD - (mesh.getNodeTime() % (BLINK_PERIOD * 1000)) / 1000);
}

void changedConnectionCallback() {
  // Reset blink task
  onFlag = false;
  blinkNoNodes.setIterations((mesh.getNodeList().size() + 1) * 2);
  blinkNoNodes.enableDelayed(BLINK_PERIOD - (mesh.getNodeTime() % (BLINK_PERIOD * 1000)) / 1000);

  nodes = mesh.getNodeList();

  calc_delay = true;
}

void nodeTimeAdjustedCallback(int32_t offset) {
  Serial.printf("Adjusted time %u. Offset = %d\n", mesh.getNodeTime(), offset);
}

void delayReceivedCallback(uint32_t from, int32_t delay) {
  Serial.printf("Delay to node %u is %d us\n", from, delay);
}

void displayJsonTopology() {
  String json = mesh.subConnectionJson();
  Serial.println(json);
}

void handleSendMessage(String msg) {
  int firstSpace = msg.indexOf(' ', 13);
  int secondSpace = msg.indexOf(' ', firstSpace + 1);  //Send_Message NodeID 1234567890123456 #FF000 //format
  String nodeId = msg.substring(13, firstSpace);
  String message = msg.substring(firstSpace + 1, secondSpace);
  String hexColorId = msg.substring(secondSpace + 1);
  String fullMessage = "NodeID " + nodeId + " says: " + message + "|Color:" + hexColorId;
  Serial.printf("nodeId = %s", nodeId);
  
  mesh.sendSingle(nodeId.toDouble(), fullMessage);
  Serial.printf("Message %s with color %s to nodeID %d\n", message.c_str(), hexColorId.c_str(), nodeId.toDouble());
}

void handleBroadcastMessage(String msg) {
  int firstSpace = msg.indexOf(' ', 18);
  String message = msg.substring(18, firstSpace);
  String hexColorId = msg.substring(firstSpace + 1);
  String fullMessage = "Broadcast: " + message + "|Color:" + hexColorId;
  mesh.sendBroadcast(fullMessage);
  Serial.println("Broadcast Sent Successfully");
  Serial.println(fullMessage);
}

void changeLEDColor(String hexColorId) {
  long number = strtol(&hexColorId[1], NULL, 16);  // Convert hex to long
  int r = number >> 16;                            // First 2 digits of long
  int g = number >> 8 & 0xFF;                      // Middle 2 digits of long
  int b = number & 0xFF;                           // Last 2 digits of long
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CRGB(r, g, b);
  }
  FastLED.show();
}
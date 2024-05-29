#include <painlessMesh.h>
#include <ArduinoJson.h>
#include <vector>
#include <string>
#include <sstream>
#include <NeoPixelBus.h>
#ifdef LED_BUILTIN
#define LED LED_BUILTIN
#else
#define LED 2
#endif

#define LED_PIN 10
#define NUM_LEDS 5

#define BLINK_PERIOD 3000
#define BLINK_DURATION 100

#define MESH_SSID "whateverYouLike1"
#define MESH_PASSWORD "somethingSneaky1"
#define MESH_PORT 5555
#define VERSION "1.2.1"
DynamicJsonDocument doc(1024);
NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> strip(NUM_LEDS, LED_PIN);
// Prototypes
void sendMessage();
void receivedCallback(uint32_t from, String &msg);
void newConnectionCallback(uint32_t nodeId);
void changedConnectionCallback();
void nodeTimeAdjustedCallback(int32_t offset);
void delayReceivedCallback(uint32_t from, int32_t delay);
void displayJsonTopology();
void lightUpLEDsSequentially();
void lightUpLEDsOneByOne(RgbColor color, uint16_t delayTime);
void handleReceivedMessage(const JsonDocument &doc);
void processSerialInput();
std::vector<uint32_t> pathfinder(const painlessmesh::protocol::NodeTree &node, const String &prefix, const uint32_t endnode);
void pathlighting();

Scheduler userScheduler;
painlessMesh mesh;

bool calc_delay = false;
SimpleList<uint32_t> nodes;

Task taskSendMessage(TASK_SECOND * 1, TASK_FOREVER, &sendMessage);
// Task taskDelayer(TASK_SECOND * 0.5, TASK_FOREVER, &lightUpLEDsSequentially);
Task blinkNoNodes;
bool onFlag = false;

void setup()
{
  Serial.begin(115200);
  strip.Begin();
  strip.Show();
  Serial.printf("Starting Mesh Node... Version %s\n", VERSION);
  mesh.setDebugMsgTypes(ERROR | DEBUG);
  mesh.setContainsRoot(true);
  mesh.init(MESH_SSID, MESH_PASSWORD, &userScheduler, MESH_PORT);
  mesh.onReceive(&receivedCallback);
  mesh.onNewConnection(&newConnectionCallback);
  mesh.onChangedConnections(&changedConnectionCallback);
  mesh.onNodeTimeAdjusted(&nodeTimeAdjustedCallback);
  mesh.onNodeDelayReceived(&delayReceivedCallback);
  doc["From"] = mesh.getNodeId();
  userScheduler.addTask(taskSendMessage);
  // userScheduler.addTask(taskDelayer);

  blinkNoNodes.set(BLINK_PERIOD, (mesh.getNodeList().size() + 1) * 2, []()
                   {
    onFlag = !onFlag;
    blinkNoNodes.delay(BLINK_DURATION);

    if (blinkNoNodes.isLastIteration()) {
      blinkNoNodes.setIterations((mesh.getNodeList().size() + 1) * 2);
      blinkNoNodes.enableDelayed(BLINK_PERIOD -
                                 (mesh.getNodeTime() % (BLINK_PERIOD * 1000)) / 1000);
    } });
  userScheduler.addTask(blinkNoNodes);
  blinkNoNodes.enable();

  randomSeed(analogRead(A0));
}

void loop()
{
  mesh.update();
  digitalWrite(LED, !onFlag);

  processSerialInput();
}

std::vector<String> splitString(const String &str)
{
  std::vector<String> result;
  std::string stdStr = str.c_str();
  std::istringstream iss(stdStr);
  std::string word;

  while (std::getline(iss, word, ' '))
  {
    result.push_back(String(word.c_str()));
  }

  return result;
}

void processSerialInput()
{
  if (Serial.available() > 0)
  {
    String command = Serial.readStringUntil('\n');
    command.trim();
    std::vector<String> words = splitString(command);
    words[0].toLowerCase();

    if (!words.empty() && words[0] == "send")
    {
      unsigned long ulong = std::stoul(words[1].c_str(), nullptr, 10);
      String cipher_text;
      for (int i = 3; i < words.size(); i++)
      {
        cipher_text += words[i] + " ";
      }
      doc["msg"] = cipher_text;
      doc["to"] = ulong;
      doc["HEX"] = words[2];
      delayMicroseconds(100);
      taskSendMessage.enable();
    }
    else if (!words.empty() && words[0] == "topology")
    {
      displayJsonTopology();
    }
  }
}

void sendMessage()
{
  String msg;
  serializeJson(doc, msg);
  mesh.sendBroadcast(msg);
  if (doc["HEX"] != "false")
  {
    pathlighting();
  }

  taskSendMessage.disable();
  if (calc_delay)
  {
    for (auto node : nodes)
    {
      mesh.startDelayMeas(node);
    }
    calc_delay = false;
  }

  Serial.printf("Sending message: %s\n", msg.c_str());
}

void receivedCallback(uint32_t from, String &msg)
{
  Serial.printf("Received %s\n", msg.c_str());

  DynamicJsonDocument receivedDoc(1024);
  deserializeJson(receivedDoc, msg);
  handleReceivedMessage(receivedDoc);
}

void newConnectionCallback(uint32_t nodeId)
{
  onFlag = false;
  blinkNoNodes.setIterations((mesh.getNodeList().size() + 1) * 2);
  blinkNoNodes.enableDelayed(BLINK_PERIOD - (mesh.getNodeTime() % (BLINK_PERIOD * 1000)) / 1000);
}

void changedConnectionCallback()
{
  onFlag = false;
  blinkNoNodes.setIterations((mesh.getNodeList().size() + 1) * 2);
  blinkNoNodes.enableDelayed(BLINK_PERIOD - (mesh.getNodeTime() % (BLINK_PERIOD * 1000)) / 1000);

  nodes = mesh.getNodeList();
  calc_delay = true;
}

void nodeTimeAdjustedCallback(int32_t offset)
{
  Serial.printf("Adjusted time %u. Offset = %d\n", mesh.getNodeTime(), offset);
}

void delayReceivedCallback(uint32_t from, int32_t delay)
{
  Serial.printf("Delay to node %u is %d us\n", from, delay);
}

void displayJsonTopology()
{
  String topology_json = mesh.subConnectionJson(true);
  Serial.println(topology_json);
}
void lightUpLEDsSequentially(String hexColorId)
{
  long number = strtol(&hexColorId[1], NULL, 16); // Convert hex to long
  int r = number >> 16;                           // First 2 digits of long
  int g = number >> 8 & 0xFF;                     // Middle 2 digits of long
  int b = number & 0xFF;
  lightUpLEDsOneByOne(RgbColor(r, g, b), 500); // 500ms delay between each LED lighting up
  // delay(1000);

  // Turn off all LEDs
  lightUpLEDsOneByOne(RgbColor(0, 0, 0), 500); // 500ms delay between each LED turning off
  // delay(1000);
}

void lightUpLEDsOneByOne(RgbColor color, uint16_t delayTime)
{
  for (uint16_t i = 0; i < NUM_LEDS; i++)
  {
    strip.SetPixelColor(i, color);
    strip.Show();
    delay(delayTime);
  }
}
void handleReceivedMessage(const JsonDocument &doc)
{
  if (doc["type"] == "lit" && doc["HEX"] != "false")
  {
    // Serial.printf(doc["HEX"].as<String>());
    lightUpLEDsSequentially(doc["HEX"].as<String>());
  }
}

std::vector<uint32_t> path;
std::vector<uint32_t> final_path;
std::vector<uint32_t> pathfinder(const painlessmesh::protocol::NodeTree &node, const String &prefix, const uint32_t endnode)
{
  // Serial.printf(prefix + String(node.nodeId));

  path.push_back(node.nodeId);
  if (endnode == node.nodeId)
  {
    final_path = path;
    path.clear();
    Serial.printf("Node Found\n");
    Serial.print("Time_pathfinder_end: ");
    Serial.println(micros());
    return final_path;
  }
  for (const auto &child : node.subs)
  {
    if (!pathfinder(child, prefix + "  ", endnode).empty())
    {
      return final_path;
    } // Indent for children
  }
  path.pop_back();

  Serial.printf("Time_pathfinder_end: ");
  Serial.println(micros());

  return {};
}
void pathlighting()
{
  DynamicJsonDocument pathjson(1024);
  pathjson["type"] = "lit";
  pathjson["HEX"] = doc["HEX"];

  String msg;
  serializeJson(pathjson, msg);
  // Serial.printf(mesh.subConnectionJson());

  painlessmesh::protocol::NodeTree structure = mesh.asNodeTree();
  Serial.print("Time_pathfinder_start: ");
  Serial.println(micros());
  Serial.print("memory: ");
  Serial.println(ESP.getFreeHeap());
  std::vector<uint32_t> light_the_path = pathfinder(structure, "", doc["to"]);
  for (auto node : light_the_path)
  {
    Serial.println(node);
    mesh.sendSingle(node, msg);
    delayMicroseconds(100);
  }
}
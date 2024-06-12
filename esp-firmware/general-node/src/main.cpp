#include "config.hpp"
#include "serial_interface.hpp"
#include "lighting.hpp"
// #include "mesh.hpp"

#define LED_ANIMATE_DELAY 300
#define LED_PIN 10
#define BAUD_RATE 115200
#define NV_STORE_ON_SET true
#define DELAYED_BOOT_START 5000

void onReceiveCallback(uint32_t from_node_id, String &received_stringified_mesh_json);
void processLightingOnMessageReceive(JsonDocument &received_serial_mesh_json);

void sendMeshMessageCallback(JsonDocument &stringified_json_mesh);

void pathLighting();


#if defined(ROOT_NODE)
    #define IS_ROOT_NODE true
#else 
    #define IS_ROOT_NODE false
#endif



// Class Instantiation
Scheduler user_scheduler;
Preferences prefs;
NodeConfig *config;
Mesh *mesh;
SerialInterface *serial_interface;
Lighting *lighting;

/*
    -using TaskCallback and TaskOnDisable-
    Positional Arguments:
    Task(unsigned long aInterval, long aIterations, TaskCallback aCallback, Scheduler* aScheduler, bool aEnable, TaskOnEnable aOnEnable, TaskOnDisable aOnDisable, bool aSelfdestruct);
*/
Task task_light_animate_off(LED_ANIMATE_DELAY, NUM_LED, []()
                            { lighting->lightAnimate(); }, NULL, false, NULL, []()
                            { lighting->lightReset(); });

Task task_light_animate(LED_ANIMATE_DELAY, NUM_LED, []()
                        { lighting->lightAnimate(); }, NULL, false, NULL, []()
                        { lighting->lightReset();
                          task_light_animate_off.restart(); });

Task task_log_config(TASK_IMMEDIATE, TASK_ONCE, []()
                     {  config->logConfig();
                        task_light_animate.restart(); });

Task task_process_serial(TASK_IMMEDIATE, TASK_FOREVER, []()
                         { serial_interface->processSerial(); });

// Root Node Task

#if defined(ROOT_NODE)

Task auto_dump_esp_counter(TASK_SECOND * 5, TASK_FOREVER, []()
                           { Serial.printf("Node Count: %d\n", mesh->getNodesCount()); });

Task auto_dump_esp_topology(TASK_SECOND * 5, TASK_FOREVER, []()
                            { Serial.println(mesh->getTopology(true)); });

#endif

Task task_path_lighting(TASK_IMMEDIATE, TASK_ONCE, &pathLighting);

void setup()
{
    Serial.begin(BAUD_RATE);

    ulong start_time = millis();

    while ((millis() - start_time) < DELAYED_BOOT_START)
    {
        Serial.printf(". ");
        delay(1000);
    }
    Serial.print("Starting Node...\n");

    if (!prefs.begin("node_config", false))
    {
        Serial.println("Failed to open Preferences");
        prefs.clear();
    }

    config = new NodeConfig(IS_ROOT_NODE, user_scheduler, LED_PIN, NUM_LED, Serial, VERSION, prefs, NV_STORE_ON_SET);
    mesh = new Mesh(*config);
    serial_interface = new SerialInterface(*config, *mesh);
    serial_interface->setSendMessageCallable(&sendMeshMessageCallback);
    lighting = new Lighting(*config, *mesh);

    delay(100);

    // Start the mesh
    mesh->init();
    mesh->onReceive(onReceiveCallback);

    user_scheduler.addTask(task_log_config);
    task_log_config.enableDelayed(1000);

    user_scheduler.addTask(task_process_serial);
    task_process_serial.enable();

    user_scheduler.addTask(task_light_animate);
    user_scheduler.addTask(task_light_animate_off);
    // task_light_animate.enable();

    user_scheduler.addTask(task_path_lighting);

    #if defined(ROOT_NODE)
    user_scheduler.addTask(auto_dump_esp_counter);
    auto_dump_esp_counter.enable();

    user_scheduler.addTask(auto_dump_esp_topology);
    auto_dump_esp_topology.enable();
    #endif
}

void loop()
{
    mesh->loop();
}

void onReceiveCallback(uint32_t from_node_id, String &received_stringified_mesh_json)
{
    JsonDocument received_serial_mesh_json;
    deserializeJson(received_serial_mesh_json, received_stringified_mesh_json);
    serial_interface->displayLiveMessage(received_serial_mesh_json);
    processLightingOnMessageReceive(received_serial_mesh_json);
}

void processLightingOnMessageReceive(JsonDocument &received_serial_mesh_json)
{
    if (received_serial_mesh_json.containsKey("lighting"))
    {
        if (received_serial_mesh_json["lighting"].containsKey("color"))
        {
            lighting->setLightColor(received_serial_mesh_json["lighting"]["color"].as<String>());
            task_light_animate.restart();
        }
    }
}

void sendMeshMessageCallback(JsonDocument &serial_json_mesh)
{
    String stringified_json_mesh;
    serializeJson(serial_json_mesh, stringified_json_mesh);
    mesh->sendMessage(0, stringified_json_mesh, true);
    // send lightup messages
    if (serial_json_mesh["payload"]["HEX"] != "false")
    {
        lighting->setEndNodeId(serial_json_mesh["payload"]["to_node_id"].as<String>());
        lighting->setLightColor(serial_json_mesh["payload"]["HEX"].as<String>());
        task_light_animate.restart();
        task_path_lighting.restart();
    }
}

void pathLighting()
{
    lighting->pathFinder();
    lighting->sendPathLightingMessages();
}
/*
    * Node Config:

        * Light Config:
            * Led Count
            * Led Pin
            *! NeoPixelBus Object ( TBD)

        * Serial Config:
            * Serial Object

        * Mesh Config:
            * SSID
            * PSK
            * Port
            * Contains Root
            * Set Root
            * Scheduler ( User instantiated )

        * Room Config:
            * Room ID
            * Description (optional)
*/

#pragma once

#include <Arduino.h>
#include <string.h>
#include <painlessMesh.h>
#include <vector>
#include <Preferences.h>

using namespace std;

#if defined(ARDUINO_XIAO_ESP32C3)
#define HardwareSerial HWCDC
#endif

/**
 * @brief Mesh Configuration
 * The `MeshConfig` class is defining a configuration structure for a mesh network setup. It includes the following members:
 * 
 * - `ssid` : The SSID of the mesh network
 * - `password` : The password of the mesh network
 * - `port` : The port number of the mesh network
 * - `containsRoot` : A boolean flag to check if the mesh network contains a root node
 * - `setRoot` : A boolean flag to set the root node
 * - `scheduler` : A pointer to the scheduler instance
 */

class MeshConfig
{
public:
    String ssid;

    String password;

    uint16_t port;

    bool containsRoot;

    bool setRoot;

    Scheduler *scheduler;
};


/**
 * @brief Light Configuration
 * The `LightConfig` class is defining a configuration structure for the light setup. It includes the following members:
 * 
 * - `effect_speed` : The speed of the light effect
 * - `led_pin` : The pin number of the LED
 * - `led_count` : The count of the LEDs on the NeoPixel strip
 */
class LightConfig
{
public:
    uint8_t effect_speed;

    uint8_t led_pin;

    uint8_t led_count;
};

/**
 * @brief UART Configuration
 * The `UART_Config` class is defining a configuration structure for the UART setup. It includes the following members:
 * 
 * - `serial` : A pointer to the HardwareSerial object
 */
class UART_Config
{
public:
    HardwareSerial *serial;
};

/**
 * @brief Room Configuration
 * The `RoomConfig` class is defining a configuration structure for the room setup. It includes the following members:
 * 
 * - `id` : The ID of the room
 */
class RoomConfig
{
public:
    uint8_t id;
};


/**
 * @brief Node Configuration
 * The `NodeConfig` class is defining a configuration structure for the node setup. It includes the following public members:
 * 
 * - `node_id` : The ID of the node
 * - `version` : The version of the node
 * - `room_config` : The room configuration
 * - `mesh_config` : The mesh configuration
 * - `light_config` : The light configuration
 * - `serial_config` : The UART configuration
 * - `nv_store_on_set` : A boolean flag to store the configuration in the EEPROM on set operation for base network credentials and room ID
 * - `prefs` : A pointer to the Preferences object
 * - `base_ssid` : The SSID of the base network
 * - `base_password` : The password of the base network
 * - `default_base_ssid` : The default SSID of the base network
 * - `default_base_password` : The default password of the base network
 * - `default_room_id` : The default ID of the room
 * - `nv_store_namespace` : The namespace of the non-volatile store
 */
class NodeConfig
{
private:
    bool nv_store_on_set;

    vector<String> getWirelessCredentialsFromRoomId();
    Preferences *prefs;
    String base_ssid;
    String base_password;

    /**
     * @brief Loads the saved configuration from the EEPROM or sets the default configuration
     * 
     */
    void loadSavedConfigOrSetDefault();

    /**
     * @brief Generates the wireless credentials from the Room ID and the Base Network Credentials and sets them
     * 
     */
    void setWirelessCredentials();

    /** 
     * @brief Namespace for the non-volatile store.
    */
    String nv_store_namespace = "node_config";


    String default_base_ssid = DEFAULT_BASE_SSID;
    String default_base_password = DEFAULT_BASE_PASSWORD;
    uint8_t default_room_id = ROOM_NUMBER;

public:
    uint32_t node_id;

    String version;

    RoomConfig room_config;

    MeshConfig mesh_config;

    LightConfig light_config;

    UART_Config serial_config;

    /**
     * @brief Set the Node Id object
     *
     * @param node_id
     */
    void setNodeId(uint32_t node_id);
    /**
     * @brief Get the Node Id object
     *
     * @return uint32_t node_id
     */
    uint32_t getNodeId();

    /**
     * @brief Set the Room Id object
     *
     * @param room_id
     */
    void setRoomId(uint8_t room_id);

    /**
     * @brief Get the Room Id object
     *
     * @return uint8_t room_id
     */
    uint8_t getRoomId();

    /**
     * @brief Set the Base Network Credentials object
     *
     * @param base_ssid
     * @param base_password
     */
    void setBaseNetworkCredentials(String base_ssid, String base_password);

    /**
     * @brief Get the Base Network Credentials object
     *
     * @return vector<String> base_network_credentials
     */
    vector<String> getBaseNetworkCredentials();

    /**
     * @brief Set the Wireless Credentials object
     * Note : These are generated from the Room ID and the Base Network Credentials
     *
     * @param ssid
     * @param password
     */
    vector<String> getWirelessCredentials();

    /**
     * @brief Saves the current state of config in the EEPROM
     *
     * @return true Save Successful!
     * @return false Save Unsuccessful :(
     */
    bool save();

    /**
     * @brief
     *
     * @param name Namespace name of the config to load from
     * @return true Load Successful
     * @return false Load Unsuccessful :(
     */
    bool load();

    /**
     * @brief  Logs the current state of the config on the Serial Monitor
     *
     */
    void logConfig();
    /**
     * @brief Construct a new Node Config:: Node Config object
     *
     * @param isRoot Weather this node is a root node (There can only be one)
     * @param scheduler Scheduler Instance
     * @param led_pin
     * @param led_count
     * @param serial
     * @param version
     * @param nv_store_on_set
     */
    // Constructor
    NodeConfig(bool isRoot, Scheduler &scheduler, uint8_t led_pin, uint8_t led_count, HardwareSerial &serial, String version, Preferences &prefs, bool nv_store_on_set);
};
#include <HardwareSerial.h>
#include <ArduinoJson.h>
#include <painlessMesh.h>
#include "mesh.hpp"

/**
 * @brief Serial Interface Class
 *
 * Private Members:
 * - `serial` : A pointer to the HardwareSerial object
 * - `mesh` : A pointer to the Mesh object
 * - `nodeId` : The node ID of the current node
 *
 *
 */
class SerialInterface
{
private:
    HardwareSerial *serial;
    Mesh *mesh;
    NodeConfig *nodeConfig;

    /**
     * @brief Function pointer to keep callback funtion from Main for sending message to the mesh network
     */
    void (*sendMessageCallable)(JsonDocument &serial_json_mesh);

    //  SETTERS     //

    /**
     * @brief Set the Room Id in the Node Config
     *
     * @param incoming_serial_json
     */
    void setRoomId(JsonDocument &incoming_serial_json);

    /**
     * @brief Set the Base Network Credentials in the Node Config
     *
     * @param incoming_serial_json
     */
    void setBaseNetworkCredentials(JsonDocument &incoming_serial_json);

    //  GETTERS     //

    /**
     * @brief Process the incoming command "get-room-id" and respond with the room id of the node
     *
     * @param incoming_serial_json
     */
    void getRoomId(JsonDocument &incoming_serial_json);

    /**
     * @brief Process the incoming command "get-wirells-credentials" and respond with the wireless credentials of the node
     *
     * @param incoming_serial_json
     */
    void getWirelessCredentials(JsonDocument &incoming_serial_json);

    /**
     * @brief Process the incoming command "get-base-network-credentials" and respond with the base network credentials of the node
     *
     * @param incoming_serial_json
     */
    void getBaseNetworkCredentials(JsonDocument &incoming_serial_json);

    /**
     * @brief Wrapper to send the response back to the serial interface against the incoming commands
     *
     * @param response_serial_json
     * @param incoming_serial_json
     */
    void sendResponse(JsonDocument &response_serial_json, JsonDocument &incoming_serial_json);

    /**
     * @brief Process the incoming command "topology" and respond with the topology of the mesh network
     *
     * @param pretty
     * @param incoming_serial_json
     */
    void sendTopology(bool pretty, JsonDocument &incoming_serial_json);

    /**
     * @brief Process incoming command "ping" and build the mesh message to be sent then call the sendMessageCallable callback
     *
     * @param incoming_serial_json
     */
    void sendMessage(JsonDocument &incoming_serial_json);

public:
    /**
     * @brief Set the Send Message Callable from Main
     *
     * @param sendMessageCallback
     */
    void setSendMessageCallable(void (*sendMessageCallback)(JsonDocument &stringified_json_mesh));

    /**
      * @brief logs the received payload from the mesh network on the serial interface
      *
      * @param payload  json object of the received message.
      */
    void displayLiveMessage(JsonDocument payload);

    /**
     * @brief Performs serial interface sub-routine. Put this in your void loop();
     *
     *  Performs the following when called.
     *      1. Checks the Serial Buffer
     *      2. Performs relevant action else discard
     */
    void processSerial();

    /**
     * @brief Construct a new serial interface object
     *
     * @param serial Reference to already instantiated HardwareSerial object
     */
    SerialInterface(NodeConfig &config, Mesh &mesh);
};

#include "serial_interface.hpp"

using namespace std;

SerialInterface::SerialInterface(NodeConfig &config, Mesh &mesh)
{
    this->serial = config.serial_config.serial;
    this->mesh = &mesh;
    this->nodeConfig = &config;
}

void SerialInterface::setSendMessageCallable(void (*sendMessageCallback)(JsonDocument &serial_json_mesh))
{
    this->sendMessageCallable = sendMessageCallback;
}

void SerialInterface::sendResponse(JsonDocument &response_serial_json, JsonDocument &incoming_serial_json)
{
    incoming_serial_json["payload"]["response"] = response_serial_json;
    String stringified_json_response;

    serializeJson(incoming_serial_json, *this->serial);
    this->serial->println();
}

void SerialInterface::sendMessage(JsonDocument &incoming_serial_json)
{
    JsonDocument serial_json_mesh;

    serial_json_mesh["payload_type"] = "mesh";
    serial_json_mesh["payload"]["from_node_id"] = this->nodeConfig->getNodeId();
    serial_json_mesh["payload"]["to_node_id"] = incoming_serial_json["payload"]["to_node_id"];
    serial_json_mesh["payload"]["HEX"] = incoming_serial_json["payload"]["HEX"];
    serial_json_mesh["payload"]["msg"] = incoming_serial_json["payload"]["msg"];

    this->sendMessageCallable(serial_json_mesh);

    this->sendResponse(serial_json_mesh, incoming_serial_json);
}

void SerialInterface::sendTopology(bool pretty, JsonDocument &incoming_serial_json)
{

    String topology = this->mesh->getTopology(pretty);

    JsonDocument response_serial_json;
    deserializeJson(response_serial_json, topology);

    this->sendResponse(response_serial_json, incoming_serial_json);
}

void SerialInterface::setRoomId(JsonDocument &incoming_serial_json_payload)
{
    uint8_t new_room_id = int(incoming_serial_json_payload["payload"]["room_id"]);
    this->nodeConfig->setRoomId(new_room_id);

    JsonDocument response_serial_json;
    bool success = (this->nodeConfig->getRoomId() == new_room_id);

    response_serial_json["success"] = success;
    response_serial_json["room_id"] = new_room_id;

    this->sendResponse(response_serial_json, incoming_serial_json_payload);
}

void SerialInterface::setBaseNetworkCredentials(JsonDocument &incoming_serial_json_payload)
{
    // set the base network credentials
    String new_base_ssid = incoming_serial_json_payload["payload"]["base_ssid"].as<String>();
    String new_base_password = incoming_serial_json_payload["payload"]["base_password"].as<String>();
    this->nodeConfig->setBaseNetworkCredentials(new_base_ssid, new_base_password);

    JsonDocument response_serial_json;
    vector<String> new_base_network_credentials = this->nodeConfig->getBaseNetworkCredentials();
    bool success = (new_base_network_credentials[0] == new_base_ssid && new_base_network_credentials[1] == new_base_password);

    response_serial_json["success"] = success;
    response_serial_json["base_ssid"] = new_base_network_credentials[0];
    response_serial_json["base_password"] = new_base_network_credentials[1];

    this->sendResponse(response_serial_json, incoming_serial_json_payload);
}

void SerialInterface::getRoomId(JsonDocument &incoming_serial_json_payload)
{
    JsonDocument response_serial_json;
    response_serial_json["room_id"] = this->nodeConfig->getRoomId();

    this->sendResponse(response_serial_json, incoming_serial_json_payload);
}

void SerialInterface::getWirelessCredentials(JsonDocument &incoming_serial_json_payload)
{
    JsonDocument response_serial_json;
    vector<String> wireless_credentials = this->nodeConfig->getWirelessCredentials();

    response_serial_json["ssid"] = wireless_credentials[0];
    response_serial_json["password"] = wireless_credentials[1];

    this->sendResponse(response_serial_json, incoming_serial_json_payload);
}

void SerialInterface::getBaseNetworkCredentials(JsonDocument &incoming_serial_json_payload)
{
    JsonDocument response_serial_json;
    vector<String> base_network_credentials = this->nodeConfig->getBaseNetworkCredentials();

    response_serial_json["base_ssid"] = base_network_credentials[0];
    response_serial_json["base_password"] = base_network_credentials[1];

    this->sendResponse(response_serial_json, incoming_serial_json_payload);
}

void SerialInterface::displayLiveMessage(JsonDocument payload)
{
    serializeJson(payload, *this->serial);
    this->serial->println();
}

void SerialInterface::processSerial()
{
    if (this->serial->available())
    {
        String incoming_stringified_json = this->serial->readStringUntil('\n');
        incoming_stringified_json.trim();
        JsonDocument incoming_serial_json;
        deserializeJson(incoming_serial_json, incoming_stringified_json);

        if (incoming_serial_json["payload"]["cmd"] == "ping")
        {
            this->sendMessage(incoming_serial_json);
        }
        else if (incoming_serial_json["payload"]["cmd"] == "capture-topology")
        {
            this->sendTopology(false, incoming_serial_json);
        }
        else if (incoming_serial_json["payload"]["cmd"] == "topology")
        {
            this->sendTopology(true, incoming_serial_json);
        }
        else if (incoming_serial_json["payload"]["cmd"] == "set-room-id")
        {
            this->setRoomId(incoming_serial_json);
        }
        else if (incoming_serial_json["payload"]["cmd"] == "set-base-network-credentials")
        {
            this->setBaseNetworkCredentials(incoming_serial_json);
        }
        else if (incoming_serial_json["payload"]["cmd"] == "get-room-id")
        {
            this->getRoomId(incoming_serial_json);
        }
        else if (incoming_serial_json["payload"]["cmd"] == "get-wireless-credentials")
        {
            this->getWirelessCredentials(incoming_serial_json);
        }
        else if (incoming_serial_json["payload"]["cmd"] == "get-base-network-credentials")
        {
            this->getBaseNetworkCredentials(incoming_serial_json);
        }
        else if (incoming_serial_json["payload"]["cmd"] == "esp-reset")
        {
            ESP.restart();
        }
        else
        {
            this->serial->println("Invalid Command");
        }
        // process the commands
    }
}
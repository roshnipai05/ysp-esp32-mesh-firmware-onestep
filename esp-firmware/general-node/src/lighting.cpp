#include "lighting.hpp"

/**
 * Constructs a Lighting object.
 *
 * This constructor initializes a Lighting object with NodeConfig.
 * It sets the number of LEDs, LED pin, LedState, and HexColorID based on the provided configuration.
 *
 * It inherits the LED strip from the NeoPixelBus library and initializes the taskLightAnimate with a callback function to run the NextLight method every second.
 */
Lighting::Lighting(NodeConfig &config, Mesh &mesh) : ledStrip(config.light_config.led_count, config.light_config.led_pin)
{
    this->mesh = &mesh;
    this->serial = config.serial_config.serial;
    this->led_count = config.light_config.led_count;
    this->led_gpio_pin = config.light_config.led_pin;
    this->current_led_index = 0;
    this->ledStrip.Begin();
    this->ledStrip.SetLuminance(175);
    this->ledStrip.Show();
    this->setLightColor("#FF69B4");
}

/**
 * Sets the color of the LED strip.
 *
 * @param hex_color_id The hexadecimal color code to set the LED strip to.
 */
void Lighting::setLightColor(String hex_color_id)
{
    this->hex_color.Parse<HtmlColorNames>(hex_color_id);
}

void Lighting::lightAnimate()
{
    this->ledStrip.SetPixelColor(this->current_led_index, this->hex_color);
    this->ledStrip.Show();
    this->current_led_index++;
}

void Lighting::lightReset()
{
    this->setLightColor("black");
    this->current_led_index = 0;
}

void Lighting::setEndNodeId(String end_node_id)
{
    this->end_node_id = static_cast<uint32_t>(stoul(end_node_id.c_str()));
}

void Lighting::pathFinder()
{
    this->path_to_end_node = this->mesh->getPathToNode(this->end_node_id);
}

void Lighting::sendPathLightingMessages()
{
    if (this->path_to_end_node.empty())
    {
        this->serial->println("No path to end node found to light up.");
        return;
    }

    JsonDocument serial_json_mesh;
    String stringified_json_mesh;
    char hex_color_string[8];

    this->hex_color.ToString<HtmlShortColorNames>(hex_color_string, 8);
    serial_json_mesh["lighting"]["color"] = hex_color_string;
    serializeJson(serial_json_mesh, stringified_json_mesh);

    for (uint32_t node_id : this->path_to_end_node)
    {
        this->mesh->sendMessage(node_id, stringified_json_mesh, false);
    }
}
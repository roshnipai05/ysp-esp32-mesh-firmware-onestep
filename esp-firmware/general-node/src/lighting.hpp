#include <NeoPixelBusLg.h>
#include "config.hpp"
#include "mesh.hpp"

/**
 * @class Lighting
 * @brief Represents the lighting functionality of a node.
 *
 * The Lighting class provides methods to control the LED strip connected to the node.
 * It allows changing the color of the LEDs and animating the lighting effects.
 */
class Lighting
{
private:
    uint8_t led_gpio_pin;
    uint8_t current_led_index;
    // String hex_color_id;
    NeoPixelBusLg<NeoGrbFeature, Neo800KbpsMethod> ledStrip;
    HtmlColor hex_color;
    Mesh *mesh;
    HardwareSerial *serial;
    vector<uint32_t> path_to_end_node;
    uint32_t end_node_id;

public:
    uint16_t led_count;

    void setEndNodeId(String end_node_id);

    void pathFinder();

    void sendPathLightingMessages();

    /**
     * @brief Runs the lighting effect.
     *
     * This method changes the lighting effect to the next available effect.
     */
    void lightAnimate();

    /**
     * @brief Sets the color of the LED strip.
     *
     * @param hex_color_id The hexadecimal color code to set the LED strip to.
     */
    void setLightColor(String hex_color_id);

    void lightReset();

    /**
     * @brief Constructs a new Lighting object.
     *
     * @param config The configuration object for the node.
     */
    Lighting(NodeConfig &config, Mesh &mesh);
};
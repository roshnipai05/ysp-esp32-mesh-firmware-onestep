#include "topology.h"

JsonDocument getTopology(painlessMesh &mesh)
{
    JsonDocument doc;
    auto strigified_mesh_topology = mesh.subConnectionJson();
    deserializeJson(doc, strigified_mesh_topology);
    return doc;
}
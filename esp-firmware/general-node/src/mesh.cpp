#include "mesh.hpp"

void Mesh::init()
{

    this->mesh.setDebugMsgTypes(ERROR | DEBUG);

    if (this->config->containsRoot)
    {
        this->mesh.setContainsRoot(true);
    }

    if (this->config->setRoot)
    {
        this->mesh.setRoot(true);
    }

    this->mesh.init(this->config->ssid.c_str(), this->config->password.c_str(), this->config->scheduler);
    this->nodeConfig->setNodeId(this->mesh.getNodeId());
}

void Mesh::loop()
{
    this->mesh.update();
}

void Mesh::sendMessage(uint32_t to, String msg, bool is_broadcast)
{
    if (is_broadcast)
    {
        this->mesh.sendBroadcast(msg);
    }
    else
    {
        this->mesh.sendSingle(to, msg);
    }
}

String Mesh::getTopology(bool pretty = false)
{
    return this->mesh.subConnectionJson(pretty);
}

void Mesh::onReceive(void (*callback)(uint32_t from, String &msg))
{
    this->mesh.onReceive(callback);
}

vector<uint32_t> Mesh::pathFinder(painlessmesh::protocol::NodeTree &node, uint32_t end_node)
{
    if (node.nodeId == end_node)
    {
        return {node.nodeId};
    }

    if (node.subs.size())
    {
        for (painlessmesh::protocol::NodeTree &child : node.subs)
        {
            vector<uint32_t> path = pathFinder(child, end_node);
            if (!path.empty())
            {
                path.push_back(node.nodeId);
                return path;
            }
        }
    }
    return {};
}

vector<uint32_t> Mesh::getPathToNode(uint32_t end_node)
{
    painlessmesh::protocol::NodeTree node = this->mesh.asNodeTree();
    return pathFinder(node, end_node);
}

uint32_t Mesh::getOwnNodeId()
{
    return this->mesh.getNodeId();
}

int Mesh::getNodesCount(){
    return this -> mesh.getNodeList().size();}

Mesh::Mesh(NodeConfig &node_config)
{
    this->config = &node_config.mesh_config;
    this->nodeConfig = &node_config;
}

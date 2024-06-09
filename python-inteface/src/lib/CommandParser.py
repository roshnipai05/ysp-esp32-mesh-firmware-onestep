import json

from Config import TOPOLOGY_FILE, log as logger
from Config import decrypt

class CommandParser:
    """
    Class to parse command strings passed from command interface to main controller into JSON objects based on predefined serial interfacing schemas set up on the board firmware and to extract information from JSON strings.
    """

    def create_payload(self, command: str) -> str:
        """
        Parses a command string and returns a JSON string of the payload.
        """
        components = command.strip().split()
        if not components:
            logger.error('Empty command string received.')
            return json.dumps({})

        cmd_type = components[0].lower()
        payload = {}

        try:
            if cmd_type == 'export_topology':
                payload = {'cmd': 'capture-topology'}
            elif cmd_type == 'get_topology':
                payload = {'cmd': 'topology'}
            elif cmd_type == 'ping_node' and len(components) == 4:
                payload = {
                    'cmd': 'ping',
                    'to_node_id': components[1],
                    'HEX': components[2],
                    'msg': components[3]
                }
############ ...something here?
            else:
                logger.error('Invalid command or incorrect parameters.')
                return json.dumps({})

            result = {
                'payload_type': 'cmd',
                'payload': payload
            }
            return json.dumps(result)
        except Exception as e:
            logger.exception('Error processing command.')
            return json.dumps({})

    def extract_from_payload(self, json_str: str) -> str:
        """
        Extracts relevant information from a JSON string. Returns the input string if it cannot be parsed.
        """
        try:
            data = json.loads(json_str)
            payload = data.get('payload', {})
            if 'response' in payload:
                if payload['cmd'] == 'capture-topology':
                    self.export_to_jsonfile(TOPOLOGY_FILE, payload['response'], append=False)
                return json.dumps(payload['response'], indent=2)
            elif data.get('payload_type') == 'mesh':
                payload['msg'] = self.decrypt(payload['msg'])
                return json.dumps(payload, indent=2)
            return json.dumps(payload, indent=2)
        except json.JSONDecodeError:
            # logger.warning('Malformed JSON received, returning original.')
            return json_str
        except Exception as e:
            logger.exception('Unhandled exception during JSON extraction.')
            return json_str

    def export_to_jsonfile(self, filename: str, contents: dict, append: bool = False) -> None:
        mode = 'a' if append else 'w'
        with open(filename, mode) as ofile:
            json.dump(contents, ofile, indent=4)
            ofile.write('\n')

    def decrypt(self, message: str) -> str:
        return decrypt(message)

# This allows the script to be run for testing purposes
if __name__ == '__main__':
    parser = CommandParser()
    cmd = 'ping_node 87654321 #fafafa Thisisatestmessage'
    json_payload = parser.create_payload(cmd)
    print(json_payload)

    json_response = '{"payload_type": "cmd", "payload": {"cmd": "topology", "response": {"detail": "Network Topology"}}}'
    extracted = parser.extract_from_payload(json_response)
    print(extracted)


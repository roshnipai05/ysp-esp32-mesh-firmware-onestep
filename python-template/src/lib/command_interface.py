import os
import random
import re
import signal
import socket
import sys

from Config import EXIT_COMMAND, SOCK_HOST, SOCK_PORT, WORDLIST_FILE, log
from DeviceList import AllowedDevicesNodeIDs
from Logger import pprint

from workspace import encrypt

device_list = dict()
wordlist = list()
payload = ''
encrypted_payload = ''

def trigger_exit():
    os.kill(os.getpid(), signal.SIGINT)

def signal_handler(sig, frame):
    print('\n')
    log.info('Initiating interface shutdown...')

    # init server exit before shutting down
    send_data(EXIT_COMMAND)
    sys.exit(0)

def check_server_availability(host=SOCK_HOST, port=SOCK_PORT):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((host, port))
            s.close()
        return True
    except socket.error:
        return False

def send_data(data, host=SOCK_HOST, port=SOCK_PORT):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(data.encode())
    except ConnectionError as e:
        log.error(f'Connection failed: {e}')

def colour_validator(colour):
    # IMP: `colour` should be all lowercase
    return colour == 'false' or re.match(r'^#[0-9a-fA-F]{6}$', colour) is not None

def base_string_validator(input_string):
    return input_string.lower().strip()

def topology_cmd_handler(args):
    try:
        if len(args) != 0:
            raise ValueError('Incorrect use of `get_topology` command')
        send_data('topology')
    except ValueError as e:
        log.warning(e)
        log.info('Usage: `get_topology`')

def ping_cmd_handler(args):
    try:
        if len(args) != 2:
            raise ValueError('Incorrect use of `ping_node` command')

        hw_index, colour = args

        if not hw_index.isdigit() or int(hw_index) not in device_list:
            raise ValueError('[hw index] needs to be the number on your development board')
        if not colour_validator(colour):
            raise ValueError('[color hex] needs to be a hex value (like `#ff0000`) or the word `false`')
        else:
            # generate message and send
            global payload, encrypted_payload

            payload = ''.join(random.sample(wordlist, 5))
            encrypted_payload = encrypt(payload)

            # replace HWIndex with nodeID
            send_data(f'ping {device_list[int(hw_index)]} {colour} {encrypted_payload}')
    except ValueError as e:
        log.warning(e)
        log.info('Usage: `ping_node [hw index] [color hex OR \'false\']`')

def payload_cmd_handler(args):
    try:
        if len(args) != 0:
            raise ValueError('Incorrect use of `print_payload` command')

        print('Payload used for the previous `ping_node` command\nNote: Encrypted payload is sent to the pinged node\n')
        print(f'Unencrypted payload: {payload}')
        print(f'Encrypted payload: {encrypted_payload}')
    except ValueError as e:
        log.warning(e)
        log.info('Usage: `print_payload`')

def nodeid_cmd_handler(args):
    try:
        if len(args) != 0:
            raise ValueError('Incorrect use of `print_my_nodeid` command')

        print("Your development board's Node ID will be printed on the Serial Monitor now")
        send_data('mirror-mirror')
    except ValueError as e:
        log.warning(e)
        log.info('Usage: `print_my_nodeid`')

def export_topology_cmd_handler(args):
    try:
        if len(args) != 0:
            raise ValueError('Incorrect use of `export_topology_cmd_handler` command')

        print('Current topology will be saved to `src/topology.json`')
        send_data('capture-topology')
    except ValueError as e:
        log.warning(e)
        log.info('Usage: `export_topology_cmd_handler`')

def help_cmd_handler(args):
    print('Available Commands:')
    print('  get_topology           - Retrieve network topology')
    print('  ping_node [hw index] [color hex OR `false`] - Send a ping to a node with optional color')
    print('  print_my_nodeid        - Display the node ID of the development board connected to your device')
    print('  print_payload          - Print the encrypted and plaintext payload sent in the previous `ping_node`')
    print('  export_topology        - Retrieve and save the current network topology to a JSON file `src/topology.json`')
    print('  help                   - Display this help message')
    print('  exit                   - Exit the command interface')

command_handlers = {
    'get_topology': topology_cmd_handler,
    'ping_node': ping_cmd_handler,
    'print_my_nodeid': nodeid_cmd_handler,
    'print_payload': payload_cmd_handler,
    'export_topology': export_topology_cmd_handler,
    'help': help_cmd_handler
}

def usr_input_handler(input_string):
    # IMP: `input_string` should be lowercase

    parts = input_string.split()
    cmd = parts[0]
    args = parts[1:]

    if cmd in command_handlers:
        command_handlers[cmd](args)
    else:
        command_handlers['help'](args)

def main():
    host = SOCK_HOST
    port = SOCK_PORT

    # Register signal handlers
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame))

    if not check_server_availability(host, port):
        log.error('Server must be running before client starts.')
        log.info('Run `python server.py` in a different terminal before running this script.')
        sys.exit(1)

    log.info('Command Interface initiated. Press CTRL+C or type "exit" to exit.')
    try:
        # Initialise device list
        # AllowedDevicesNodeIDs key-value pair is (nodeID, HWIndex).
        # We need the reverse since `ping_node` takes HWIndex
        global device_list
        device_list = {v: k for k, v in AllowedDevicesNodeIDs.items()}

        # Read the wordfile and load words into a list
        with open(WORDLIST_FILE, 'r') as file:
            global wordlist
            wordlist = file.read().split()

        while True:
            pprint('\nEnter a command\n> ', '')
            usr_input = base_string_validator(input())
            if usr_input == EXIT_COMMAND:
                trigger_exit()
                break
            usr_input_handler(usr_input)
    except FileNotFoundError:
        log.error('File `wordlist` not found in `src/lib/`')
    except Exception as e:
        log.error(f'Unexpected error: {e}')
    finally:
        log.info('Closing Command Interface')

if __name__ == '__main__':
    main()


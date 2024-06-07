import os
import re
import signal
import socket
import sys

from logger import get_logger, pprint

LIB_DIR = os.path.dirname( os.path.abspath(__file__) )
SRC_DIR = os.path.dirname(LIB_DIR)

if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from edit import encrypt

log = get_logger()
wordlist = list()

def trigger_exit():
    os.kill(os.getpid(), signal.SIGINT)

def signal_handler(sig, frame):
    print('\n')
    log.info('Initiating interface shutdown...')

    # init server exit before shutting down
    send_data('exit')
    sys.exit(0)

def check_server_availability(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((host, port))
            s.close()
        return True
    except socket.error as e:
        # log.error(f"Server not available: {e}")
        return False

def send_data(data, host='127.0.0.1', port=65432):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(data.encode())
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")

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

        # TODO: check with device list and print helpful error messages
        # replace hw_index with corresponding node_id
        if not hw_index.isdigit():
            raise ValueError('[hw index] needs to be the number on your development board')
        if not colour_validator(colour):
            raise ValueError('[color hex] needs to be a hex value (like `#ff0000`) or the word `false`')
        else:
            print(f"ping {hw_index} {colour}")
    except ValueError as e:
        log.warning(e)
        log.info('Usage: `ping_node [hw index] [color hex OR \'false\']`')


def help_cmd_handler(args):
    print('Available Commands:')
    print('  get_topology           - Retrieve network topology')
    print('  ping_node [hw index] [color hex OR `false`] - Send a ping to a node with optional color')
    print('  help                   - Display this help message')
    print('  exit                   - Exit the command interface')

command_handlers = {
    'get_topology': topology_cmd_handler,
    'ping_node': ping_cmd_handler,
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
    host = '127.0.0.1'
    port = 65432

    # Register signal handlers
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame))

    if not check_server_availability(host, port):
        log.error('Server must be running before client starts.')
        log.info('Run `python server.py` in a different terminal before running this script.')
        sys.exit(1)

    log.info('Command Interface initiated. Press CTRL+C or type "exit" to exit.')
    try:
        # Read the wordfile and load words into a list
        wordlist_filepath = os.path.join(LIB_DIR, 'wordlist')
        with open(wordlist_filepath, 'r') as file:
            global wordlist
            wordlist = file.read().split()

        while True:
            pprint('\nEnter a command\n> ', '')
            usr_input = base_string_validator(input())
            if usr_input == 'exit':
                trigger_exit()
                break
            usr_input_handler(usr_input)
    except FileNotFoundError:
        log.error('File `wordlist` not found in `src/lib/`')
    finally:
        log.info('Closing Command Interface')

if __name__ == '__main__':
    main()


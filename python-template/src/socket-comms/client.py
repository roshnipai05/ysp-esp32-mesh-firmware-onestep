import os
import re
import signal
import socket
import sys

def trigger_exit():
    os.kill(os.getpid(), signal.SIGINT)

def signal_handler(sig, frame):
    print('\nInitiating interface shutdown...')

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
        # print(f"Server not available: {e}")
        return False

def send_data(data, host='127.0.0.1', port=65432):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(data.encode())
    except ConnectionError as e:
        print(f"Connection failed: {e}")

def colour_validator(colour):
    # IMP: `colour` should be all lowercase
    return colour == 'false' or re.match(r'^#[0-9a-fA-F]{6}$', colour) is not None

def base_string_validator(input_string):
    return input_string.lower().strip()

def topology_cmd_handler():
    pass

def ping_cmd_handler():
    pass

def help_cmd_handler():
    pass

command_handlers = {
    'get_topology': topology_cmd_handler,
    'ping_node': ping_cmd_handler,
    'help': help_cmd_handler
}

def usr_input_handler(input_string):
    # TODO: sanitise input before processing
    send_data(input_string)

def main():
    host = '127.0.0.1'
    port = 65432

    # Register signal handlers
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame))

    if not check_server_availability(host, port):
        print('Server must be running before client starts.')
        print('Run `python server.py` in a different terminal before running this script.')
        sys.exit(1)

    print('Command Interface initiated. Press CTRL+C or type "exit" to exit.')
    try:
        while True:
            usr_input = base_string_validator(input('\nEnter a command\n> '))
            if usr_input == 'exit':
                trigger_exit()
                break
            usr_input_handler(usr_input)
    finally:
        print('Closing command interface')

if __name__ == '__main__':
    main()


import os
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

def check_server(host, port):
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
        print(f"Failed to connect or send data: {e}")

def main():
    host = '127.0.0.1'
    port = 65432

    # Register signal handlers
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame))

    if not check_server(host, port):
        print('Server must be running before client starts.')
        print('Run `python server.py` in a different terminal before running this script.')
        sys.exit(1)

    print('Command Interface initiated. Press CTRL+C or type "exit" to exit.')
    try:
        while True:
            data = input('\nEnter a command\n> ')
            if data.lower() == 'exit':
                trigger_exit()
                break
            send_data(data)
    finally:
        print('Closing command interface')

if __name__ == '__main__':
    main()


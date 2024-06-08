import json
import os
import queue
import socket
import threading
import time
import serial
import signal
import sys

from logger import get_logger
from serialController import ESPController, HWNode

LIB_DIR = os.path.dirname( os.path.abspath(__file__) )
SRC_DIR = os.path.dirname(LIB_DIR)

if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

EXIT_COMMAND = 'exit'
TOPOLOGY_FILE = os.path.join(SRC_DIR, 'topology.json')

log = get_logger()
# serial_port = '/dev/cu.usbmodem1301'
# baud_rate = 115200
# ser = serial.Serial(serial_port, baud_rate)

def trigger_exit():
    # invoke SIGINT when user enters 'exit'. Signal handler will take care of cleanup.
    os.kill(os.getpid(), signal.SIGINT)

def self_identifier(id):
    print(f"[server] My Node ID: {id}")

def process_line(line, file):
    try:
        json_data = json.loads(line.strip())
        json.dump(json_data, file, indent=4)
        file.write('\n')
        return True
    except json.JSONDecodeError:
        # continue with the callee loop if json is not valid
        return False

def topology_export_handler(controller, cmd):
    controller.push(cmd)
    time.sleep(0.5)
    serial_buff = controller.pull()
    print(f"[export] Ready for export: {serial_buff}")

    try:
        with open(TOPOLOGY_FILE, 'w') as ofile:
            for line in serial_buff.split('\n'):
                if process_line(line, ofile):
                    break   # exit loop after json file is populated successfully
    except Exception as e:
        print(f"Unexpected Error: {e}")

def serial_interface(node: ESPController, cmd_queue: queue.Queue, shutdown_event: threading.Event):
    # IMP: *only* reads from Queue
    try:
        # if signal handler requested a shutdown, break out of loop
        while not shutdown_event.is_set():
            # if ser.in_waiting > 0:
            #     read_data = ser.read(ser.in_waiting).decode('utf-8')
            read_data = node.pull()
            if read_data:
                print(f"[serial] Received:\n{read_data}")
            if cmd_queue.qsize() > 0:
                cmd_str = cmd_queue.get()

                # connected board's nodeID, no serial call
                if cmd_str == 'mirror-mirror':
                    self_identifier(node.nodeID)

                # update current network topology json dump
                if cmd_str == 'capture-topology':
                    topology_export_handler(node, cmd_str)
                node.push(cmd_str)
                # cmd_str += '\n'
                # ser.write(cmd_str.encode('utf-8'))
            time.sleep(0.5)
    except serial.SerialException as e:
        print(f"[serial] Serial error: {e}")
    finally:
        print('[serial] Closing serial monitor')
        node.disconnectESP()
        # ser.close()


def client_handler(conn, addr, cmd_queue):
    # IMP: *only* writes to Queue
    # TODO: add logger w/ levels set using config.py
    # print(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            # only parse to check for exit command to start exit immediately
            if data.decode() == EXIT_COMMAND:
                trigger_exit()
                break

            print(f"[server] Sending command: {data.decode()}")
            cmd_queue.put(data.decode())
    except ConnectionResetError:
        print(f"[server] Connection reset by {addr}")
    finally:
        conn.close()

def init_server(signal_handler, input_queue):
    # TODO: set in config.py
    host = '127.0.0.1'
    port = 65432
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"[server] Server started on {host}:{port}")

    # Register signal handlers
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(server_socket, sig, frame))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(server_socket, sig, frame))

    try:
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=client_handler, args=(conn, addr, input_queue))
            client_thread.daemon = True    # background daemon, easy exit handling
            client_thread.start()
    finally:
        print('[server] Closing server')
        server_socket.close()

def main():
    global HWNode

    if not HWNode.controller:
        log.error('[housekeeping] No development board detected on your device')
        log.info('Check if your board is connected and the red on-board light is on')
        sys.exit(1)

    # client commands queue
    # IMP: there are no locks. Make sure we are dealing with only one Queue.
    client_cmd_queue = queue.Queue()

    # event channel to signal shutdown across threads safely
    shutdown_event = threading.Event()

    serial_thread = threading.Thread(target=serial_interface, args=(HWNode, client_cmd_queue, shutdown_event))
    serial_thread.start()

    def signal_handler(server, sig, frame):
        print('\n[housekeeping] Initiating shutdown...')
        shutdown_event.set()

        # wait for serial monitor to exit once `shutdown_event` is set
        serial_thread.join()
        # serial and server threads will free their objects on exit
        sys.exit(0)

    init_server(signal_handler, client_cmd_queue)

if __name__ == '__main__':
    main()


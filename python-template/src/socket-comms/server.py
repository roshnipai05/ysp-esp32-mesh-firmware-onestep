import queue
import socket
import threading
import time
import serial
import signal
import sys

serial_port = '/dev/cu.usbmodem1301'

EXIT_COMMAND = 'exit'

baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate)

def serial_interface(cmd_queue: queue.Queue):
    # BUG: currently closing port inside the loop. Errors out on sigint
    # IMP: *only* reads from Queue
    try:
        while True:
            if ser.in_waiting > 0:
                read_data = ser.read(ser.in_waiting).decode('utf-8')
                print("[ser] Received:", read_data)
            if cmd_queue.qsize() > 0:
                cmd_str = cmd_queue.get()

                if cmd_str == EXIT_COMMAND:
                    print('[ser] Exiting serial monitor')
                    break
                cmd_str += '\n'
                ser.write(cmd_str.encode('utf-8'))

            # hacky, unsure why. Taken from: ElectricRCAircraftGuy/eRCaGuy_PyTerm `serial_terminal.py`
            time.sleep(0.01)
        print('[ser] End')
        # TODO: use a shutdown global Event() to terminate from signal handler
    except serial.SerialException as e:
        print(f"[ser] Serial error: {e}")

def client_handler(conn, addr, cmd_queue):
    # IMP: *only* writes to Queue
    # TODO: add logger w/ levels set using config.py
    # print(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
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
        server_socket.close()

def main():
    # client commands queue
    # IMP: there are no locks. Make sure we are dealing with only one Queue.
    client_cmd_queue = queue.Queue()

    serial_thread = threading.Thread(target=serial_interface, args=(client_cmd_queue,))
    serial_thread.start()

    def signal_handler(server, sig, frame):
        print('\nShutting down...')
        ser.close()
        server.close()
        sys.exit(0)

    init_server(signal_handler, client_cmd_queue)

    # wait for serial monitor to finish reading after server quits
    serial_thread.join()
if __name__ == '__main__':
    main()


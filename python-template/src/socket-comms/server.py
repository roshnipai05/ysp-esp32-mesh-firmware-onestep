import queue
import socket
import threading
import time
import serial
import signal
import sys

serial_port = '/dev/cu.usbmodem11301'

EXIT_COMMAND = 'exit'

baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate)

def serial_interface(cmd_queue: queue.Queue, shutdown_event: threading.Event):
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
                    # TODO: does this close ser properly? is signal invoked?
                    break
                cmd_str += '\n'
                ser.write(cmd_str.encode('utf-8'))
            # if signal handler requested a shutdown, break out of loop
            if shutdown_event.is_set():
                break

            # hacky, unsure why. Taken from: ElectricRCAircraftGuy/eRCaGuy_PyTerm `serial_terminal.py`
            time.sleep(0.01)
        print('[ser] End')
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

    # event channel to signal shutdown across threads safely
    shutdown_event = threading.Event()

    serial_thread = threading.Thread(target=serial_interface, args=(client_cmd_queue, shutdown_event))
    serial_thread.start()

    def signal_handler(server, sig, frame):
        print('\nShutting down...')
        shutdown_event.set()
        # wait for serial monitor to exit once `shutdown_event` is set
        serial_thread.join()

        # free serial object and shut down socket server before exit
        ser.close()
        server.close()
        sys.exit(0)

    init_server(signal_handler, client_cmd_queue)

if __name__ == '__main__':
    main()


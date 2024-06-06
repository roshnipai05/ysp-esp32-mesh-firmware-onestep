import socket
import threading
import signal
import sys

def client_handler(conn, addr):
    # TODO: add logger w/ levels set using config.py
    # print(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode()}")
    except ConnectionResetError:
        print(f"Connection reset by {addr}")
    finally:
        conn.close()

def init_server():
    # TODO: set in config.py
    host = '127.0.0.1'
    port = 65432
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server started on {host}:{port}")

    def signal_handler(sig, frame):
        print('\nShutting down server...')
        server_socket.close()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame))

    try:
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=client_handler, args=(conn, addr))
            thread.daemon = True    # background daemon, easy exit handling
            thread.start()
    finally:
        server_socket.close()

if __name__ == '__main__':
    init_server()


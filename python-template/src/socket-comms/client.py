import socket

def send_data(data):
    host = '127.0.0.1'
    port = 65432
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(data.encode())
            print("Data sent")
    except ConnectionError as e:
        print(f"Failed to connect or send datea: {e}")

def main():
    while True:
        try:
            data = input("Enter data to send: ")
            send_data(data)
        except KeyboardInterrupt:
            print('\nClient interrupted by user')
            break

if __name__ == '__main__':
    main()


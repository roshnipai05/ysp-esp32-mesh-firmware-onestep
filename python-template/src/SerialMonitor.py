import serial
import time
import threading

def receive_messages(ser):
    while True:
        if ser.in_waiting > 0:
            message = ser.readline().decode('utf-8').strip()
            print(f"{message}")


serial_port = 'COM17'  # Change this to your serial port
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate)

# Start the receive_messages thread
receive_thread = threading.Thread(target=receive_messages, args=(ser,))
receive_thread.start()

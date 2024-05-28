import serial
import time
import threading
from edit import encrypt, decrypt
import json
import edit

serial_port = edit.serial_port  # Change this to your serial port
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate)


def receive_messages(ser):
    while True:
        if ser.in_waiting > 0:
            serial_lines = ser.readline().decode('utf-8').strip().split("\n")
            for line in serial_lines:
                if line.startswith("Received"):
                    # Remove "Received " from the message
                    json_obj_dump = line.replace("Received ", "")
                    print(f"Received message: {json_obj_dump}")

                    try:
                        json_message = json.loads(json_obj_dump)
                        if 'msg' in json_message:
                            decrypted_message = decrypt(json_message['msg'])
                            print(f"Decrypted message: {decrypted_message}")
                        else:
                            print(f"DEBUG, This is light up instr: {json_message}")
                    except json.JSONDecodeError as e:
                        print(f"err is {e}")
                else:
                    print(f" \n")



# Start the receive_messages thread
receive_thread = threading.Thread(target=receive_messages, args=(ser,))
receive_thread.start()

import serial
import sys
import signal
from edit import decrypt
import json
import edit

def signal_handler(ser, sig, frame):
    print("Signal received, stopping...")
    ser.close()
    sys.exit(0)

def receive_messages(ser):
    # Register signal handlers
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(ser, sig, frame))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(ser, sig, frame))

    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("Received"):
                # Split at received. 0th index is empty, 1st index is the message. 2nd index is light up instruction. Ignore.
                message_payload = line.split("Received ")[1]
                try:
                    json_message = json.loads(message_payload)
                    if 'msg' in json_message:
                        decrypted_message = decrypt(json_message['msg'])
                        print(f"Decrypted message: {decrypted_message}")
                    #else:
                        # Control flow should never reach here
                        # print(f"DEBUG, This is light up instr: {json_message}")
                except json.JSONDecodeError as e:
                    print(f"{e}")
            else:
                print(f"{line}")

if __name__ == "__main__":
    serial_port = edit.serial_port  # Change this to your serial port
    baud_rate = 115200
    ser = serial.Serial(serial_port, baud_rate)
    receive_messages(ser)

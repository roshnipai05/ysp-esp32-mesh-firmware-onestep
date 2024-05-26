import serial
import time
import threading
import random
import re
from edit import caesar_cipher_encrypt, caesar_cipher_decrypt
# Set up the serial connection
serial_port = 'COM21'  # Change this to your serial port
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate)


# Function to generate a random 16-character alphanumeric key
def generate_random_key():
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    key = ''.join(random.choice(characters) for _ in range(16))
    return key

# Function to handle receiving messages
def receive_messages(ser):
    while True:
        if ser.in_waiting > 0:
            message = ser.readline().decode('utf-8').strip()
            print(f"Received message: {message}")

def handle_send_message(command):
    match = re.match(r'Send (\d+) (\w+)$', command)
    if not match:
        print("Usage: Send TargetNode HexColorID ")
    else: # 
        node_id = match.group(1)
        hex_color = match.group(2)
        full_message = f"Send {node_id} {hex_color} {key} "

        ser.write((full_message + '\n').encode('utf-8'))
        print(f"Sent encrypted message to node {node_id} with color {hex_color}")
        time.sleep(1) 
        while ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            print(response)


def handle_show_message(command):
    match = re.match(r'Show_Message ([01])$', command)
    if not match:
        print("Usage: Show_Message 0/1")
    else:
        show_message_flag = int(match.group(1))
        if show_message_flag == 0:
            print(f"Unencrypted key: {key}")
        else:
            encrypted_key = caesar_cipher_encrypt(key)
            print(f"Encrypted key: {encrypted_key}")


def handle_list_nodes(command):
    ser.write("topology\n".encode('utf-8'))
    time.sleep(1) 
    while ser.in_waiting > 0:
        response = ser.readline().decode('utf-8').strip()
        print(response)

def handle_debug_mode(command):
    print("Entering Debug Mode. Type 'exit' to leave Debug Mode.")
    while True:
        debug_command = input("Debug> ")
        if debug_command.lower() == "exit":
            break
        ser.write((debug_command + '\n').encode('utf-8'))

def handle_list_colors(command):
    colors = {
        "Red": "0xFF0000",
        "Green": "0x00FF00",
        "Blue": "0x0000FF",
        "Yellow": "0xFFFF00",
        "Cyan": "0x00FFFF",
        "Magenta": "0xFF00FF",
        "White": "0xFFFFFF",
        "Black": "0x000000"
    }
    print("colors and their hex codes:")
    for color, code in colors.items():
        print(f"{color}: {code}")

def handle_unknown_command(command):
    print("Unknown command. Available commands: Send, ShowMessage, List_Nodes, List_Colors")

command_handlers = {
    "Send": handle_send_message,
    "ShowMessage": handle_show_message,
    "List_Nodes": handle_list_nodes,
    "DebugMode": handle_debug_mode,
    "List_Colors": handle_list_colors
}



# Main command-line interface
try:
    key = generate_random_key()
    while True:
        command = input("Enter command: ")
        command_name = command.split(maxsplit=1)[0]
        handler = command_handlers.get(command_name)
        if handler:
            handler(command)
        else:
            handle_unknown_command(command)
except KeyboardInterrupt:
    print("Program interrupted")
finally:
    ser.close()

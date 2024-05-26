import serial
import time
import threading
import random
import re

# Set up the serial connection
serial_port = 'COM17'  # Change this to your serial port
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate)


# Function to generate a random 16-character alphanumeric key
def generate_random_key():
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    key = ''.join(random.choice(characters) for _ in range(16))
    return key


# Function to encrypt the message using Caesar cipher
def caesar_cipher_encrypt(message):


    return message

# Function to decrypt the message using Caesar cipher
def caesar_cipher_decrypt(message):
    
    return message

# Function to handle receiving messages
def receive_messages(ser):
    while True:
        if ser.in_waiting > 0:
            message = ser.readline().decode('utf-8').strip()
            print(f"Received message: {message}")

def handle_send_message(command):
    match = re.match(r'Send_Message (\d+) (\w+)$', command)
    if not match:
        print("Usage: Send_Message NodeID HexColorID")
    else:
        node_id = match.group(1)
        hex_color = match.group(2)
        full_message = f"Send_Message {node_id} {key} {hex_color}"


        ser.write((full_message + '\n').encode('utf-8'))
        print(f"Sent encrypted message to node {node_id} with color {hex_color}")

def handle_broadcast_message(command):
    match = re.match(r'Broadcast_Message (\w+)$', command)
    if not match:
        print("Usage: Broadcast_Message HexColorID")
    else:
        hex_color = match.group(1)
        full_message = f"Broadcast_Message {key} {hex_color}"
        encrypted_message = caesar_cipher_encrypt(full_message)
        ser.write((encrypted_message + '\n').encode('utf-8'))
        print(f"Sent encrypted broadcast message with color {hex_color}")


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
        "Red": "#FF0000",
        "Green": "#00FF00",
        "Blue": "#0000FF",
        "Yellow": "#FFFF00",
        "Cyan": "#00FFFF",
        "Magenta": "#FF00FF",
        "White": "#FFFFFF",
        "Black": "#000000"
    }
    print("Available colors and their hex codes:")
    for color, code in colors.items():
        print(f"{color}: {code}")

def handle_unknown_command(command):
    print("Unknown command. Available commands: Send_Message, Broadcast_Message, ShowMessage, List_Nodes, DebugMode")

command_handlers = {
    "Send_Message": handle_send_message,
    "Broadcast_Message": handle_broadcast_message,
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

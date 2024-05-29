import random
import re
import serial
import signal
import sys
import time
import os

from edit import encrypt, serial_port

ROOT = os.path.dirname(        # src
        os.path.abspath(__file__)
    )

# Set up the serial connection

serial_port = serial_port  # Change this to your serial port

baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate)

def signal_handler(ser, sig, frame):
    print("\nSignal received, stopping...")
    ser.close()
    sys.exit(0)


# Function to generate a random 16-character alphanumeric key
def generate_random_string():
    # characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    # rand_string = ''.join(random.choice(characters) for _ in range(16))

    random_words = random.sample(wordlist, 4)
    rand_string = '-'.join(random_words)

    return f"Payload {rand_string}"

# Function to handle receiving messages
def receive_messages(ser):
    while True:
        if ser.in_waiting > 0:
            message = ser.readline().decode('utf-8').strip()
            print(f"Received message: {message}")

def handle_send_message(command):
    match = re.match(r'Send (\d+) (#(?:[0-9a-fA-F]{6})|false|False)$', command)
    if not match:
        print("Usage: Send TargetNode HexColorID \n Set HexColorID as false for No Lighting") #Send Target node Hexcolor Msg
    else: #
        node_id = match.group(1)
        hex_color = match.group(2)

        serial_command = f"Send {node_id} {hex_color} {encrypted_payload}"

        ser.write((serial_command + '\n').encode('utf-8'))

        print(f"Message Sent Successfully. To: {node_id} Color: {hex_color}")

        time.sleep(1)
        while ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            print(response)

def handle_show_message(command):
    match = re.match(r'Show_Message ([01])$', command)
    if not match:
        print("Usage: Show_Message 0/1 (0 for the Unencrypted payload, 1 for encrypted)")
    else:
        show_message_flag = int(match.group(1))
        if show_message_flag == 0:
            print(f"Unencrypted payload: {payload}")
        else:
            encrypted_payload = encrypt(payload)
            print(f"Encrypted payload: {encrypted_payload}")

def handle_list_nodes(command):
    ser.write("topology\n".encode('utf-8'))
    time.sleep(1)
    while ser.in_waiting > 0:
        response = ser.readline().decode('utf-8').strip()
        print(response)

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
    print("colors and their hex codes:")
    for color, code in colors.items():
        print(f"{color}: {code}")

def handle_debug_mode(command):
    print("Entering Debug Mode. Type 'exit' to leave Debug Mode.")
    while True:
        debug_command = input("Debug> ")
        if debug_command.lower() == "exit":
            break
        ser.write((debug_command + '\n').encode('utf-8'))

def handle_unknown_command(command):
    print("Unknown command. Available commands: Send, Show_Message, List_Nodes, List_Colors")

command_handlers = {
    "Send": handle_send_message,
    "Show_Message": handle_show_message,
    "List_Nodes": handle_list_nodes,
    "DebugMode": handle_debug_mode,
    "List_Colors": handle_list_colors
}

# Main command-line interface
if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(ser, sig, frame))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(ser, sig, frame))

    wordlist = []
    try:
        # Read the wordfile and load words into a list
        wordlist_filepath = os.path.join(ROOT, "wordlist")
        with open(wordlist_filepath, 'r') as file:
            wordlist = file.read().split()

        payload = generate_random_string()
        encrypted_payload = encrypt(payload)
        while True:
            command = input("Enter command: ")
            command_name = command.split(maxsplit=1)[0]
            handler = command_handlers.get(command_name)
            if handler:
                handler(command)
            else:
                handle_unknown_command(command)

    except FileNotFoundError:
        print("Error: 'wordlist' file not found")
    except ValueError:
        print("Error: The word list is too short to pick 4 unique words")

"""
Encryption Workspace - Instruction Guide for Red-Blue Team Activities

Welcome to your encryption workspace! This file is part of a simulated secure communications project where you will implement encryption and decryption logic to secure messages sent between devices on a mesh network.

Team Instructions:
- There are two teams: Blue and Red.
- Blue Team (Defenders): Consists of 5 nodes. Your task is to implement the encryption and decryption logic shared amongst your team to secure your messages.
- Red Team (Attackers): Consists of 5 nodes. Initially, write your own encrypt and decrypt functions. Then, your task is to intercept and attempt to decrypt messages from the Blue Team, understanding and possibly reverse-engineering their encryption methods.

Rules:
- Do not change the function signatures (the way the functions are defined and what parameters they take) of `encrypt` and `decrypt`.
- You may introduce new functions if needed, but remember that only `encrypt` and `decrypt` will be used by the rest of the codebase to handle messages.
- All your encryption and decryption logic should happen within these functions.
- Use the test function to try out your code before running `ping_node` on the Command Interface.
- Focus on learning and understanding cryptography basics rather than just efficiency.

Good luck, and let the simulation begin!
"""

# Global shift key for Caesar Cipher-like encryption
SHIFT_KEY = 3

def encrypt(message):
    """
    Encrypts a message using a shift cipher.
    Parameters:
        message (str): The plaintext message that needs to be encrypted.
    Returns:
        str: The encrypted message.
    """
    # This function should encrypt the message and return it.
    # Currently, it does nothing to the message; replace the return statement with your encryption logic.
    return message

def decrypt(message):
    """
    Decrypts a message using a shift cipher.
    Parameters:
        message (str): The encrypted message that needs to be decrypted.
    Returns:
        str: The decrypted message.
    """
    # This function should decrypt the message and return it.
    # Currently, it does nothing to the message; replace the return statement with your decryption logic.
    return message

def test():
    """
    A test function to check the implementation of the encrypt and decrypt functions.
    Use this to ensure your code is working as expected before it's integrated into the larger system.
    """
    original_message = "Hello, World! This is a test message."
    print("[test] Original Message:", original_message)

    encrypted_message = encrypt(original_message)
    print("[test] Encrypted Message:", encrypted_message)

    decrypted_message = decrypt(encrypted_message)
    print("[test] Decrypted Message:", decrypted_message)

if __name__ == "__main__":
    test()


# backend/api_key_management.py

import subprocess
import getpass
import os

def save_api_key(api_key_file):
    api_key = getpass.getpass("Enter your NGC API key, it will be ecrypted and stored.: ")
    print("Enter a password to encrypt your API key.")
    encrypted_key = subprocess.check_output(f"echo {api_key} | openssl enc -aes-256-cbc -pbkdf2 -a -salt", shell=True)
    with open(api_key_file, "wb") as f:
        f.write(encrypted_key)
    print("API key saved.")
    return api_key

def read_api_key(api_key_file):
    if not os.path.exists(api_key_file):
        print("API key file not found!")
        return save_api_key(api_key_file)
    else:
        print("Enter your password to decrypt your API key.")
        decrypted_key = subprocess.check_output(f"openssl enc -aes-256-cbc -pbkdf2 -d -a -in {api_key_file}", shell=True)
        return decrypted_key.decode().strip()


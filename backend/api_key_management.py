import subprocess
import getpass
import os

def save_api_key(api_key_file):
    api_key = getpass.getpass("Enter your NGC API key, it will be encrypted and stored: ")
    print("Enter a password to encrypt your API key.")
    # Using shell=True is a potential security risk; it's better to pass the command as a list to avoid shell injection.
    encrypted_key = subprocess.check_output(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-a", "-salt", "-pass", f"pass:{api_key}"], input=api_key.encode())
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
        # Using shell=True is a potential security risk; it's better to pass the command as a list to avoid shell injection.
        decrypted_key = subprocess.check_output(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-d", "-a", "-in", api_key_file])
        return decrypted_key.decode().strip()


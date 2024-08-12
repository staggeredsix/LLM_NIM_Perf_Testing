# backend/nim_management.py

import os

def add_nim(nim_file):
    nim_name = input("Enter the NIM name (e.g., mistral-7b-instruct): ").lower()
    img_name = input("Enter the Docker image name (e.g., nvcr.io/nim/mistralai/mistral-7b-instruct-v03:latest): ").lower()
    with open(nim_file, "a") as f:
        f.write(f"{nim_name}:{img_name}\n")
    print("NIM added.")

def list_nims(nim_file):
    print("Available NIMs:")
    if os.path.exists(nim_file):
        with open(nim_file, "r") as f:
            for i, line in enumerate(f, 1):
                print(f"{i} --- {line.strip()}")
    else:
        print("No NIMs found.")


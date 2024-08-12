# backend/install_tools.py

import subprocess
import os
def command_exists(command):
    return subprocess.call(f"type {command}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def install_tools():
    if not command_exists("openssl"):
        raise SystemExit("openssl could not be found, please install it.")
    if not command_exists("python3"):
        raise SystemExit("python3 could not be found, please install it.")

def check_python_version():
    python_version = f"{os.sys.version_info.major}.{os.sys.version_info.minor}"
    print(f"Detected Python version: {python_version}")
    return python_version

def install_pip():
    if not command_exists("pip3"):
        print("pip could not be found, installing it now.")
        subprocess.run("curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py", shell=True)
        subprocess.run("python3 get-pip.py", shell=True)
        os.remove("get-pip.py")
        if not command_exists("pip3"):
            raise SystemExit("pip installation failed.")

def check_ubuntu_version():
    is_ubuntu_24xx = False
    if command_exists("lsb_release"):
        ubuntu_version = subprocess.check_output("lsb_release -rs", shell=True).decode().strip()
        if ubuntu_version.startswith("24."):
            is_ubuntu_24xx = True
            print("Running on Ubuntu 24.xx. Will use --break-system-packages for pip installations.")
    return is_ubuntu_24xx

def install_python_packages(is_ubuntu_24xx):
    required_python_packages = ["pandas", "matplotlib", "requests"]
    for package in required_python_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Python package {package} is not installed. Installing...")
            install_command = f"pip3 install {package}"
            if is_ubuntu_24xx:
                install_command += " --break-system-packages"
            subprocess.run(install_command, shell=True, check=True)


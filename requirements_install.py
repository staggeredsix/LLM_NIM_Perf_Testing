import os
import subprocess
import sys

def run_command(command, error_message):
    """Runs a system command and handles errors."""
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError:
        print(f"Error: {error_message}")
        sys.exit(1)

def install_docker():
    print("Installing Docker CE...")
    run_command("sudo apt-get update", "Failed to update package lists")
    run_command("sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common", "Failed to install dependencies")
    run_command("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -", "Failed to add Docker GPG key")
    run_command("sudo add-apt-repository \"deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\"", "Failed to add Docker repository")
    run_command("sudo apt-get update", "Failed to update package lists after adding Docker repository")
    run_command("sudo apt-get install -y docker-ce", "Failed to install Docker CE")

def install_nvidia_toolkit():
    print("Installing NVIDIA Container Toolkit...")
    distribution_cmd = ". /etc/os-release; echo $ID$VERSION_ID"
    distribution = subprocess.getoutput(distribution_cmd)
    run_command("curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -", "Failed to add NVIDIA Docker GPG key")
    run_command(f"curl -s -L https://nvidia.github.io/nvidia-docker/{distribution}/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list", "Failed to add NVIDIA Docker repository")
    run_command("sudo apt-get update", "Failed to update package lists after adding NVIDIA repository")
    run_command("sudo apt-get install -y nvidia-container-toolkit", "Failed to install NVIDIA Container Toolkit")
    run_command("sudo systemctl restart docker", "Failed to restart Docker")

def install_ngc_cli():
    print("Installing NVIDIA NGC CLI...")
    run_command("wget -O ngccli_cat_linux.zip https://ngc.nvidia.com/downloads/ngccli_cat_linux.zip", "Failed to download NVIDIA NGC CLI")
    run_command("unzip ngccli_cat_linux.zip", "Failed to unzip NVIDIA NGC CLI")
    run_command("chmod u+x ngc", "Failed to make NGC CLI executable")

def install_python_packages():
    print("Installing Python packages...")
    run_command("pip install -r requirements.txt", "Failed to install Python packages from requirements.txt")

def check_python():
    """Check if Python 3 is installed and prompt to install it if not."""
    if not sys.version_info >= (3, 6):
        response = input("Python 3 is not installed. Do you want to install it? (y/n): ").strip().lower()
        if response == 'y':
            run_command("sudo apt-get install -y python3", "Failed to install Python 3")
        else:
            print("Python 3 is required to run this script.")
            sys.exit(1)

    # Check if pip3 is installed
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
    except subprocess.CalledProcessError:
        print("pip for Python 3 is not installed. Installing pip3...")
        run_command("sudo apt-get install -y python3-pip", "Failed to install pip3")

def add_user_to_docker_group():
    print("Adding current user to Docker group...")
    run_command("sudo usermod -aG docker $USER", "Failed to add user to Docker group")
    print("Please log out and back in for the Docker group changes to take effect.")

if __name__ == "__main__":
    check_python()
    install_docker()
    install_nvidia_toolkit()
    install_ngc_cli()
    install_python_packages()
    add_user_to_docker_group()

    print("All required software has been installed successfully.")

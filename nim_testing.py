import os
import subprocess
import logging
from backend.install_tools import install_tools, check_python_version, install_pip, check_ubuntu_version, install_python_packages
from backend.api_key_management import read_api_key
from backend.nim_management import add_nim, list_nims
from backend.performance_test import run_test

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def prune_docker_containers():
    confirm = input("Do you want to stop all running containers and prune them? If you choose no, the script may fail. (y/n): ").strip().lower()
    if confirm == 'y':
        logging.info("Stopping all running containers...")
        subprocess.run("docker stop $(docker ps -q)", shell=True)
        logging.info("Pruning all containers...")
        subprocess.run("docker container prune -f", shell=True)
        logging.info("All containers stopped and pruned.")

def kill_all_containers():
    confirm = input("Do you want to kill all running containers? (y/n): ").strip().lower()
    if confirm == 'y':
        logging.info("Killing all running containers...")
        subprocess.run("docker stop $(docker ps -q)", shell=True)
        logging.info("Purging all containers...")
        subprocess.run("docker rm $(docker ps -a -q)", shell=True)
        logging.info("All containers killed and purged.")

def menu():
    # Get the directory where nim_testing.py resides
    script_dir = os.path.dirname(os.path.abspath(__file__))

    nim_file = os.path.join(script_dir, "nim_list.txt")
    api_key_file = os.path.join(script_dir, "ngc_api_key.enc")  # Store API key in the same directory as nim_testing.py
    local_nim_cache = os.path.expanduser("~/.cache/nim")
    output_dir = os.path.join(script_dir, "performance_results")

    os.makedirs(local_nim_cache, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Prompt for the API key decryption
    print("Enter Password for API Key Decryption")
    api_key = read_api_key(api_key_file)

    # Set the API key as an environment variable
    os.environ["NGC_API_KEY"] = api_key

    options = ["Run tests against all NIMs", "Run test against a specific NIM", "Add a new NIM", "Quit"]
    while True:
        print("Select an option:")
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            gpus = int(input("Enter the number of GPUs to use: "))
            request_count = input("Enter the number of requests to send (press Enter to use default of 10): ")
            request_count = int(request_count) if request_count else 10

            if os.path.exists(nim_file):
                with open(nim_file, "r") as f:
                    for line in f:
                        model, img_name = line.strip().split("|", 1)
                        img_name = img_name.strip()  # Remove any leading/trailing whitespace
                        logging.info(f"Prepared Docker command for NIM: {model}")
                        logging.info(f"Docker image: {img_name.lower()}")
                        confirm_run = input(f"Proceed with running {model} using image {img_name.lower()}? (y/n): ").strip().lower()
                        if confirm_run == 'y':
                            run_test(img_name.lower(), gpus, os.environ["NGC_API_KEY"], local_nim_cache, output_dir, request_count)
                        else:
                            logging.info("User cancelled the operation.")
        elif choice == 2:
            list_nims(nim_file)
            nim_number = int(input("Enter the NIM number: "))
            gpus = int(input("Enter the number of GPUs to use: "))
            request_count = input("Enter the number of requests to send (press Enter to use default of 10): ")
            request_count = int(request_count) if request_count else 10

            with open(nim_file, "r") as f:
                model_img = f.readlines()[nim_number - 1].strip()
                model, img_name = model_img.split("|", 1)
                img_name = img_name.strip()  # Remove any leading/trailing whitespace
                logging.info(f"Prepared Docker command for NIM: {model}")
                logging.info(f"Docker image: {img_name.lower()}")
                confirm_run = input(f"Proceed with running {model} using image {img_name.lower()}? (y/n): ").strip().lower()
                if confirm_run == 'y':
                    run_test(img_name.lower(), gpus, os.environ["NGC_API_KEY"], local_nim_cache, output_dir, request_count)
                else:
                    logging.info("User cancelled the operation.")
        elif choice == 3:
            add_nim(nim_file)
        elif choice == 4:
            kill_all_containers()  # Prompt to kill all containers before quitting
            break
        else:
            logging.info("Invalid option.")

if __name__ == "__main__":
    install_tools()
    check_python_version()
    install_pip()
    is_ubuntu_24xx = check_ubuntu_version()
    install_python_packages(is_ubuntu_24xx)
    prune_docker_containers()
    menu()


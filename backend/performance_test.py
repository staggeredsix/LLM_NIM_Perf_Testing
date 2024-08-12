import time
import requests
import re
import threading
import subprocess
import logging
import os

# ANSI escape codes for flashing and color
FLASH = "\033[5m"
RED = "\033[31m"
RESET = "\033[0m"

def extract_model_from_logs(logs):
    model_pattern = r'"model":\s*"([^"]+)"'
    match = re.search(model_pattern, logs)
    if match:
        return match.group(1)
    else:
        raise ValueError("Model identifier not found in the logs.")

def monitor_logs(container_id, log_file):
    """Attaches to the container logs and monitors for tokens per second."""
    print(f"{FLASH}{RED}Attaching to container logs to monitor performance...{RESET}")
    log_process = subprocess.Popen(f"docker logs -f {container_id}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    for line in log_process.stdout:
        decoded_line = line.decode('utf-8').strip()
        log_file.write(decoded_line + "\n")  # Write log to the log file only
        
        if "tokens per second" in decoded_line.lower():
            tokens_per_sec = float(decoded_line.split()[-2])  # Assume the metric is before 'tokens per second'
            print(f"{RED}Container reported {tokens_per_sec} tokens per second.{RESET}")
            log_file.write(f"Container-reported tokens per second: {tokens_per_sec}\n")

    log_process.terminate()

def make_single_request(model_name, log_file, total_start_time):
    try:
        # Start the timer before making the request
        request_send_time = time.time_ns()
        
        response = requests.post(
            "http://0.0.0.0:8000/v1/chat/completions",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": "Tell me a story that is 500 words long and about cheeseburgers."}],
                "top_p": 1,
                "n": 1,
                "max_tokens": 1024,
                "stream": False,
                "frequency_penalty": 1.0
            }
        )
        
        # Measure when the response is fully received
        end_time = time.time_ns()

        if response.status_code == 200:
            total_tokens_in_response = sum(len(choice['message']['content'].split()) for choice in response.json().get("choices", []))
            total_time = (end_time - request_send_time) / 1e9  # Convert nanoseconds to seconds

            # Calculate tokens per second
            tokens_per_second = total_tokens_in_response / total_time

            # Log to file
            log_file.write(f"Total Time for This Request: {total_time:.6f} seconds\n")
            log_file.write(f"Tokens per Second: {tokens_per_second:.6f}\n")
            log_file.write(f"Total Tokens: {total_tokens_in_response}\n\n")

            # Print live feedback to the user
            print(f"Request completed: {total_tokens_in_response} tokens generated in {total_time:.6f} seconds ({tokens_per_second:.6f} tokens/second)")
        else:
            log_file.write(f"Error: Received unexpected status code {response.status_code}\n")
            log_file.write(response.text + "\n\n")
            print(f"Error: Received unexpected status code {response.status_code}")
    except Exception as e:
        log_file.write(f"Error during request: {e}\n\n")
        print(f"Error during request: {e}")

def run_test(img_name, gpus, api_key, local_nim_cache, output_dir, request_count=10):
    # Use the environment variable directly in the command
    run_command = (
        f"docker run --rm --gpus {gpus} --shm-size=16GB "
        f"-e NGC_API_KEY={os.environ['NGC_API_KEY']} -v {local_nim_cache}:/opt/nim/.cache "
        f"-u {os.getuid()}:{os.getgid()} -p 8000:8000 {img_name}"
    )
    
    container_process = subprocess.Popen(run_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

    nim_logs = []
    model_name = None
    uvicorn_running = False

    print(f"{FLASH}{RED}Attaching to container logs to identify model and confirm server start...{RESET}")
    for line in iter(container_process.stdout.readline, b''):
        decoded_line = line.decode('utf-8').strip()
        nim_logs.append(decoded_line)
        print(decoded_line)  # Keep printing this for user feedback

        if "Uvicorn running on" in decoded_line:
            uvicorn_running = True
            break

        if model_name is None:
            try:
                model_name = extract_model_from_logs(decoded_line)
            except ValueError:
                continue

    if not uvicorn_running:
        print("Error: Server did not start. Exiting...")
        container_process.terminate()
        return

    print(f"Model identified: {model_name}")
    print(f"{FLASH}{RED}Uvicorn is running. Detaching from the container and waiting 15 seconds for the server to warm up...{RESET}")

    time.sleep(15)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Extract the last segment of the model name for directory creation
    model_dir_name = model_name.split("/")[-1]

    # Ensure the specific model directory exists
    model_dir = os.path.join(output_dir, model_dir_name)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    timestamp = time.strftime("%d%b%y_%H%M%S")
    log_filename = os.path.join(model_dir, f"{model_dir_name}_performance_{timestamp}.txt")

    with open(log_filename, "w") as log_file:
        log_file.write(f"Performance Test for Model: {model_name}\n")
        log_file.write(f"Number of Requests: {request_count}\n\n")

        # Start log monitoring thread
        log_thread = threading.Thread(target=monitor_logs, args=(container_process.pid, log_file))
        log_thread.start()

        # Sequential Requests
        log_file.write("Sequential Requests:\n")
        total_start_time = time.time_ns()  # Start the overall timer
        for i in range(request_count):
            print(f"Sequential Request {i + 1}/{request_count}")
            make_single_request(model_name, log_file, total_start_time)

        # Concurrent Requests
        print(f"\n{FLASH}{RED}Starting Concurrent Requests with {request_count} threads...{RESET}")
        log_file.write("\nConcurrent Requests:\n")
        threads = []
        total_start_time = time.time_ns()  # Restart the overall timer for concurrent requests
        for i in range(request_count):
            print(f"Starting thread {i + 1}/{request_count} for concurrent request...")
            thread = threading.Thread(target=make_single_request, args=(model_name, log_file, total_start_time))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print(f"{FLASH}{RED}Concurrent requests completed.{RESET}")

        # Wait for log monitoring to finish
        log_thread.join()

    print(f"Performance test completed. Logs saved to {log_filename}")

    container_process.terminate()
    print("Test completed, and container has been terminated.")

    # Cleanup all containers and prune them
    cleanup_containers()

def cleanup_containers():
    # Stop all running containers
    subprocess.run("docker stop $(docker ps -q)", shell=True)
    # Remove all containers
    subprocess.run("docker rm $(docker ps -a -q)", shell=True)
    # Prune all containers
    subprocess.run("docker container prune -f", shell=True)

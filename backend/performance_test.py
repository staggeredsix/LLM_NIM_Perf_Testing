import time
import subprocess
import os
from backend.tests.extract_model import extract_model_from_logs
from backend.tests.monitor_logs import monitor_logs
from backend.tests.run_test_phase1 import run_test_phase1
from backend.tests.run_test_phase2 import run_test_phase2
from backend.tests.run_stress_test import run_stress_test_phase
from backend.tests.run_multiprocess_test import run_multiprocess_test
from backend.tests.utils.cleanup_containers import cleanup_containers

def run_test(img_name, gpus, api_key, local_nim_cache, output_dir, request_count=10, max_processes=8):
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

    print("Attaching to container logs to identify model and confirm server start...")
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
    print("Uvicorn is running. Detaching from the container and waiting 15 seconds for the server to warm up...")

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

        # Sequential Test Phase 1 - Stream = False
        run_test_phase1(model_name, request_count, log_file)

        # Concurrent Test Phase 1 - Stream = False
        run_multiprocess_test(model_name, "http://0.0.0.0:8000/v1/chat/completions", request_count, log_file, stream=False, max_processes=max_processes)

        # Sequential Test Phase 2 - Stream = True
        run_test_phase2(model_name, log_file, request_count, is_concurrent=False)  # Removed max_processes argument

        # Ask user if they want to run the stress test
        run_stress_test = input("Do you want to run a stress test to see how many concurrent requests your system can handle? This will test until the model is outputting 10 tokens per second. It may KILL your GPU because of the amount of load. Do this only if you are okay with murdering hardware. (y/n): ").strip().lower()
        if run_stress_test == 'y':
            run_stress_test_phase(model_name, log_file, request_count, max_processes, log_filename)

    print(f"Performance test completed. Logs saved to {log_filename}")

    container_process.terminate()
    print("Test completed, and container has been terminated.")

    # Cleanup all containers and prune them
    cleanup_containers()


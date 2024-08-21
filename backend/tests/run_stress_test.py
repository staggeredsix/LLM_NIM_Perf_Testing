import multiprocessing
import time
import os
import subprocess
import re
from backend.tests.make_single_request import make_single_request
from backend.tests.utils.cleanup_containers import cleanup_containers

def run_stress_test_phase(model_name, log_file, request_count, max_processes=8):
    """Runs the concurrent stress test, scaling up the number of threads until the model drops below a certain TPS threshold."""

    print(f"\nStarting Concurrent Stress Test...")
    stress_level = 1
    tokens_per_second_threshold = 10

    try:
        while True:
            print(f"\nStarting stress level {stress_level} with {request_count * stress_level} processes...")

            # Run the requests using multiprocessing
            run_multiprocess_test(model_name, request_count * stress_level, log_file, stream=True, max_processes=max_processes)

            # Check the average TPS from the logs
            log_file.seek(0)  # Move the file pointer to the beginning
            logs = log_file.read()
            tps_matches = re.findall(r"Tokens per Second: (\d+\.\d+)", logs)
            if tps_matches:
                avg_tps = sum(float(tps) for tps in tps_matches) / len(tps_matches)
                print(f"Average Tokens per Second: {avg_tps:.6f}")
                if avg_tps < tokens_per_second_threshold:
                    print(f"TPS dropped below {tokens_per_second_threshold} tokens/second. Stopping stress test.")
                    break

            stress_level += 1
    except KeyboardInterrupt:
        print(f"\nStress test interrupted by user. Exiting gracefully...")
    finally:
        # Cleanup all containers and prune them
        cleanup_containers()
        print(f"Concurrent Stress Test completed.")

def run_multiprocess_test(model_name, request_count, log_file, stream=False, max_processes=8):
    """Handles the multiprocessing of requests for the stress test."""
    token_timestamps = multiprocessing.Manager().list()
    processes = []
    core_count = os.cpu_count()

    for i in range(request_count):
        core_id = i % core_count
        process = multiprocessing.Process(target=make_single_request, args=(model_name, log_file, time.time_ns(), token_timestamps, stream))
        processes.append(process)
        process.start()
        os.sched_setaffinity(process.pid, {core_id})
        print(f"Process {process.pid} assigned to CPU core {core_id}")

        if len(processes) >= max_processes:
            for p in processes:
                p.join()
            processes = []

    # Ensure all processes finish
    for p in processes:
        p.join()

if __name__ == "__main__":
    model_name = "your_model_name_here"  # Replace with the actual model name
    request_count = 10  # Default number of requests
    with open(f"stress_test_logs_{model_name}.txt", "w+") as log_file:
        run_stress_test_phase(model_name, log_file, request_count)


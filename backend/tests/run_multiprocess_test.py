import multiprocessing
import os
import time  # Added the missing import
from backend.tests.make_single_request import make_single_request

def run_multiprocess_test(model_name, url, request_count, log_file, stream=False, max_processes=8):
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


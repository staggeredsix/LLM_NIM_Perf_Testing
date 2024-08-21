import time
import threading
from backend.tests.calculate_itl import calculate_itl
from backend.tests.make_single_request import make_single_request
import numpy as np

def run_test_phase2(model_name, log_file, request_count, is_concurrent=False):
    """Run Phase 2 of the test (stream=True) for both sequential and concurrent requests."""
    if is_concurrent:
        log_file.write("\nConcurrent Test Phase 2 - Stream = True:\n")
        print("\nStarting Concurrent Test Phase 2 - Stream = True...")

        # Barrier to synchronize thread start
        start_barrier = threading.Barrier(request_count)

        def concurrent_request(thread_index):
            token_timestamps = []
            start_barrier.wait()  # Wait for all threads to be ready

            total_tokens = make_single_request(model_name, log_file, time.time_ns(), token_timestamps, True)

            if total_tokens == 0:
                log_file.write(f"Warning: Thread {thread_index + 1} returned 0 tokens.\n")
                print(f"Warning: Thread {thread_index + 1} returned 0 tokens.")

            # Calculate the ITLs
            itl_list = calculate_itl(token_timestamps)

            # Filter ITLs and limit logging to the first 5
            valid_itl_list = [itl for itl in itl_list if not np.isnan(itl)]

            # Only log the first 5 ITLs and the average
            if thread_index == 0:  # Only display from the first thread to avoid clutter
                log_file.write(f"Inter-Token Latencies (First 5) for Thread {thread_index + 1}: {valid_itl_list[:5]}\n")
                print(f"Inter-Token Latencies (First 5) for Thread {thread_index + 1}: {valid_itl_list[:5]}")

                # Calculate and log the average ITL ignoring NaN values
                if valid_itl_list:
                    average_itl = np.nanmean(valid_itl_list)
                    log_file.write(f"Average Inter-Token Latency for Thread {thread_index + 1}: {average_itl:.6f} seconds\n")
                    print(f"Average Inter-Token Latency for Thread {thread_index + 1}: {average_itl:.6f} seconds")
                else:
                    log_file.write(f"No valid Inter-Token Latencies calculated for Thread {thread_index + 1}.\n")
                    print(f"No valid Inter-Token Latencies calculated for Thread {thread_index + 1}.")

        threads = []
        for i in range(request_count):
            thread = threading.Thread(target=concurrent_request, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    else:
        log_file.write("\nSequential Test Phase 2 - Stream = True:\n")
        print("\nStarting Sequential Test Phase 2 - Stream = True...")
        for i in range(request_count):
            print(f"Sequential Request {i + 1}/{request_count}")

            token_timestamps = []  # Initialize a fresh token_timestamps list for each request

            total_tokens = make_single_request(model_name, log_file, time.time_ns(), token_timestamps, True)

            if total_tokens == 0:
                log_file.write(f"Warning: Request {i + 1} returned 0 tokens.\n")
                print(f"Warning: Sequential Request {i + 1} returned 0 tokens.")

            # Calculate the ITLs for this specific request
            itl_list = calculate_itl(token_timestamps)

            # Filter ITLs and limit logging to the first 5
            valid_itl_list = [itl for itl in itl_list if not np.isnan(itl)]
            log_file.write(f"Inter-Token Latencies (First 5): {valid_itl_list[:5]}\n")
            print(f"Inter-Token Latencies (First 5): {valid_itl_list[:5]}")

            # Calculate and log the average ITL ignoring NaN values
            if valid_itl_list:
                average_itl = np.nanmean(valid_itl_list)
                log_file.write(f"Average Inter-Token Latency: {average_itl:.6f} seconds\n")
                print(f"Average Inter-Token Latency: {average_itl:.6f} seconds")
            else:
                log_file.write("No valid Inter-Token Latencies calculated.\n")
                print("No valid Inter-Token Latencies calculated.")


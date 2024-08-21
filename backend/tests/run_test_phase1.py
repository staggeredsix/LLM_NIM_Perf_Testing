import time
import logging
import threading
from backend.tests.make_single_request import make_single_request

def run_test_phase1(model_name, request_count, log_file):
    """
    Run the Phase 1 test, which includes Sequential and Concurrent requests without streaming.
    This phase measures the time taken for each request and calculates tokens per second (TPS).
    """

    # Sequential Test Phase 1 - Stream = False
    log_file.write("Sequential Test Phase 1 - Stream = False:\n")
    logging.info("Starting Sequential Test Phase 1 - Stream = False...")

    for i in range(request_count):
        logging.info(f"Sequential Request {i + 1}/{request_count}")
        request_start_time = time.time()  # Start the timer for this request

        total_tokens = make_single_request(model_name, log_file, request_start_time, [], stream=False)  # Added missing arguments

        if total_tokens is None:
            total_tokens = 0  # Handle the case where make_single_request returns None

        request_end_time = time.time()  # End the timer for this request

        # Calculate the time taken for this request
        request_duration = request_end_time - request_start_time
        # Calculate tokens per second for this request
        tokens_per_second = total_tokens / request_duration if request_duration > 0 else 0

        # Logging the results
        log_file.write(f"Request {i + 1} completed: {total_tokens} tokens generated in {request_duration:.6f} seconds "
                       f"({tokens_per_second:.6f} tokens/second)\n")
        logging.info(f"Request {i + 1} completed: {total_tokens} tokens generated in {request_duration:.6f} seconds "
                     f"({tokens_per_second:.6f} tokens/second)")

    # Concurrent Test Phase 1 - Stream = False
    log_file.write("\nConcurrent Test Phase 1 - Stream = False:\n")
    logging.info(f"\nStarting Concurrent Test Phase 1 - Stream = False with {request_count} threads...")

    def concurrent_request(thread_index):
        logging.info(f"Thread {thread_index + 1}/{request_count} starting...")
        request_start_time = time.time()  # Start the timer for this request

        total_tokens = make_single_request(model_name, log_file, request_start_time, [], stream=False)  # Added missing arguments

        if total_tokens is None:
            total_tokens = 0  # Handle the case where make_single_request returns None

        request_end_time = time.time()  # End the timer for this request

        # Calculate the time taken for this request
        request_duration = request_end_time - request_start_time
        # Calculate tokens per second for this request
        tokens_per_second = total_tokens / request_duration if request_duration > 0 else 0

        # Logging the results
        with lock:  # Ensure thread-safe logging
            log_file.write(f"Thread {thread_index + 1} completed: {total_tokens} tokens generated in {request_duration:.6f} seconds "
                           f"({tokens_per_second:.6f} tokens/second)\n")
            logging.info(f"Thread {thread_index + 1} completed: {total_tokens} tokens generated in {request_duration:.6f} seconds "
                         f"({tokens_per_second:.6f} tokens/second)")

    # Launch threads for concurrent testing
    threads = []
    lock = threading.Lock()
    for i in range(request_count):
        thread = threading.Thread(target=concurrent_request, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # Wait for all threads to finish

    logging.info("Concurrent Test Phase 1 completed.")
    log_file.write("Concurrent Test Phase 1 completed.\n")


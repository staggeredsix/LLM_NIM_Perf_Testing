import subprocess
import time

def monitor_logs(container_id, log_file):
    token_timestamps = []

    log_process = subprocess.Popen(f"docker logs -f {container_id}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for line in log_process.stdout:
        decoded_line = line.decode('utf-8').strip()
        log_file.write(decoded_line + "\n")

        if "Generated token" in decoded_line:
            current_time = time.time_ns()
            token_timestamps.append(current_time)
            log_file.write(f"Token generated at: {current_time}\n")

            if len(token_timestamps) > 1 and len(token_timestamps) <= 6:
                itl = (token_timestamps[-1] - token_timestamps[-2]) / 1e9
                log_file.write(f"Inter-Token Latency: {itl:.6f} seconds\n")

    log_process.terminate()

    return token_timestamps


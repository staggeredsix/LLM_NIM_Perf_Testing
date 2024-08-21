import requests
import time
from backend.tests.calculate_itl import calculate_itl

def make_single_request(model_name, log_file, total_start_time, token_timestamps, stream=False):
    try:
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
                "stream": stream,
                "frequency_penalty": 1.0
            },
            stream=stream
        )

        if response.status_code == 200:
            total_tokens_in_response = 0
            first_token_time = None
            all_tokens = []

            if stream:
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        token = chunk.decode('utf-8').strip()
                        token_timestamps.append(time.time_ns())
                        all_tokens.append(token)
                        total_tokens_in_response += len(token.split())
                        if not first_token_time:
                            first_token_time = token_timestamps[-1]
            else:
                total_tokens_in_response = sum(len(choice['message']['content'].split()) for choice in response.json().get("choices", []))
                token_timestamps.append(time.time_ns())

            ftl = (token_timestamps[0] - request_send_time) / 1e9
            itl_list = calculate_itl(token_timestamps)
            end_time = time.time_ns()
            total_time = (end_time - request_send_time) / 1e9
            tokens_per_second = total_tokens_in_response / total_time

            log_file.write(f"First Token Latency: {ftl:.6f} seconds\n")
            log_file.write(f"Inter-Token Latencies: {itl_list}\n")
            log_file.write(f"Total Time for This Request: {total_time:.6f} seconds\n")
            log_file.write(f"Tokens per Second: {tokens_per_second:.6f}\n")
            log_file.write(f"Total Tokens: {total_tokens_in_response}\n\n")

            print(f"Request completed: {total_tokens_in_response} tokens generated in {total_time:.6f} seconds ({tokens_per_second:.6f} tokens/second)")
            print(f"First Token Latency: {ftl:.6f} seconds")
            print(f"Inter-Token Latencies: {itl_list}")

            return total_tokens_in_response  # Ensure returning the correct value

        else:
            log_file.write(f"Error: Received unexpected status code {response.status_code}\n")
            log_file.write(response.text + "\n\n")
            print(f"Error: Received unexpected status code {response.status_code}")
            return 0  # Return 0 tokens if the status code is not 200

    except Exception as e:
        log_file.write(f"Error during request: {e}\n\n")
        print(f"Error during request: {e}")
        return 0  # Return 0 tokens in case of an exception


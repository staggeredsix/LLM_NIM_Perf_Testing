import re

def extract_model_from_logs(logs):
    model_pattern = r'"model":\s*"([^"]+)"'
    match = re.search(model_pattern, logs)
    if match:
        return match.group(1)
    else:
        raise ValueError("Model identifier not found in the logs.")


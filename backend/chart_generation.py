import os
import matplotlib.pyplot as plt

def generate_charts():
    # Get the directory where nim_testing.py resides
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "performance_results")

    # Check if the directory exists
    if not os.path.exists(output_dir):
        print(f"No performance results directory found at {output_dir}.")
        return

    # Process each log file in the directory
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                process_log_file(file_path)

def process_log_file(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Extract relevant data from the log file
    model_name = ""
    sequential_times = []
    concurrent_times = []

    for line in lines:
        if "Model:" in line:
            model_name = line.split(":")[1].strip()
        elif "First Token Latency" in line or "Tokens per Second" in line:
            value = float(line.split(":")[1].strip().split()[0])
            sequential_times.append(value)
        elif "Concurrent" in line:
            concurrent_times.append(value)

    if sequential_times:
        generate_chart(model_name, sequential_times, "Sequential Requests")

    if concurrent_times:
        generate_chart(model_name, concurrent_times, "Concurrent Requests")

def generate_chart(model_name, times, title):
    plt.figure()
    plt.plot(times, marker='o')
    plt.title(f"{model_name} - {title}")
    plt.xlabel("Request Number")
    plt.ylabel("Time (seconds)")
    plt.grid(True)
    
    # Save the chart to the same directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    chart_filename = os.path.join(script_dir, f"{model_name}_{title.replace(' ', '_')}.png")
    plt.savefig(chart_filename)
    plt.close()
    print(f"Chart saved to {chart_filename}")



# We print NaN for negative token latency because they're invalid measurements due to the amount of tokens being sent.
# We also print NaN for insanely fast ITL that is likely a poor measurement due to timestamps.
# This needs additional optimization. ITL is measured properly but abnormalities do occur.
import math
import numpy as np

def calculate_itl(token_timestamps):
    """Calculate the Inter-Token Latency (ITL) based on token timestamps."""
    itl_list = []
    for i in range(1, len(token_timestamps)):
        itl = (token_timestamps[i] - token_timestamps[i - 1]) / 1e9  # Convert nanoseconds to seconds

        # Replace ITLs with small or negative values with NaN
        if itl < 0 or abs(itl) < 1e-6:
            itl = float('nan')  # Replace with NaN

        itl_list.append(itl)

    return itl_list


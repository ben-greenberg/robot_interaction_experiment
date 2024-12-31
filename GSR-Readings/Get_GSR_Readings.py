
#!/usr/bin/env python
"""
ReceiveAndPlot example for LSL with graceful shutdown and immediate data writing to file.
"""

import math
import os
import numpy as np
import pylsl
import csv
import requests
from datetime import datetime
import signal
import sys

# Basic parameters
plot_duration = 5  # how many seconds of data to show
update_interval = 60  # ms between screen updates
pull_interval = 500  # ms between each pull operation

channel_to_plot = 32  # Channel number to plot (0-indexed)

# Path to the control file used for termination signal
control_file_path = r"C:\Users\benrg\OneDrive - Rutgers University\Documents\Rutgers\Research\Path Curvature Experiment\Phase 2\robot_interaction_experiment\GSR-Readings\control.txt"  # Update with correct path

# Get the current time for filenames
def get_time():
    """Fetch the current time either from an online API or fallback to local time."""
    try:
        response = requests.get('http://worldtimeapi.org/api/timezone/America/New_York')
        jsonResponse = response.json()
        if 'datetime' in jsonResponse:
            return jsonResponse['datetime']
    except Exception as e:
        print(f"Error fetching time: {e}. Using local time as fallback.")
        now = datetime.now()
        return now.strftime("%Y-%m-%dT%H-%M-%S")  # Format timestamp

# Generate a new filename based on the current timestamp
cTime = get_time().replace(":", "-")
save_dir = r"\Users\benrg\OneDrive - Rutgers University\Documents\Rutgers\Research\Path Curvature Experiment\Phase 2\robot_interaction_experiment\GSR_Readings"
save_dir = os.path.join(r"C:\Users\benrg\OneDrive - Rutgers University\Documents\Rutgers\Research\Path Curvature Experiment\Phase 2\robot_interaction_experiment\GSR_Readings")
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
file_name = os.path.join(save_dir, f"GSR_{cTime}.csv")
print(f"Data will be saved to: {file_name}")

# Create a list to accumulate data
data_to_write = []

def create_data_inlet(info):
    """Create a DataInlet for continuous, multi-channel data."""
    inlet = pylsl.StreamInlet(
        info,
        max_buflen=plot_duration,
        processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter,
    )
    channel_count = info.channel_count()
    bufsize = (2 * math.ceil(info.nominal_srate() * plot_duration), channel_count)
    buffer = np.empty(bufsize, dtype=np.float32 if info.channel_format() == pylsl.cf_float32 else np.float64)

    return {
        'inlet': inlet,
        'buffer': buffer,
        'channel_count': channel_count
    }

def create_marker_inlet(info):
    """Create a MarkerInlet for events that happen sporadically."""
    inlet = pylsl.StreamInlet(
        info,
        max_buflen=plot_duration,
        processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter,
    )
    return {'inlet': inlet}

def pull_and_plot_data(inlet, plot_time):
    """Pull data from the inlet and add it to the list."""
    buffer = inlet['buffer']
    channel_count = inlet['channel_count']
    lsl_inlet = inlet['inlet']
   
    _, ts = lsl_inlet.pull_chunk(timeout=0.0, max_samples=buffer.shape[0], dest_obj=buffer)
    if ts:
        ts = np.asarray(ts)
        y = buffer[:ts.size, :]
        for t, v in zip(ts, y[:, channel_to_plot]):
            data_to_write.append([t, v])

def pull_and_plot_markers(inlet):
    """Pull markers from the inlet and add them to the list."""
    strings, timestamps = inlet['inlet'].pull_chunk(0)
    if timestamps:
        for string, ts in zip(strings, timestamps):
            data_to_write.append([ts, string[0]])

def check_for_termination():
    """Checks the control file for termination signal."""
    try:
        with open(control_file_path, 'r') as file:
            signal = file.read().strip()  # Read the control file
            return signal == "terminate"  # Return True if termination signal is found
    except FileNotFoundError:
        print(f"Control file not found at {control_file_path}")
        return False
    except Exception as e:
        print(f"Error checking control file: {e}")
        return False

# Signal handler to ensure graceful shutdown and immediate data saving
def signal_handler(sig, frame):
    """Handles termination signal and writes data to file."""
    print("\nGraceful shutdown detected. Writing data to file...")
    try:
        with open(file_name, 'w', newline='') as file:
            write = csv.writer(file)
            write.writerow(["Timestamp", "Reading"])
            write.writerows(data_to_write)
            file.flush()
        print(f"Data written to {file_name}")
    except Exception as e:
        print(f"Error writing data to file: {e}")
    sys.exit(0)

# Register the signal handler for SIGINT (keyboard interrupt)
signal.signal(signal.SIGINT, signal_handler)

def main():
    # Resolve all streams that could be shown
    inlets = []
    print("Looking for streams...")
    streams = pylsl.resolve_streams()

    # Iterate over found streams, creating inlet objects that will handle data
    for info in streams:
        if info.type() == "Markers":
            if info.nominal_srate() != pylsl.IRREGULAR_RATE or info.channel_format() != pylsl.cf_string:
                print("Invalid marker stream " + info.name())
            else:
                print("Adding marker inlet: " + info.name())
                inlets.append({'type': 'marker', 'inlet': create_marker_inlet(info)})
        elif info.nominal_srate() != pylsl.IRREGULAR_RATE and info.channel_format() != pylsl.cf_string:
            print("Adding data inlet: " + info.name())
            inlets.append({'type': 'data', 'inlet': create_data_inlet(info)})
        else:
            print("Don't know what to do with stream " + info.name())

    def update():
        """Read data from the inlet and add it to the list."""
        mintime = pylsl.local_clock() - plot_duration
        for inlet in inlets:
            if inlet['type'] == 'data':
                pull_and_plot_data(inlet['inlet'], mintime)
            elif inlet['type'] == 'marker':
                pull_and_plot_markers(inlet['inlet'])

    try:
        # Create a timer that will pull and add new data occasionally
        while True:
            update()

            # Check if termination signal is present in control file
            if check_for_termination():
                print("Termination signal received. Shutting down gracefully...")
                signal_handler(None, None)  # Call the signal handler to write the data and exit gracefully

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
ReceiveAndPlot example for LSL

This example shows data from all found outlets in realtime.
It illustrates the following use cases:
- efficiently pulling data, re-using buffers
- automatically discarding older samples
- online postprocessing
"""

import math
import os
from typing import List

import numpy as np
import pylsl
import csv
import requests
from datetime import datetime

# Basic parameters
plot_duration = 5  # how many seconds of data to show
update_interval = 60  # ms between screen updates
pull_interval = 500  # ms between each pull operation

channel_to_plot = 33  # Channel number to plot (0-indexed)

def getTime():
    try: 
        response = requests.get('http://worldtimeapi.org/api/timezone/America/New_York')
        jsonResponse = response.json()
        if 'datetime' in jsonResponse:
            return jsonResponse['datetime']
    except: 
        now = datetime.now()
        # Replace colons with dashes in the timestamp for compatibility with Windows
        current_time = now.strftime("%Y-%m-%dT%H-%M-%S")  # Format the timestamp to remove colons
        return current_time


# Generate a new filename based on the current timestamp
cTime = getTime().replace(":", "-")
fileName = r"\Users\benrg\OneDrive - Rutgers University\Documents\Rutgers\Research\Path Curvature Experiment\Phase 2\robot_interaction_experiment\HeartRate_Readings\HeartRate_{0}.csv".format(cTime)
dir = r"\Users\benrg\OneDrive - Rutgers University\Documents\Rutgers\Research\Path Curvature Experiment\Phase 2\robot_interaction_experiment\HeartRate_Readings"
if not os.path.exists(dir):
        os.makedirs(dir)
print(f"Data will be saved to: {fileName}")

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

def main():
    # Resolve all streams that could be shown
    inlets = []
    print("looking for streams")
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

    except KeyboardInterrupt:
        # Handle graceful shutdown when keyboard interrupt occurs
        print("Keyboard Interrupt detected. Writing data to file...")
    finally:
        # Write accumulated data to CSV file when the script stops or is interrupted
        with open(fileName, 'w', newline='') as file:
            write = csv.writer(file)
            write.writerow(["Timestamp", "Reading"])
            write.writerows(data_to_write)
        print(f"Data written to {fileName}")

if __name__ == "__main__":
    main()

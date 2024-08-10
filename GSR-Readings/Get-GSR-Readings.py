#!/usr/bin/env python
"""
ReceiveAndPlot example for LSL

This example demonstrates how to receive and plot data from multiple data streams in real-time.
It showcases:
- Efficiently pulling data and reusing buffers
- Automatically discarding older samples to keep the plot updated
- Performing online post-processing of data
"""

import math
from typing import List

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

import pylsl
import csv
import requests
from datetime import datetime

# Define basic parameters for the plotting window
plot_duration = 5  # Duration in seconds for how long data is shown on the plot
update_interval = 60  # Interval in milliseconds between updates to the plot
pull_interval = 500  # Interval in milliseconds between each data pull operation

channel_to_plot = 32  # Index of the channel to be plotted (0-indexed)

def getTime():
    """Fetch the current time from an online API or use local time if the API fails."""
    try: 
        # Attempt to get current time from the worldtimeapi
        response = requests.get('http://worldtimeapi.org/api/timezone/America/New_York')
        jsonResponse = response.json()
        if 'datetime' in jsonResponse:
            return jsonResponse['datetime']
    except: 
        # If API request fails, fallback to local time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        return current_time

# Format the time to use in the filename for saving data
cTime = getTime().replace(":", "-")
fileName = r"C:\Users\RAMlab\GSR_Data\GSR_Output_{0}.csv".format(cTime)
print(fileName)

# List to store data that will be written to a CSV file
data_to_write = []

def create_data_inlet(info, plt):
    """
    Create a data inlet for continuous, multi-channel data.

    Parameters:
    - info: StreamInfo object containing information about the data stream
    - plt: Pyqtgraph PlotItem where data will be plotted

    Returns:
    - A dictionary containing:
      - 'inlet': StreamInlet object for pulling data
      - 'buffer': Buffer array to store incoming data
      - 'curves': List of PlotCurveItem objects for each channel
      - 'highlight_curve': PlotCurveItem for highlighting current data
      - 'channel_count': Number of channels in the data stream
    """
    # Create a StreamInlet to receive data from the stream
    inlet = pylsl.StreamInlet(
        info,
        max_buflen=plot_duration,  # Buffer length in seconds
        processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter,  # Flags for synchronization and jitter correction
    )
    channel_count = info.channel_count()  # Get the number of channels
    bufsize = (2 * math.ceil(info.nominal_srate() * plot_duration), channel_count)  # Calculate buffer size
    buffer = np.empty(bufsize, dtype=np.float32 if info.channel_format() == pylsl.cf_float32 else np.float64)  # Initialize buffer
   
    # Create a plot curve for each channel
    curves = [pg.PlotCurveItem(autoDownsample=True) for _ in range(channel_count)]
    for curve in curves:
        plt.addItem(curve)  # Add each curve to the plot
   
    # Create a highlight curve to visually indicate the current data point
    highlight_curve = pg.PlotCurveItem(pen=pg.mkPen(color='r', width=2))
    plt.addItem(highlight_curve)
   
    return {
        'inlet': inlet,
        'buffer': buffer,
        'curves': curves,
        'highlight_curve': highlight_curve,
        'channel_count': channel_count
    }

def create_marker_inlet(info):
    """
    Create a marker inlet for sporadic events like triggers or labels.

    Parameters:
    - info: StreamInfo object containing information about the marker stream

    Returns:
    - A dictionary containing:
      - 'inlet': StreamInlet object for pulling markers
    """
    inlet = pylsl.StreamInlet(
        info,
        max_buflen=plot_duration,  # Buffer length in seconds
        processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter,  # Flags for synchronization and jitter correction
    )
    return {'inlet': inlet}

def pull_and_plot_data(inlet, plot_time, plt):
    """
    Pull data from the inlet and update the plot.

    Parameters:
    - inlet: Dictionary containing the StreamInlet and other related objects
    - plot_time: The time up to which data should be displayed
    - plt: Pyqtgraph PlotItem where data will be plotted
    """
    buffer = inlet['buffer']
    curves = inlet['curves']
    highlight_curve = inlet['highlight_curve']
    channel_count = inlet['channel_count']
    lsl_inlet = inlet['inlet']
   
    # Pull data from the inlet (non-blocking)
    _, ts = lsl_inlet.pull_chunk(timeout=0.0, max_samples=buffer.shape[0], dest_obj=buffer)
    if ts:
        ts = np.asarray(ts)
        y = buffer[:ts.size, :]  # Extract data corresponding to the timestamps
        old_x, old_y = curves[channel_to_plot].getData()  # Get existing data from the curve
        old_offset = old_x.searchsorted(plot_time) if old_x is not None else 0  # Find where to start new data
        new_offset = ts.searchsorted(plot_time)  # Find the new data starting point
       
        # Concatenate old and new data
        this_x = np.hstack((old_x[old_offset:], ts[new_offset:])) if old_x is not None else ts[new_offset:]
        this_y = np.hstack((old_y[old_offset:], y[new_offset:, channel_to_plot])) if old_y is not None else y[new_offset:, channel_to_plot]
       
        # Update the plot curves with new data
        curves[channel_to_plot].setData(this_x, this_y)
        highlight_curve.setData(this_x, this_y)
       
        # Append new data to the list for CSV writing
        for t, v in zip(this_x, this_y):
            data_to_write.append([t, v])

def pull_and_plot_markers(inlet, plt):
    """
    Pull markers from the inlet and add them to the plot.

    Parameters:
    - inlet: Dictionary containing the StreamInlet for markers
    - plt: Pyqtgraph PlotItem where markers will be plotted
    """
    strings, timestamps = inlet['inlet'].pull_chunk(0)
    if timestamps:
        for string, ts in zip(strings, timestamps):
            # Add a vertical line for each marker with a label
            plt.addItem(pg.InfiniteLine(ts, angle=90, movable=False, label=string[0]))

def main():
    """
    Main function to initialize the plot, create inlets, and start the event loop.
    """
    # Resolve all available streams
    inlets = []
    print("Looking for streams")
    streams = pylsl.resolve_streams()
   
    # Create the pyqtgraph plotting window
    pw = pg.plot(title="LSL Plot")
    plt = pw.getPlotItem()
    plt.enableAutoRange(x=False, y=True)
   
    # Create inlet objects for each found stream
    for info in streams:
        if info.type() == "Markers":
            if info.nominal_srate() != pylsl.IRREGULAR_RATE or info.channel_format() != pylsl.cf_string:
                print("Invalid marker stream " + info.name())
            else:
                print("Adding marker inlet: " + info.name())
                inlets.append({'type': 'marker', 'inlet': create_marker_inlet(info)})
        elif info.nominal_srate() != pylsl.IRREGULAR_RATE and info.channel_format() != pylsl.cf_string:
            print("Adding data inlet: " + info.name())
            inlets.append({'type': 'data', 'inlet': create_data_inlet(info, plt)})
        else:
            print("Don't know what to do with stream " + info.name())

    def scroll():
        """Move the plot view so the data appears to scroll horizontally."""
        fudge_factor = pull_interval * 0.002  # Small adjustment to ensure smooth scrolling
        plot_time = pylsl.local_clock()  # Get the current time from the LSL clock
        pw.setXRange(plot_time - plot_duration + fudge_factor, plot_time - fudge_factor)

    def update():
        """Read data from the inlets and update the plot."""
        mintime = pylsl.local_clock() - plot_duration  # Calculate the minimum time to display
        for inlet in inlets:
            if inlet['type'] == 'data':
                pull_and_plot_data(inlet['inlet'], mintime, plt)
            elif inlet['type'] == 'marker':
                pull_and_plot_markers(inlet['inlet'], plt)

    # Timer to scroll the plot view at regular intervals
    update_timer = QtCore.QTimer()
    update_timer.timeout.connect(scroll)
    update_timer.start(update_interval)

    # Timer to pull new data and update the plot at regular intervals
    pull_timer = QtCore.QTimer()
    pull_timer.timeout.connect(update)
    pull_timer.start(pull_interval)

    import sys

    # Start the Qt event loop unless running in interactive mode or using pyside
    if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        QtGui.QGuiApplication.instance().exec_()

    # Save accumulated data to a CSV file after closing the application
    with open(fileName, 'w', newline='') as file:
        write = csv.writer(file)
        write.writerow(["Timestamp", "Reading", "Pull Start Time"])  # Write header row
        write.writerows(data_to_write)  # Write all collected data
    print(f"Data written to {fileName}")

if __name__ == "__main__":
    main()

Here's a more detailed `README.md` with an extensive script breakdown, including explanations for each function and pylsl functionality:

# ReceiveAndPlot Example for LSL

## Overview

This script demonstrates how to receive and plot data from multiple streams in real-time using the Lab Streaming Layer (LSL). The code efficiently pulls data, re-uses buffers, automatically discards older samples, and performs online post-processing. It handles both continuous data streams and sporadic event markers, updating an interactive plot and saving the accumulated data to a CSV file upon closing the application.

## Dependencies

Before running the script, ensure you have the following Python libraries installed:

- **`numpy`**: A package for numerical operations and data manipulation.
- **`pyqtgraph`**: Provides fast and interactive plotting capabilities.
- **`pylsl`**: The Python library for interfacing with the Lab Streaming Layer (LSL).
- **`requests`**: Used to fetch the current time from an API.
- **`csv`**: For writing data to CSV files.
- **`datetime`**: For handling date and time operations.

To install the required dependencies, use:

```bash
pip install numpy pyqtgraph pylsl requests
```

## Script Breakdown

### Basic Parameters

```python
plot_duration = 5  # Duration (in seconds) of data to be shown on the plot
update_interval = 60  # Interval (in milliseconds) between updates to the plot
pull_interval = 500  # Interval (in milliseconds) between data pulls from streams
channel_to_plot = 32  # Index of the channel to be plotted (0-indexed)
```

- **`plot_duration`**: Specifies how long (in seconds) of data will be displayed on the plot. For example, a `plot_duration` of 5 means the plot shows 5 seconds of data at any time.
- **`update_interval`**: Defines how often (in milliseconds) the plot will be refreshed with new data. A value of 60 milliseconds means the plot is updated roughly every 60 ms.
- **`pull_interval`**: Determines how frequently (in milliseconds) data is pulled from the streams. A value of 500 ms means data is fetched every half-second.
- **`channel_to_plot`**: Specifies which data channel will be plotted. Channels are zero-indexed, so `channel_to_plot = 32` refers to the 33rd channel.

### Functions

#### `getTime()`

```python
def getTime():
    """Fetch the current time from an online API or use local time if the API fails."""
```

- **Purpose**: Retrieves the current time. It first tries to fetch the time from an online API; if the request fails, it uses the local system time.
- **Returns**: A string representing the current time in the format "YYYY-MM-DDTHH:MM:SS".

#### `create_data_inlet(info, plt)`

```python
def create_data_inlet(info, plt):
    """
    Create a data inlet for continuous, multi-channel data.

    Parameters:
    - info: StreamInfo object containing information about the data stream
    - plt: Pyqtgraph PlotItem where data will be plotted

    Returns:
    - A dictionary with:
      - 'inlet': StreamInlet object for pulling data
      - 'buffer': Buffer array to store incoming data
      - 'curves': List of PlotCurveItem objects for each channel
      - 'highlight_curve': PlotCurveItem for highlighting current data
      - 'channel_count': Number of channels in the data stream
    """
```

- **Purpose**: Sets up an inlet for receiving continuous data streams.
- **Parameters**:
  - `info`: A `StreamInfo` object from `pylsl` that describes the data stream, including its format and sampling rate.
  - `plt`: The `PlotItem` from `pyqtgraph` where the data will be displayed.
- **Returns**: A dictionary containing:
  - `'inlet'`: A `StreamInlet` object that allows for pulling data from the stream.
  - `'buffer'`: A numpy array buffer that temporarily stores incoming data.
  - `'curves'`: A list of `PlotCurveItem` objects (one for each channel) used for plotting the data.
  - `'highlight_curve'`: A `PlotCurveItem` that highlights the data currently being displayed.
  - `'channel_count'`: The number of channels in the data stream.

#### `create_marker_inlet(info)`

```python
def create_marker_inlet(info):
    """
    Create a marker inlet for sporadic events like triggers or labels.

    Parameters:
    - info: StreamInfo object containing information about the marker stream

    Returns:
    - A dictionary with:
      - 'inlet': StreamInlet object for pulling markers
    """
```

- **Purpose**: Sets up an inlet for receiving event markers.
- **Parameters**:
  - `info`: A `StreamInfo` object from `pylsl` that describes the marker stream.
- **Returns**: A dictionary containing:
  - `'inlet'`: A `StreamInlet` object for pulling event markers.

#### `pull_and_plot_data(inlet, plot_time, plt)`

```python
def pull_and_plot_data(inlet, plot_time, plt):
    """
    Pull data from the inlet and update the plot.

    Parameters:
    - inlet: Dictionary containing the StreamInlet and other related objects
    - plot_time: The time up to which data should be displayed
    - plt: Pyqtgraph PlotItem where data will be plotted
    """
```

- **Purpose**: Retrieves data from the inlet and updates the plot.
- **Parameters**:
  - `inlet`: A dictionary containing the `StreamInlet`, buffer, and plotting items.
  - `plot_time`: The time up to which the data should be displayed on the plot.
  - `plt`: The `PlotItem` used to display the data.
- **Behavior**:
  - Pulls a chunk of data from the `StreamInlet` using `inlet['inlet'].pull_chunk()`.
  - Updates the plot curves with the new data.
  - Appends the new data to a list (`data_to_write`) for later export.

#### `pull_and_plot_markers(inlet, plt)`

```python
def pull_and_plot_markers(inlet, plt):
    """
    Pull markers from the inlet and add them to the plot.

    Parameters:
    - inlet: Dictionary containing the StreamInlet for markers
    - plt: Pyqtgraph PlotItem where markers will be plotted
    """
```

- **Purpose**: Retrieves and plots event markers.
- **Parameters**:
  - `inlet`: A dictionary containing the `StreamInlet` for markers.
  - `plt`: The `PlotItem` used to plot the markers.
- **Behavior**: Adds vertical lines at the marker timestamps and labels them accordingly on the plot.

### Main Function

#### `main()`

```python
def main():
    """
    Main function to initialize the plot, create inlets, and start the event loop.
    """
```

- **Purpose**: Initializes the plotting window, creates inlets for data and markers, and starts the Qt event loop.
- **Behavior**:
  - Resolves all available LSL streams using `pylsl.resolve_streams()`.
  - Creates a `pyqtgraph` plot window.
  - Iterates over the found streams, creating appropriate inlets for data or markers.
  - Defines and sets up timers to periodically update the plot and scroll the view.
  - Exports the accumulated data to a CSV file upon closing the application.

### Key `pylsl` Functions

- **`pylsl.resolve_streams()`**: Finds all available LSL streams. It returns a list of `StreamInfo` objects, each describing a stream's metadata (e.g., type, format, sampling rate).

- **`pylsl.StreamInlet(info, max_buflen, processing_flags)`**: Creates a new `StreamInlet` object for receiving data.
  - **Parameters**:
    - `info`: A `StreamInfo` object with metadata about the stream.
    - `max_buflen`: The maximum length of the buffer to store incoming data.
    - `processing_flags`: Flags for data processing, such as `pylsl.proc_clocksync` for clock synchronization and `pylsl.proc_dejitter` for removing jitter.
  - **Returns**: A `StreamInlet` object for pulling data from the stream.

- **`inlet.pull_chunk(timeout, max_samples, dest_obj)`**: Pulls a chunk of data from the `StreamInlet`.
  - **Parameters**:
    - `timeout`: Time (in seconds) to wait for data before giving up.
    - `max_samples`: Maximum number of samples to pull.
    - `dest_obj`: The buffer where the pulled data will be stored.
  - **Returns**: A tuple with two elements:
    - A numpy array of the pulled data samples.
    - A list of timestamps corresponding to the data samples.

- **`pylsl.local_clock()`**: Returns the current local clock time as a floating-point number representing seconds since an arbitrary epoch.

## Usage

1. **Run the Script**: Execute the script to start receiving and plotting data.
2. **View Plot**: The plotting window will display data from the available streams.
3. **CSV Export**: Upon closing the application, data will be saved to a CSV file specified by the `fileName` variable.

## Troubleshooting

- **Dependencies**: Ensure all required Python packages are installed. Use `pip install numpy pyqtgraph pylsl requests`.
- **Data Streams**: Verify that data streams are available and properly configured in your LSL system.
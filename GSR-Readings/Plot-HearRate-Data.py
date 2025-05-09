import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks
import os

np.set_printoptions(suppress=True)

def butter_lowpass(cutoff, fs, order=2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def apply_minor_noise_filter(data, cutoff, fs, order=2):
    b, a = butter_lowpass(cutoff, fs, order=order)
    return filtfilt(b, a, data)

def calculate_heart_rate(peaks, times):
    peak_times = times[peaks]
    intervals = np.diff(peak_times)
    if len(intervals) == 0:
        return [], 0, 0, 0
    bpm_values = 60 / intervals  # Convert seconds to BPM
    return bpm_values, np.mean(bpm_values), np.max(bpm_values), np.min(bpm_values)

def process_and_plot(file_path):
    try:
        data = pd.read_csv(file_path)

        times = data['Timestamp'].values
        raw_signal = data['Reading'].values

        if len(times) < 2:
            print(f"{os.path.basename(file_path)}: Not enough data.")
            return

        # Normalize time if needed
        if np.max(times) > 1e4:
            times = times / 1000.0

        fs = 1 / np.mean(np.diff(times))

        # Filter to remove only minor noise
        filtered_signal = apply_minor_noise_filter(raw_signal, cutoff=3, fs=fs)

        # Detect peaks (distance param ensures reasonable spacing for heart rate)
        min_distance = int(fs * 0.3)  # minimum 0.3s between beats (~200 BPM max)
        peaks, _ = find_peaks(filtered_signal, distance=min_distance)

        # Heart rate calculation
        bpm_values, avg_bpm, max_bpm, min_bpm = calculate_heart_rate(peaks, times)

        # Plotting
        # Plot Heartrate
        plt.figure(figsize=(10, 5))
        plt.plot(times, filtered_signal, label='Filtered Signal (3 Hz)', color='green')
        plt.plot(times[peaks], filtered_signal[peaks], 'ro', label='Detected Beats')
        plt.xlabel('Time (s)')
        plt.ylabel('Signal')
        plt.title(f'Heart Rate Detection - {os.path.basename(file_path)}')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # Console output
        print(f"{os.path.basename(file_path)} - Heart Rate Stats")
        print(f"  Total Beats Detected: {len(peaks)}")
        print(f"  Average BPM: {avg_bpm:.2f}")
        print(f"  Max BPM: {max_bpm:.2f}")
        print(f"  Min BPM: {min_bpm:.2f}")
        print("  Detected Beat Times (s):")
        print(np.round(times[peaks], 3))

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            process_and_plot(file_path)

    plt.show()

if __name__ == "__main__":
    input_directory = r"/Users/likhith/Downloads/HeartRate_Readings"
    process_directory(input_directory)

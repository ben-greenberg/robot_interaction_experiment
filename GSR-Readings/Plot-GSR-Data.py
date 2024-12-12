import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

def butterLowpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butterLowpassFilter(data, cutoff, fs, order=4):
    b, a = butterLowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Define the path to your CSV file
file_path = r"/Users/likhith/Downloads/GSR_Output.csv"

# Load the CSV data
data = pd.read_csv(file_path)

# Extract GSR data and time
times = data['Timestamp'].values
gsr_data = data['Reading'].values
fs = 1 / np.mean(np.diff(times))  # Calculate the sampling frequency from the time column

# Define the cutoff frequency for the low-pass filter
cutoff_freq = 15 # Hz

# Filter GSR data (low-pass filter with cutoff frequency of 15 Hz)
filtered_gsr = butterLowpassFilter(gsr_data, cutoff_freq, fs)
adjusted_filtered_gsr = butterLowpassFilter(gsr_data, 1, fs)
extra_adjusted_filtered_gsr = butterLowpassFilter(gsr_data, 0.5, fs)

# Plot filtered GSR data
plt.figure(figsize=(10, 5))
plt.plot(times, gsr_data, color='orange')
plt.plot(times, filtered_gsr, color='blue')
plt.plot(times, adjusted_filtered_gsr, color='red')
plt.xlabel('Time (s)')
plt.ylabel('Filtered GSR')
plt.title('Filtered GSR Data')
plt.grid(True)
plt.tight_layout()
plt.show()

# Thresholding to identify elevated GSR
threshold = 0.95e-5  # Adjust threshold as needed
elevated_indices = np.where(filtered_gsr > threshold)
elevated_times = times[elevated_indices]

print("Times when GSR signal is elevated:")
print(elevated_times)

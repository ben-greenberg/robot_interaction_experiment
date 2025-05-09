import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def butterLowpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butterLowpassFilter(data, cutoff, fs, order=4):
    b, a = butterLowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y


def process_file(file_path):
    try:
        data = pd.read_csv(file_path)

        times = data['Timestamp'].values
        gsr_data = data['Reading'].values

        if len(times) < 2:
            print(f"{os.path.basename(file_path)}: Not enough data.")
            return None

        fs = 1 / np.mean(np.diff(times))

        filtered_gsr = butterLowpassFilter(gsr_data, 15, fs)
        adjusted_filtered_gsr = butterLowpassFilter(gsr_data, 1, fs)
        extra_adjusted_filtered_gsr = butterLowpassFilter(gsr_data, 0.5, fs)

        fig, ax = plt.subplots(figsize=(5, 1.5))
        # ax.plot(times, gsr_data, color='orange', label='Original')
        # ax.plot(times, filtered_gsr, color='blue', label='15Hz Filter')
        ax.plot(times, adjusted_filtered_gsr, color='red', label='1Hz Filter')
        ax.plot(times, extra_adjusted_filtered_gsr, color='green', label='0.5Hz Filter')

        ax.set_title(os.path.basename(file_path), fontsize=4)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('GSR')
        ax.legend(fontsize=2)
        ax.grid(True)
        fig.tight_layout()

        return fig

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def display_all_plots(directory_path):
    root = tk.Tk()
    root.title("GSR Plot Viewer")

    canvas = tk.Canvas(root, borderwidth=0)
    frame = tk.Frame(canvas)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", on_frame_configure)

    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            fig = process_file(file_path)
            if fig:
                fig_canvas = FigureCanvasTkAgg(fig, master=frame)
                fig_canvas.draw()
                fig_canvas.get_tk_widget().pack(padx=1, pady=1)

    root.mainloop()


if __name__ == "__main__":
    input_directory = r"/Users/likhith/Downloads/GSR_Readings"
    display_all_plots(input_directory)

import pandas as pd
import os

def process_csv(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Check if the DataFrame has at least 2 rows and 2 columns
    if len(df) < 2 or len(df.columns) < 2:
        print(f"{os.path.basename(file_path)}: Not enough data.")
        return

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Convert the columns to numeric, forcing errors to NaN
    df['Timestamp'] = pd.to_numeric(df['Timestamp'], errors='coerce')
    df['Reading'] = pd.to_numeric(df['Reading'], errors='coerce')

    # Get the value from the first row of the 'Timestamp' column
    value_to_subtract = df.iloc[0]['Timestamp']

    # Subtract this value from all rows in the 'Timestamp' column
    df['Timestamp'] -= value_to_subtract

    # Save the updated DataFrame back to the same CSV file
    df.to_csv(file_path, index=False)
    print(f"Processed: {os.path.basename(file_path)}")

def process_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            process_csv(file_path)

if __name__ == "__main__":
    input_directory = r"/Users/likhith/Downloads/GSR_Readings"  # Replace with your directory
    process_directory(input_directory)

import pandas as pd

def process_csv(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Check if the DataFrame has at least 2 rows and 2 columns
    if len(df) < 2 or len(df.columns) < 2:
        print("CSV file does not have enough data.")
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
    print(f"Processed data has been saved to {file_path}")

if __name__ == "__main__":
    input_file = r"/Users/likhith/Downloads/GSR_Output.csv"  # Replace with your CSV file path

    process_csv(input_file)
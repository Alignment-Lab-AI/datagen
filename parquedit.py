import pandas as pd
import pyarrow.parquet as pq
import os

# Function to get user confirmation
def confirm(prompt):
    while True:
        response = input(prompt + " (y/n): ").strip().lower()
        if response in ["y", "n"]:
            return response == "y"

# Get the Parquet file from the current directory
file_path = [f for f in os.listdir() if f.endswith('.parquet')]
if not file_path:
    print("No Parquet files found in the current directory.")
    exit()

file_path = file_path[0]
print(f"Reading Parquet file: {file_path}")

# Read the Parquet file
df = pd.read_parquet(file_path)

# Select and drop columns
while True:
    print("\nColumns in the DataFrame:")
    for idx, col in enumerate(df.columns):
        print(f"{idx + 1}. {col} (First row value: {df[col].iloc[0]})")

    drop_column_number = input("Enter the column number you want to drop, or type 'done': ")
    if drop_column_number.lower() == 'done':
        break

    drop_column_number = int(drop_column_number) - 1
    if drop_column_number < 0 or drop_column_number >= len(df.columns):
        print("Invalid column number. Try again.")
        continue

    drop_column_name = df.columns[drop_column_number]
    df.drop(columns=[drop_column_name], inplace=True)
    print(f"Column '{drop_column_name}' dropped.")

# Rename columns if needed
renamed_columns = []
for col in df.columns:
    if confirm(f"Do you want to rename the column '{col}'?"):
        new_name = input(f"Enter the new name for '{col}': ")
        renamed_columns.append(new_name)
    else:
        renamed_columns.append(col)

# Apply the renaming
df.columns = renamed_columns

# Save as JSON
output_path = "output.json"
df.to_json(output_path, orient='records')

print(f"File saved successfully at {output_path}")

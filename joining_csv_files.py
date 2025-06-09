import pandas as pd

# File paths
source_csv = "budget4 with IDs10.csv"  # Path to the source CSV file
target_csv = "ep32_2016_2017.csv"  # Path to the target CSV file
#output_csv = "budget4 with IDs10.csv"  # Path to the output CSV file

# Read the source and target CSV files
source_df = pd.read_csv(source_csv, encoding="utf-8", sep=";")
##ACHTUNG: adjust encoding to your file; if it has Umlaute, its latin-1
target_df = pd.read_csv(target_csv, sep=";", encoding = "latin-1") 

# Append the source data to the target data
combined_df = pd.concat([target_df, source_df], ignore_index=True)

# Overwrite the source CSV file with the combined data
combined_df.to_csv(source_csv, index=False, encoding="utf-8", sep=";")

print(f"Data from {target_csv} has been appended to {source_csv}")
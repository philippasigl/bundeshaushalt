import pdfplumber
import pandas as pd
import re
import os

def extract_table_from_pdf(pdf_path, columns_to_extract=['epl.\nkap.', 'titel','bezeichnung der finanzhilfe']):
    """
    Extract specific columns from tables in a PDF and save to CSV.
    
    Args:
        pdf_path (str): Path to the PDF file
        columns_to_extract (list): Column names to extract (case insensitive)
    
    Returns:
        DataFrame: Combined data from all pages
    """
    # Normalize the column names for case-insensitive comparison
    columns_to_extract_lower = [col.lower().strip() for col in columns_to_extract]
    
    # Initialize empty list for storing dataframes
    all_data = []
    
    # Open the PDF
    with pdfplumber.open(pdf_path) as pdf:
        # Process each page
        for page_num, page in enumerate(pdf.pages):
            print(f"Processing page {page_num + 1} of {len(pdf.pages)}...")
            
            if page_num + 1 < 67 or page_num + 1 > 95:
                continue

            # Extract tables on this page
            tables = page.extract_tables()
            
            for table_num, table in enumerate(tables):
                if not table:
                    continue
                
                # Convert the table to a DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])
                
                # Check if the DataFrame is empty or doesn't have columns
                if df.empty or not all(isinstance(col, str) for col in df.columns):
                    continue
                
                # Normalize the column names in the DataFrame
                df.columns = [str(col).lower().strip() for col in df.columns]
                
                # Find the matching columns using partial matching
                selected_columns = {}
                for target_col in columns_to_extract_lower:
                    for df_col in df.columns:
                        if target_col in df_col:
                            # Use the original column name as the key
                            original_idx = columns_to_extract_lower.index(target_col)
                            selected_columns[columns_to_extract[original_idx]] = df_col
                            break
                
                # If we found both columns, extract them
                if len(selected_columns) == len(columns_to_extract):
                    extracted_df = df[list(selected_columns.values())].copy()
                    extracted_df.columns = list(selected_columns.keys())
                    all_data.append(extracted_df)
                else:
                    print(f"  Could not find all required columns on page {page_num + 1}, table {table_num + 1}")
                    print(f"  Available columns: {df.columns.tolist()}")
    
    # Combine all DataFrames
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Clean the data: remove empty rows and strip whitespace
        combined_df = combined_df.dropna(how='all')
        for col in combined_df.columns:
            if combined_df[col].dtype == object:
                combined_df[col] = combined_df[col].str.strip()
        
        return combined_df
    else:
        print("No matching tables found.")
        return pd.DataFrame(columns=columns_to_extract)

def main():
    # Get the PDF file path from user
    pdf_path = "29-subventionsbericht.pdf"
    
    # Check if the file exists
    if not os.path.isfile(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    # Extract the tables
    extracted_data = extract_table_from_pdf(pdf_path)
    
    if not extracted_data.empty:
        # Save to CSV
        output_path = pdf_path.rsplit('.', 1)[0] + '_extracted.csv'
        extracted_data.to_csv(output_path, sep=";", index=False, encoding="utf-8")
        print(f"Extracted data saved to: {output_path}")
        print(f"Found {len(extracted_data)} rows of data")
        print("\nPreview of extracted data:")
        print(extracted_data.head())
    else:
        print("No data was extracted.")

if __name__ == "__main__":
    main()
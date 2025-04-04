import pandas as pd
import json
import os
from pathlib import Path

def convert_excel_to_csv(input_file, output_file, sheet_name=None):
    """
    Convert Excel file to CSV.
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output CSV file
        sheet_name: Optional sheet name to extract (default: first sheet)
    """
    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Read Excel file
    df = pd.read_excel(input_file, sheet_name=sheet_name)
    
    # Write to CSV
    df.to_csv(output_file, index=False)
    
    print(f"Converted {input_file} to {output_file}")
    return df


def prepare_customer_data(input_file, output_file):
    """
    Prepare customer data from Excel file and save to CSV.
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output CSV file
    """
    # Convert Excel to CSV
    df = convert_excel_to_csv(input_file, output_file)
    
    print(f"Customer data prepared: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns: {', '.join(df.columns)}")
    
    # Display sample
    print("\nSample customer data:")
    print(df.head(2))


def prepare_product_data(input_file, output_file):
    """
    Prepare product data from Excel file and save to CSV.
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output CSV file
    """
    # Convert Excel to CSV
    df = convert_excel_to_csv(input_file, output_file)
    
    print(f"Product data prepared: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns: {', '.join(df.columns)}")
    
    # Display sample
    print("\nSample product data:")
    print(df.head(2))


def main():
    """Main function to prepare data files."""
    # Create data directory
    Path("data").mkdir(exist_ok=True)
    
    # Prepare customer data
    prepare_customer_data(
        "input/customer_data_collection.xlsx",
        "data/customer_data.csv"
    )
    
    # Prepare product data
    prepare_product_data(
        "input/product_recommendation_data.xlsx",
        "data/product_data.csv"
    )


if __name__ == "__main__":
    main()
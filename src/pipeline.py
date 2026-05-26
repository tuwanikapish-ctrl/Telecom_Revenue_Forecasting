import os
from src.datacleaning import clean_data

def run_pipeline(filepath):
    """
    Runs the data processing pipeline:
    1. Cleans the data
    2. Saves the cleaned data to the processed folder
    """
    print(f"Running pipeline for {filepath}...")
    
    # Clean the data
    df = clean_data(filepath)
    
    # Ensure processed directory exists
    processed_dir = 'data/processed'
    os.makedirs(processed_dir, exist_ok=True)
    
    # Save the cleaned data
    output_path = os.path.join(processed_dir, 'cleaned_data.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Pipeline completed successfully. Cleaned data saved to {output_path}")

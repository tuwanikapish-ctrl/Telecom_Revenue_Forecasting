import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import run_pipeline

if __name__ == "__main__":
    # Default path or argument path
    raw_data_path = "data/raw/data.csv"
    if len(sys.argv) > 1:
        raw_data_path = sys.argv[1]
    
    if not os.path.exists(raw_data_path):
        print(f"Error: {raw_data_path} does not exist.")
        print("Please provide a valid path or place your raw data at data/raw/data.csv")
    else:
        run_pipeline(raw_data_path)

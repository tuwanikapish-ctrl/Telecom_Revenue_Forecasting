import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.forecasting import run_forecast

if __name__ == "__main__":
    processed_data_path = "data/processed/cleaned_data.csv"
    if len(sys.argv) > 1:
        processed_data_path = sys.argv[1]
        
    if not os.path.exists(processed_data_path):
        print(f"Error: {processed_data_path} does not exist.")
        print("Please run preprocess.py first to generate the cleaned data.")
    else:
        forecast_df = run_forecast(processed_data_path)
        print("Forecast Generated Successfully.")
        print(forecast_df.head())
        
        # Save forecast to processed folder
        output_path = "data/processed/forecast_output.csv"
        forecast_df.to_csv(output_path, index=False)
        print(f"Forecast saved to {output_path}")

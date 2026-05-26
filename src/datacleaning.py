import pandas as pd

def clean_data(filepath):
    """
    Reads and cleans the raw data file.
    Supports CSV and Excel files.
    """
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    elif filepath.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(filepath)
    else:
        raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")
        
    # Clean column names
    df.columns = df.columns.str.strip().str.title()
    
    # Check for required columns
    required_cols = ['Date', 'Revenue']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
        
    # Convert Date to datetime and Revenue to numeric
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
    
    # Clean Service column if it exists
    if 'Service' in df.columns:
        df['Service'] = df['Service'].astype(str).str.strip().str.title()
        
    # Drop rows with invalid dates or revenues
    df = df.dropna(subset=['Date', 'Revenue'])
    
    # Sort by date
    df = df.sort_values(by='Date')
    
    return df

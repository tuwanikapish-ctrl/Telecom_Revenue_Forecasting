import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def run_forecast(filepath, days_to_forecast=30):
    """
    Generates a simple linear regression forecast for the revenue.
    Returns a DataFrame with columns: Date, Forecast, Lower, Upper.
    """
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Aggregate revenue by date
    df = df.groupby('Date')['Revenue'].sum().reset_index()
    df = df.sort_values('Date')
    
    # If not enough data, return empty forecast dataframe
    if len(df) < 2:
        return pd.DataFrame(columns=['Date', 'Forecast', 'Lower', 'Upper'])
        
    # Convert dates to numerical values (days since start) for regression
    min_date = df['Date'].min()
    df['Days'] = (df['Date'] - min_date).dt.days
    
    X = df[['Days']].values
    y = df['Revenue'].values
    
    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate future dates
    last_date = df['Date'].max()
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, days_to_forecast + 1)]
    future_days = np.array([[(d - min_date).days] for d in future_dates])
    
    # Predict future revenue
    forecasts = model.predict(future_days)
    
    # Calculate a simple confidence interval based on historical residuals
    historical_predictions = model.predict(X)
    residuals = y - historical_predictions
    std_dev = np.std(residuals) if len(residuals) > 0 else 0
    margin_of_error = 1.96 * std_dev  # Approximate 95% confidence interval
    
    # Create the forecast DataFrame
    forecast_df = pd.DataFrame({
        'Date': future_dates,
        'Forecast': forecasts,
        'Lower': forecasts - margin_of_error,
        'Upper': forecasts + margin_of_error
    })
    
    return forecast_df

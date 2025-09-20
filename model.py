# model.py
from prophet import Prophet
import pandas as pd
import numpy as np

def get_forecast(component_data, periods=90):
    """
    Generates a forecast using Facebook Prophet for the given component data.
    Returns forecast for historical + future periods.
    """
    # Prepare data for Prophet
    prophet_df = component_data[['Date', 'Units_Used']].copy()
    prophet_df = prophet_df.rename(columns={'Date': 'ds', 'Units_Used': 'y'})
    
    # Initialize and fit the model with proper configuration
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.95,  # 95% confidence interval
        seasonality_mode='multiplicative'
    )
    
    model.fit(prophet_df)
    
    # Create future dataframe including the historical period + future periods
    future = model.make_future_dataframe(periods=periods, freq='D')
    
    # Generate forecast
    forecast = model.predict(future)
    
    return forecast

# model.py
import pandas as pd
from prophet import Prophet

def get_forecast(component_data):
    """
    Trains a Prophet model and forecasts demand for the next 90 days.
    Returns the forecast DataFrame.
    """
    # Prepare the data for Prophet: it requires columns 'ds' (date) and 'y' (value)
    df_prophet = component_data[['Date', 'Units_Used']].copy()
    df_prophet.columns = ['ds', 'y']  # Rename columns for Prophet

    # Create and train the model
    model = Prophet()
    model.fit(df_prophet)

    # Generate future timeline (forecast next 90 days)
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)

    return forecast

# calculations.py
import numpy as np
from scipy import stats
import pandas as pd

def calculate_safety_stock(historical_demand, lead_time, service_level=0.95):
    """
    Calculates safety stock based on demand variability.
    SS = Z * σ * √L
    """
    # Z-score for service level (e.g., 95% -> Z = 1.65)
    z_score = stats.norm.ppf(service_level)
    
    # Standard deviation of historical daily demand
    demand_std = np.std(historical_demand)
    
    # Calculate Safety Stock
    safety_stock = z_score * demand_std * np.sqrt(lead_time)
    return round(safety_stock)

def calculate_demand_over_lead_time(forecast_df, lead_time):
    """
    Calculates worst-case demand during lead time using yhat_upper forecast
    D_L = sum(yhat_upper for next L days)
    """
    # Get the future forecast (last 'lead_time' days of the forecast)
    future_forecast = forecast_df.tail(lead_time)
    worst_case_demand = future_forecast['yhat_upper'].sum()
    return round(worst_case_demand)

def calculate_optimal_inventory(forecast_df, lead_time, safety_stock):
    """
    Calculates optimal inventory level using worst-case forecast demand during lead time plus safety stock.
    OIL = D_L (worst-case) + SS
    """
    demand_during_lead_time = calculate_demand_over_lead_time(forecast_df, lead_time)
    optimal_inventory = demand_during_lead_time + safety_stock
    return round(optimal_inventory)

def calculate_order_quantity(optimal_inventory, current_inventory):
    """
    Calculates how much to order.
    ROQ = Max(0, OIL - Current_Stock)
    """
    return max(0, round(optimal_inventory - current_inventory))

def estimate_old_method_inventory(historical_demand, safety_multiplier=60):
    """
    Estimates what inventory would be using a conservative old method.
    Based on maximum historical demand * safety multiplier
    """
    peak_demand = np.max(historical_demand)
    return round(peak_demand * safety_multiplier)

def calculate_cost_savings(optimal_inventory, old_method_inventory, component_cost, holding_cost_rate=0.20):
    """
    Calculates annual cost savings compared to the old inventory method.
    Capital Released = (Old_Inventory - Optimal_Inventory) * Cost
    Annual Savings = Capital Released * Holding_Cost_Rate
    """
    inventory_reduction = old_method_inventory - optimal_inventory
    # Ensure we don't show negative savings if new method is worse (it shouldn't be)
    inventory_reduction = max(0, inventory_reduction)
    capital_released = inventory_reduction * component_cost
    annual_savings = capital_released * holding_cost_rate
    
    return round(annual_savings), inventory_reduction, round(capital_released)

def get_component_cost(component_id, current_df):
    """
    Returns the cost for a given component from the current stocks data.
    """
    try:
        return current_df[current_df['Component_ID'] == component_id]['Unit_Cost'].values[0]
    except:
        # Default costs if not found
        cost_map = {
            'RES-': 0.5, 'CAP-': 0.8, 'IC-': 85.0, 'CONN-': 8.0, 
            'SENSOR-': 45.0, 'MODULE-': 120.0, 'LED-': 1.5, 'MOSFET-': 18.0
        }
        for prefix, cost in cost_map.items():
            if component_id.startswith(prefix):
                return cost
        return 10.0  # Default cost

# calculations.py
import numpy as np
from scipy import stats

def calculate_safety_stock(historical_demand, lead_time, service_level=0.95):
    """
    Calculates safety stock based on demand variability.
    """
    # Z-score for service level (e.g., 95% -> Z = 1.65)
    z_score = stats.norm.ppf(service_level)

    # Standard deviation of historical daily demand
    demand_std = np.std(historical_demand)

    safety_stock = z_score * demand_std * np.sqrt(lead_time)
    return round(safety_stock)

def calculate_optimal_inventory(forecast_df, lead_time, safety_stock):
    """
    Calculates optimal inventory level using worst-case forecast demand during lead time plus safety stock.
    """
    # Get the worst-case (yhat_upper) forecast for the lead time period
    worst_case_demand = forecast_df['yhat_upper'].head(lead_time).sum()
    optimal_inventory = worst_case_demand + safety_stock
    return round(optimal_inventory)

def calculate_order_quantity(optimal_inventory, current_inventory=0):
    """
    Calculates how much to order.
    """
    return max(0, optimal_inventory - current_inventory)

def estimate_old_method_inventory(avg_daily_demand, days_of_stock=60):
    """
    Estimates what inventory would be using the old method (e.g., 60 days of stock).
    This is a simple, common manual method we're comparing against.
    """
    return round(avg_daily_demand * days_of_stock)

def calculate_cost_savings(optimal_inventory, old_method_inventory, component_cost, holding_cost_rate=0.20):
    """
    Calculates annual cost savings compared to the old inventory method.
    This is the MOST IMPORTANT metric for business impact.
    """
    # Calculate reduced inventory
    inventory_reduction = old_method_inventory - optimal_inventory
    
    # Calculate annual holding cost savings (20% of component value per year is standard)
    annual_savings = inventory_reduction * component_cost * holding_cost_rate
    
    return round(annual_savings), inventory_reduction

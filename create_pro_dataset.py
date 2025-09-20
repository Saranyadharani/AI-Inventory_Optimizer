# create_pro_dataset.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def create_hackathon_winning_dataset():
    print("🚀 Creating Professional Hackathon Dataset...")
    print("This dataset will showcase REAL AI capabilities!")
    
    # Create data folder
    os.makedirs('data', exist_ok=True)
    
    # 25 Real Electronic Components with different behaviors
    components = {
        # High-volume passive components (stable demand)
        'RES-10K-0.25W': {'base': 2500, 'cost': 0.5, 'volatility': 0.3, 'category': 'Passive'},
        'CAP-100uF-25V': {'base': 1800, 'cost': 0.8, 'volatility': 0.4, 'category': 'Passive'},
        'CAP-1uF-50V': {'base': 2200, 'cost': 0.3, 'volatility': 0.2, 'category': 'Passive'},
        'DIODE-1N4148': {'base': 1200, 'cost': 0.2, 'volatility': 0.3, 'category': 'Semiconductor'},
        
        # Medium-volume ICs (growing demand)
        'IC-ATMEGA328P': {'base': 450, 'cost': 85.0, 'volatility': 0.6, 'category': 'IC'},
        'IC-ESP32-WROOM': {'base': 320, 'cost': 120.0, 'volatility': 0.8, 'category': 'Module'},
        'IC-STM32F103': {'base': 280, 'cost': 65.0, 'volatility': 0.5, 'category': 'IC'},
        'IC-LM7805': {'base': 380, 'cost': 12.0, 'volatility': 0.4, 'category': 'Power'},
        
        # Connectors and electromechanical
        'CONN-USB-B': {'base': 420, 'cost': 8.0, 'volatility': 0.7, 'category': 'Connector'},
        'CONN-HDMI': {'base': 180, 'cost': 15.0, 'volatility': 0.6, 'category': 'Connector'},
        'CONN-JACK-3.5MM': {'base': 250, 'cost': 6.0, 'volatility': 0.5, 'category': 'Connector'},
        
        # Sensors and modules (volatile demand)
        'SENSOR-DHT22': {'base': 150, 'cost': 45.0, 'volatility': 0.9, 'category': 'Sensor'},
        'SENSOR-HC-SR04': {'base': 120, 'cost': 35.0, 'volatility': 0.8, 'category': 'Sensor'},
        'MODULE-RELAY': {'base': 80, 'cost': 25.0, 'volatility': 0.7, 'category': 'Module'},
        
        # Power components
        'MOSFET-IRF540': {'base': 180, 'cost': 18.0, 'volatility': 0.5, 'category': 'Power'},
        'TRANSISTOR-2N2222': {'base': 300, 'cost': 2.0, 'volatility': 0.4, 'category': 'Semiconductor'},
        
        # Specialized components
        'CRYSTAL-16MHZ': {'base': 200, 'cost': 5.0, 'volatility': 0.3, 'category': 'Oscillator'},
        'LED-RGB-5MM': {'base': 350, 'cost': 1.5, 'volatility': 0.6, 'category': 'Opto'},
        'BUZZER-5V': {'base': 90, 'cost': 8.0, 'volatility': 0.5, 'category': 'Audio'},
        
        # New for 2024 (high growth)
        'IC-RP2040': {'base': 180, 'cost': 95.0, 'volatility': 1.2, 'category': 'IC'},
        'SENSOR-BME280': {'base': 95, 'cost': 65.0, 'volatility': 0.9, 'category': 'Sensor'},
        'MODULE-LORA': {'base': 60, 'cost': 150.0, 'volatility': 1.1, 'category': 'Module'},
        'IC-WIFI-ESP8266': {'base': 220, 'cost': 75.0, 'volatility': 0.8, 'category': 'Module'},
        'CONN-USBC': {'base': 280, 'cost': 12.0, 'volatility': 0.7, 'category': 'Connector'}
    }
    
    # Generate 3 years of daily data (2022-2024)
    dates = pd.date_range('2022-01-01', '2024-12-31', freq='D')
    all_historical = []
    
    print("📈 Generating realistic demand patterns for 25 components...")
    
    for comp_id, config in components.items():
        base = config['base']
        volatility = config['volatility']
        
        # Complex trend with growth
        growth_rate = 1.0 + (volatility * 0.3)  # More volatile = higher growth
        trend = np.linspace(base, base * growth_rate, len(dates))
        
        # Strong weekly seasonality (30-50% weekend drop)
        day_of_week = np.array([d.weekday() for d in dates])
        weekly_season = np.where(day_of_week >= 5, -0.4 * base, 0)
        
        # Strong yearly seasonality (Q4 peak + summer slump)
        month = np.array([d.month for d in dates])
        yearly_season = np.zeros(len(dates))
        yearly_season = np.where(month >= 10, 0.6 * base, yearly_season)  # Q4 peak
        yearly_season = np.where((month >= 6) & (month <= 8), -0.3 * base, yearly_season)  # Summer slump
        
        # Random noise and spikes
        noise = np.random.normal(0, base * 0.2 * volatility, len(dates))
        
        # Occasional demand spikes (5% chance daily)
        spike_mask = np.random.random(len(dates)) < 0.05
        spikes = np.where(spike_mask, base * 2.5 * np.random.random(len(dates)), 0)
        
        # Combine everything
        demand = trend + weekly_season + yearly_season + noise + spikes
        demand = np.maximum(demand, base * 0.2).astype(int)  # No negative values
        
        comp_data = pd.DataFrame({
            'Date': dates,
            'Component_ID': comp_id,
            'Units_Used': demand,
            'Category': config['category']
        })
        
        all_historical.append(comp_data)
    
    # Combine all data
    historical_df = pd.concat(all_historical, ignore_index=True)
    
    # Create current stock levels (realistic based on demand patterns)
    current_stocks = []
    for comp_id, config in components.items():
        comp_data = historical_df[historical_df['Component_ID'] == comp_id]
        avg_daily = comp_data['Units_Used'].mean()
        
        # Realistic stock levels: 45-60 days of average demand
        days_coverage = 45 + (np.random.random() * 15)
        current_stock = int(avg_daily * days_coverage)
        
        current_stocks.append({
            'Component_ID': comp_id,
            'Current_Stock': current_stock,
            'Unit_Cost': config['cost'],
            'Category': config['category'],
            'Avg_Daily_Demand': round(avg_daily, 2),
            'Demand_Volatility': config['volatility']
        })
    
    current_df = pd.DataFrame(current_stocks)
    
    # Save files
    historical_df.to_csv('data/historical_data.csv', index=False)
    current_df.to_csv('data/current_stocks.csv', index=False)
    
    print("✅ Generated professional dataset!")
    print(f"📊 Historical data: {len(historical_df):,} records")
    print(f"📦 {len(components)} components with realistic demand patterns")
    print(f"💰 Total inventory value: ₹{current_df['Current_Stock'].dot(current_df['Unit_Cost']):,.0f}")
    print("\n🎯 This dataset will showcase:")
    print("   - Realistic seasonality & trends")
    print("   - Different component behaviors")
    print("   - Significant cost savings potential")
    print("   - Professional-grade AI analysis")

if __name__ == "__main__":
    create_hackathon_winning_dataset()

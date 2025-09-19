import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Electronics Inventory AI Optimizer",
    page_icon="📈",
    layout="wide"
)

# -------------------- DATA LOADING --------------------
@st.cache_data  # This caches the data so it doesn't reload on every interaction
def load_data():
    # Load your generated dataset from the data folder
    file_path = os.path.join('data', 'electronics_inventory_dataset_2022_2024.csv')
    df = pd.read_csv(file_path)
    
    # FIXED: Explicitly define the date format (DD-MM-YYYY)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')  # Convert to datetime
    return df

df = load_data()

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("🔧 Controls & Filters")

# Component Selector
component_list = df['Component_ID'].unique()
selected_component = st.sidebar.selectbox(
    "Select Electronic Component",
    component_list
)

# Lead Time Input (Business Decision)
lead_time = st.sidebar.slider(
    "Supplier Lead Time (days)",
    min_value=7,
    max_value=90,
    value=30,
    help="Total time from placing order to receiving components"
)

# Service Level Input
service_level = st.sidebar.slider(
    "Target Service Level",
    min_value=0.85,
    max_value=0.99,
    value=0.95,
    help="Probability of not having a stockout (e.g., 0.95 = 95%)"
)

# -------------------- MAIN DASHBOARD LAYOUT --------------------
st.title("🏭 AI-Powered Electronics Inventory Optimizer")
st.markdown("---")

# Row 1: Key Performance Indicators (KPIs)
st.subheader("📊 Inventory Overview")
col1, col2, col3, col4 = st.columns(4)

# Filter data for selected component
component_data = df[df['Component_ID'] == selected_component]

# Calculate some metrics for the KPIs
avg_daily_use = component_data['Units_Used'].mean()
total_units_used = component_data['Units_Used'].sum()

with col1:
    st.metric(label="Avg Daily Usage", value=f"{avg_daily_use:,.0f} units")
with col2:
    st.metric(label="Total Units Used (3Y)", value=f"{total_units_used:,.0f}")
with col3:
    st.metric(label="Lead Time", value=f"{lead_time} days")
with col4:
    st.metric(label="Target Service Level", value=f"{service_level*100:.0f}%")

st.markdown("---")

# Row 2: Charts and Forecast
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Demand Forecast & History")
    
    # Create interactive time series plot
    fig = px.line(component_data, x='Date', y='Units_Used', 
                  title=f'Daily Usage: {selected_component}')
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("⚠️ Inventory Recommendations")
    
    # Placeholder for AI recommendations - WE WILL CONNECT THIS NEXT
    st.info("""
    **AI Analysis Pending**
    
    Connect the model to see:
    - Optimal Inventory Level
    - Safety Stock Required
    - Recommended Order Quantity
    - Estimated Cost Savings
    """)
    
    st.warning("**Priority: HIGH**")
    st.button("🔄 Generate AI Recommendations", type="primary")

# Row 3: Inventory History Table (Simplified)
st.subheader("📋 Recent Inventory Activity")
st.dataframe(component_data.tail(10), use_container_width=True)

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("AI Inventory Optimization System | Built for CREONIX '25 Hackathon")

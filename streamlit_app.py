# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Import your local modules
from calculations import *
from model import get_forecast

# Page config
st.set_page_config(
    page_title="AI Inventory Optimizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        historical = pd.read_csv('data/historical_data.csv')
        current = pd.read_csv('data/current_stocks.csv')
        historical['Date'] = pd.to_datetime(historical['Date'])
        return historical, current
    except FileNotFoundError:
        st.error("❌ Data files not found! Please run: python create_pro_dataset.py")
        return None, None

historical_df, current_df = load_data()

if historical_df is None:
    st.stop()

# Sidebar
st.sidebar.title("🔧 Control Center")
st.sidebar.markdown("---")

component = st.sidebar.selectbox(
    "**Select Electronic Component**",
    sorted(historical_df['Component_ID'].unique()),
    help="Choose which component to analyze"
)

lead_time = st.sidebar.slider(
    "**Supplier Lead Time (Days)**",
    min_value=7,
    max_value=90,
    value=30,
    help="Total time from order to delivery"
)

service_level = st.sidebar.slider(
    "**Target Service Level**",
    min_value=0.85,
    max_value=0.99,
    value=0.95,
    help="Probability of avoiding stockouts (0.95 = 95%)"
)

# Get current stock and cost
current_stock = current_df[current_df['Component_ID'] == component]['Current_Stock'].values[0]
unit_cost = current_df[current_df['Component_ID'] == component]['Unit_Cost'].values[0]
avg_daily_demand = current_df[current_df['Component_ID'] == component]['Avg_Daily_Demand'].values[0]

# Main app
st.markdown('<h1 class="main-header">🏭 AI Inventory Command Center</h1>', unsafe_allow_html=True)
st.markdown("---")

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("**Current Stock**", f"{current_stock:,}", "units")
with col2:
    st.metric("**Avg Daily Demand**", f"{avg_daily_demand:,.0f}", "units/day")
with col3:
    st.metric("**Unit Cost**", f"₹{unit_cost:,.2f}", "per unit")
with col4:
    st.metric("**Service Level**", f"{service_level*100:.0f}%", "target")

st.markdown("---")

# Charts and Analysis
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Historical Demand Analysis")
    comp_data = historical_df[historical_df['Component_ID'] == component]
    
    fig = px.line(comp_data, x='Date', y='Units_Used', 
                 title=f'Demand Pattern: {component}',
                 template='plotly_white')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("⚡ AI Recommendations")
    
    st.info(f"""
    **Ready to Analyze: {component}**
    
    - **Current Stock**: {current_stock:,} units
    - **Lead Time**: {lead_time} days
    - **Service Level**: {service_level*100:.0f}%
    - **Unit Cost**: ₹{unit_cost:,.2f}
    """)
    
    if st.button("🚀 Generate AI Insights", type="primary", use_container_width=True):
        with st.spinner('🤖 AI is analyzing demand patterns...'):
            try:
                # Get the AI forecast
                forecast = get_forecast(comp_data, periods=lead_time + 60)
                
                # Calculate the key metrics
                historical_demand = comp_data['Units_Used'].values
                safety_stock = calculate_safety_stock(historical_demand, lead_time, service_level)
                optimal_inventory = calculate_optimal_inventory(forecast, lead_time, safety_stock)
                order_quantity = calculate_order_quantity(optimal_inventory, current_stock)
                
                # Calculate cost savings
                old_method_inventory = estimate_old_method_inventory(historical_demand)
                annual_savings, inventory_reduction, capital_released = calculate_cost_savings(
                    optimal_inventory, old_method_inventory, unit_cost
                )
                
                # Display the results
                st.success("🎯 AI Analysis Complete! Optimization Results:")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("**Optimal Inventory**", f"{optimal_inventory:,}", 
                             f"vs old: {old_method_inventory:,}")
                with col2:
                    st.metric("**Safety Stock**", f"{safety_stock:,}", 
                             f"{service_level*100:.0f}% service level")
                with col3:
                    st.metric("**Order Quantity**", f"{order_quantity:,}", 
                             "Recommended order")
                
                # Financial impact
                st.markdown("---")
                st.subheader("💰 Financial Impact Analysis")
                
                col4, col5, col6 = st.columns(3)
                with col4:
                    st.metric("**Inventory Reduction**", f"{inventory_reduction:,}", "units")
                with col5:
                    st.metric("**Capital Released**", f"₹{capital_released:,}", "immediate benefit")
                with col6:
                    st.metric("**Annual Savings**", f"₹{annual_savings:,}", "20% holding cost")
                
                # Priority status
                st.markdown("---")
                if current_stock < safety_stock:
                    st.error("🚨 CRITICAL: Risk of imminent stockout! Order immediately.")
                elif current_stock < optimal_inventory:
                    st.warning("⚠️  WARNING: Stock levels below optimal. Monitor closely.")
                else:
                    st.success("✅ HEALTHY: Stock levels are optimal or above.")
                    
            except Exception as e:
                st.error(f"❌ Error in AI analysis: {str(e)}")
                st.info("💡 Make sure all dependencies are installed: pip install -r requirements.txt")

# Portfolio Overview
st.markdown("---")
st.subheader("📊 Portfolio Overview")

col1, col2, col3 = st.columns(3)
with col1:
    total_components = len(current_df)
    st.metric("Total Components", total_components)
with col2:
    total_inventory_value = (current_df['Current_Stock'] * current_df['Unit_Cost']).sum()
    st.metric("Total Inventory Value", f"₹{total_inventory_value:,.0f}")
with col3:
    total_categories = current_df['Category'].nunique()
    st.metric("Product Categories", total_categories)

# Category distribution
st.subheader("📦 Inventory by Category")
category_summary = current_df.groupby('Category').agg({
    'Component_ID': 'count',
    'Current_Stock': 'sum',
    'Unit_Cost': 'mean'
}).rename(columns={'Component_ID': 'Count', 'Unit_Cost': 'Avg_Cost'})

fig1 = px.pie(current_df, values='Current_Stock', names='Category', 
             title='Inventory Distribution by Category')
st.plotly_chart(fig1, use_container_width=True)

# Footer
st.markdown("---")
st.caption("🏆 AI-Powered Inventory Optimization | Built for Hackathon | Powered by Facebook Prophet & Streamlit")

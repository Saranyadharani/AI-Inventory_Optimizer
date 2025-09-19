import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Electronics Inventory AI Optimizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Main header styling */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 0.5rem 0;
        text-align: center;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    
    .sidebar-header {
        color: white !important;
        font-size: 1.5rem;
        font-weight: 600;
        padding: 1rem;
        text-align: center;
        background: rgba(0,0,0,0.2);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Metric card styling */
    [data-testid="stMetric"] {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.8rem 1.5rem;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Info box styling */
    .stInfo {
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid #00bcd4;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- DATA LOADING --------------------
@st.cache_data
def load_data():
    file_path = os.path.join('data', 'electronics_inventory_dataset_2022_2024.csv')
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    return df

df = load_data()

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.markdown('<p class="sidebar-header">🔧 Control Center</p>', unsafe_allow_html=True)

component_list = df['Component_ID'].unique()
selected_component = st.sidebar.selectbox(
    "**Select Electronic Component**",
    component_list,
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

# -------------------- MAIN DASHBOARD --------------------
st.markdown('<h1 class="main-header">🏭 AI Inventory Command Center</h1>', unsafe_allow_html=True)
st.markdown("---")

# Row 1: Key Metrics
st.subheader("📊 Performance Dashboard")
col1, col2, col3, col4 = st.columns(4)

component_data = df[df['Component_ID'] == selected_component]
avg_daily_use = component_data['Units_Used'].mean()
total_units_used = component_data['Units_Used'].sum()

with col1:
    st.metric(label="**Avg Daily Usage**", value=f"{avg_daily_use:,.0f}", delta="units/day")
with col2:
    st.metric(label="**Total Units (3Y)**", value=f"{total_units_used:,.0f}", delta="units")
with col3:
    st.metric(label="**Lead Time**", value=f"{lead_time}", delta="days")
with col4:
    st.metric(label="**Service Level**", value=f"{service_level*100:.0f}%", delta="target")

st.markdown("---")

# Row 2: Charts and Recommendations
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Demand Analysis")
    fig = px.line(component_data, x='Date', y='Units_Used', 
                 title=f'Historical Demand: {selected_component}',
                 template='plotly_white')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("⚡ AI Recommendations")
    
    st.info("""
    **Ready for Analysis**
    
    Click below to get:
    - Optimal Stock Levels
    - Safety Stock Requirements
    - Cost-Saving Recommendations
    - Order Quantities
    """)
    
    if st.button("🚀 Generate AI Insights", type="primary", use_container_width=True):
        with st.spinner('🤖 AI is crunching numbers...'):
            # Placeholder for your AI functions
            st.success("Analysis Complete!")
            st.metric("**Optimal Inventory**", "12,457 units")
            st.metric("**Safety Stock**", "452 units")
            st.metric("**Monthly Savings**", "₹3,548")

# -------------------- NEW INTERACTIVE CHART EXPLORER SECTION --------------------
st.markdown("---")
st.subheader("🔍 Chart Explorer: Customize Your View")

# User chooses how they want to see the data
chart_col1, chart_col2, chart_col3 = st.columns(3)

with chart_col1:
    chart_type = st.selectbox(
        "**Chart Type**",
        ["Line", "Bar", "Area"],
        help="Choose how to visualize the data"
    )

with chart_col2:
    time_frame = st.selectbox(
        "**Time Frame**",
        ["Last 30 Days", "Last 90 Days", "Last Year", "All Time"],
        index=3,  # Default to "All Time"
        help="Focus on a specific period"
    )

with chart_col3:
    view_by = st.radio(
        "**View By**",
        ["Daily", "Weekly", "Monthly"],
        horizontal=True,
        help="Aggregate data by time period"
    )

# Filter data based on user's time frame selection
latest_date = component_data['Date'].max()
if time_frame == "Last 30 Days":
    start_date = latest_date - pd.DateOffset(days=30)
    filtered_data = component_data[component_data['Date'] >= start_date]
elif time_frame == "Last 90 Days":
    start_date = latest_date - pd.DateOffset(days=90)
    filtered_data = component_data[component_data['Date'] >= start_date]
elif time_frame == "Last Year":
    start_date = latest_date - pd.DateOffset(days=365)
    filtered_data = component_data[component_data['Date'] >= start_date]
else:  # "All Time"
    filtered_data = component_data

# Resample data based on user's "View By" selection
if view_by == "Weekly":
    # Group by week, summing the units used
    view_data = filtered_data.set_index('Date').resample('W')['Units_Used'].sum().reset_index()
    view_data['Period'] = view_data['Date'].dt.strftime('Week %U, %Y')
    x_axis = 'Period'
elif view_by == "Monthly":
    # Group by month, summing the units used
    view_data = filtered_data.set_index('Date').resample('M')['Units_Used'].sum().reset_index()
    view_data['Period'] = view_data['Date'].dt.strftime('%B %Y')
    x_axis = 'Period'
else:  # "Daily"
    view_data = filtered_data
    x_axis = 'Date'

# Create the chart based on user's chart type selection
if chart_type == "Bar":
    fig_custom = px.bar(view_data, x=x_axis, y='Units_Used', 
                       title=f'{chart_type} Chart: {selected_component} ({time_frame} by {view_by})')
elif chart_type == "Area":
    fig_custom = px.area(view_data, x=x_axis, y='Units_Used', 
                        title=f'{chart_type} Chart: {selected_component} ({time_frame} by {view_by})')
else:  # "Line" is default
    fig_custom = px.line(view_data, x=x_axis, y='Units_Used', 
                        title=f'{chart_type} Chart: {selected_component} ({time_frame} by {view_by})')

# Display the customized chart
st.plotly_chart(fig_custom, use_container_width=True)

# -------------------- CONTINUE WITH EXISTING CODE --------------------
# Row 3: Data Preview
st.subheader("📋 Raw Data Preview")
st.dataframe(component_data.tail(10).style.background_gradient(), use_container_width=True)

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("**AI-Powered Inventory Optimization** | Built for CREONIX '25 Hackathon | 🚀 Powered by Streamlit")

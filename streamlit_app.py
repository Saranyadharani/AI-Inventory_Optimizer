# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import io
from calculations import *
from model import get_forecast

# Page config
st.set_page_config(
    page_title="AI Inventory Command Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FIXED CSS - Professional, high-contrast design
st.markdown("""
<style>
    /* DARK PROFESSIONAL BACKGROUND */
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%) !important;
    }
    
    /* MAIN CONTENT AREA - DARK CARD STYLE */
    .main .block-container {
        background: #1e1e1e !important;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid #333;
    }
    
    /* WHITE TEXT THROUGHOUT */
    .stApp * {
        color: #ffffff !important;
    }
    
    /* HEADERS - BOLD AND PROMINENT */
    h1, h2, h3 {
        font-weight: 800 !important;
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
        margin-bottom: 1rem !important;
    }
    
    /* MAIN HEADER - CENTERED WITH GRADIENT */
    .main-header {
        font-size: 3rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem !important;
    }
    
    /* METRICS - MODERN CARD DESIGN */
    [data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        color: #00ff88 !important;
        text-shadow: 0 2px 4px rgba(0,255,136,0.3) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #cccccc !important;
        opacity: 0.9;
    }
    
    /* METRIC CARDS - GLASS MORPHISM */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.05) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    /* SIDEBAR - DARK THEME */
    .stSidebar {
        background: linear-gradient(180deg, #0a0a0a 0%, #151515 100%) !important;
        border-right: 1px solid #333;
    }
    
    .stSidebar * {
        color: #ffffff !important;
    }
    
    .sidebar-header {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* INPUTS - MODERN DARK STYLE */
    .stSelectbox, .stSlider, .stTextInput, .stNumberInput {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
        color: white !important;
        padding: 8px 12px !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
    }
    
    /* BUTTONS - GRADIENT MODERN */
    .stButton > button {
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%) !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.8rem 1.5rem !important;
        margin: 0.5rem 0 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,255,136,0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(0,255,136,0.5) !important;
    }
    
    /* TABS - MODERN STYLING */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px !important;
        background: rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
        padding: 5px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        padding: 0.8rem 1.5rem !important;
        margin: 2px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%) !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* INFO BOXES - DARK THEME */
    .stInfo, .stSuccess, .stWarning, .stError {
        background: rgba(255,255,255,0.05) !important;
        border-left: 4px solid #00ff88 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
    }
    
    /* DATA FRAMES - DARK STYLE */
    .stDataFrame {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* SEPARATORS */
    hr {
        border-color: rgba(255,255,255,0.2) !important;
        margin: 2rem 0 !important;
    }
    
    /* SCROLLBAR STYLING */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Load data (rest of your code remains exactly the same)
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

def create_download_link(df, filename, file_type):
    """Generate download link for CSV or PDF"""
    if file_type == 'csv':
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    return href

historical_df, current_df = load_data()
if historical_df is None:
    st.stop()

# Sidebar - Control Center
st.sidebar.markdown('<div class="sidebar-header">🔧 Control Center</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

component = st.sidebar.selectbox(
    "**Select Electronic Component**",
    sorted(historical_df['Component_ID'].unique()),
    help="Choose which component to analyze"
)

lead_time = st.sidebar.slider(
    "**Supplier Lead Time (Days)**",
    min_value=7, max_value=90, value=30,
    help="Total time from order to delivery"
)

service_level = st.sidebar.slider(
    "**Target Service Level**",
    min_value=0.85, max_value=0.99, value=0.95,
    help="Probability of avoiding stockouts (0.95 = 95%)"
)

# Get component data
comp_data = historical_df[historical_df['Component_ID'] == component]
current_stock = current_df[current_df['Component_ID'] == component]['Current_Stock'].values[0]
unit_cost = current_df[current_df['Component_ID'] == component]['Unit_Cost'].values[0]
category = current_df[current_df['Component_ID'] == component]['Category'].values[0]

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**Component Details:**
- **Category**: {category}
- **Current Stock**: {current_stock:,} units
- **Unit Cost**: ₹{unit_cost:,.2f}
""")

# Main Dashboard
st.markdown('<h1 class="main-header">🏭 AI Inventory Command Center</h1>', unsafe_allow_html=True)
st.markdown("---")

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("**Current Stock**", f"{current_stock:,}", "units")

with col2:
    avg_daily = comp_data['Units_Used'].mean()
    st.metric("**Avg Daily Demand**", f"{avg_daily:,.0f}", "units/day")

with col3:
    st.metric("**Unit Cost**", f"₹{unit_cost:,.2f}", "per unit")

with col4:
    st.metric("**Service Level**", f"{service_level*100:.0f}%", "target")

st.markdown("---")

# Rest of your code remains exactly the same...
# Main Content
tab1, tab2, tab3, tab4 = st.tabs(["📈 Demand Analysis", "💰 Financial Dashboard", "📊 Portfolio Overview", "📋 Export Reports"])

with tab1:
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📊 Demand Forecast Analysis")
        
        # Interactive chart with customization
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            chart_type = st.selectbox("Chart Style", ["Line", "Area", "Bar"], key="chart_type")
        with chart_col2:
            time_frame = st.selectbox("Time Frame", ["Last 90 Days", "Last 180 Days", "Last Year", "All Time"], key="time_frame")
        
        # Filter data based on selection
        if time_frame == "Last 90 Days":
            chart_data = comp_data.tail(90)
        elif time_frame == "Last 180 Days":
            chart_data = comp_data.tail(180)
        elif time_frame == "Last Year":
            chart_data = comp_data[comp_data['Date'] >= comp_data['Date'].max() - pd.DateOffset(days=365)]
        else:
            chart_data = comp_data
        
        # Create chart based on selection
        if chart_type == "Line":
            fig = px.line(chart_data, x='Date', y='Units_Used', 
                         title=f'📈 {component} Demand Pattern ({time_frame})',
                         template='plotly_dark')
        elif chart_type == "Area":
            fig = px.area(chart_data, x='Date', y='Units_Used',
                         title=f'📊 {component} Demand Pattern ({time_frame})',
                         template='plotly_dark')
        else:
            fig = px.bar(chart_data, x='Date', y='Units_Used',
                        title=f'📋 {component} Demand Pattern ({time_frame})',
                        template='plotly_dark')
        
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("⚡ AI Recommendations")
        st.info(f"""
        **Ready to Analyze: {component}**
        
        - **Category**: {category}
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
                    
                    # Store results in session state for other tabs
                    st.session_state.results = {
                        'optimal_inventory': optimal_inventory,
                        'safety_stock': safety_stock,
                        'order_quantity': order_quantity,
                        'old_method_inventory': old_method_inventory,
                        'annual_savings': annual_savings,
                        'inventory_reduction': inventory_reduction,
                        'capital_released': capital_released
                    }
                    
                    st.success("🎯 AI Analysis Complete!")
                    
                except Exception as e:
                    st.error(f"❌ Error in AI analysis: {str(e)}")

        # Display results if available
        if 'results' in st.session_state:
            results = st.session_state.results
            st.markdown("---")
            st.subheader("📋 Optimization Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("**Optimal Inventory**", f"{results['optimal_inventory']:,}", 
                         f"vs old: {results['old_method_inventory']:,}")
            with col2:
                st.metric("**Safety Stock**", f"{results['safety_stock']:,}", 
                         f"{service_level*100:.0f}% service level")
            with col3:
                st.metric("**Order Quantity**", f"{results['order_quantity']:,}", 
                         "Recommended order")

with tab2:
    st.subheader("💰 Financial Impact Dashboard")
    
    if 'results' in st.session_state:
        results = st.session_state.results
        
        # Financial Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("**Inventory Reduction**", f"{results['inventory_reduction']:,}", "units")
        
        with col2:
            st.metric("**Capital Released**", f"₹{results['capital_released']:,}", "immediate benefit")
        
        with col3:
            st.metric("**Annual Savings**", f"₹{results['annual_savings']:,}", "20% holding cost")
        
        with col4:
            roi = (results['annual_savings'] / results['capital_released'] * 100) if results['capital_released'] > 0 else 0
            st.metric("**ROI**", f"{roi:.1f}%", "first year")
        
        # Financial Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Savings breakdown chart
            savings_data = pd.DataFrame({
                'Category': ['Annual Savings', 'Capital Released'],
                'Amount': [results['annual_savings'], results['capital_released']],
                'Type': ['Recurring', 'One-Time']
            })
            fig1 = px.bar(savings_data, x='Category', y='Amount', color='Type',
                         title='💵 Financial Impact Breakdown',
                         template='plotly_dark')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Inventory comparison chart
            inventory_data = pd.DataFrame({
                'Method': ['Old System', 'AI Optimized'],
                'Inventory': [results['old_method_inventory'], results['optimal_inventory']],
                'Type': ['Inefficient', 'Optimized']
            })
            fig2 = px.bar(inventory_data, x='Method', y='Inventory', color='Type',
                         title='📦 Inventory Level Comparison',
                         template='plotly_dark')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Priority Status
        st.markdown("---")
        if current_stock < results['safety_stock']:
            st.error("🚨 CRITICAL: Risk of imminent stockout! Order immediately.")
        elif current_stock < results['optimal_inventory']:
            st.warning("⚠️  WARNING: Stock levels below optimal. Monitor closely.")
        else:
            st.success("✅ HEALTHY: Stock levels are optimal or above.")
            
    else:
        st.info("👆 Generate AI insights first to see financial dashboard")

with tab3:
    st.subheader("📊 Portfolio Overview")
    
    # Portfolio Metrics
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
                 title='Inventory Distribution by Category',
                 template='plotly_dark')
    st.plotly_chart(fig1, use_container_width=True)
    
    # Cost analysis
    st.subheader("💵 Unit Cost Analysis")
    fig2 = px.bar(current_df, x='Component_ID', y='Unit_Cost', color='Category',
                 title='Unit Cost by Component (₹)',
                 template='plotly_dark')
    fig2.update_xaxes(tickangle=45)
    st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.subheader("📋 Export Reports")
    
    if 'results' in st.session_state:
        results = st.session_state.results
        
        # Purchase Recommendation Report
        st.markdown("### 📄 Purchase Recommendation Report")
        
        report_data = pd.DataFrame({
            'Parameter': [
                'Component ID', 'Analysis Date', 'Current Stock', 
                'Optimal Inventory Level', 'Safety Stock', 'Recommended Order Quantity',
                'Unit Cost', 'Total Order Value', 'Lead Time', 'Service Level',
                'Inventory Reduction', 'Capital Released', 'Annual Savings', 'ROI'
            ],
            'Value': [
                component, datetime.now().strftime('%Y-%m-%d'), current_stock,
                results['optimal_inventory'], results['safety_stock'], results['order_quantity'],
                unit_cost, results['order_quantity'] * unit_cost, lead_time, f"{service_level*100}%",
                results['inventory_reduction'], results['capital_released'], 
                results['annual_savings'], f"{(results['annual_savings']/results['capital_released']*100):.1f}%" if results['capital_released'] > 0 else "N/A"
            ]
        })
        
        st.dataframe(report_data, use_container_width=True)
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(create_download_link(report_data, f"purchase_recommendation_{component}.csv", "csv"), unsafe_allow_html=True)
        
        with col2:
            # Generate comprehensive report
            comprehensive_report = pd.DataFrame({
                'Component': [component],
                'Current_Stock': [current_stock],
                'Optimal_Inventory': [results['optimal_inventory']],
                'Safety_Stock': [results['safety_stock']],
                'Order_Quantity': [results['order_quantity']],
                'Unit_Cost': [unit_cost],
                'Total_Order_Value': [results['order_quantity'] * unit_cost],
                'Inventory_Reduction': [results['inventory_reduction']],
                'Capital_Released': [results['capital_released']],
                'Annual_Savings': [results['annual_savings']],
                'ROI_Percentage': [results['annual_savings']/results['capital_released']*100 if results['capital_released'] > 0 else 0],
                'Lead_Time_Days': [lead_time],
                'Service_Level': [service_level],
                'Analysis_Date': [datetime.now().strftime('%Y-%m-%d')]
            })
            st.markdown(create_download_link(comprehensive_report, f"comprehensive_report_{component}.csv", "csv"), unsafe_allow_html=True)
    else:
        st.info("👆 Generate AI insights first to export reports")

# Run the app
if __name__ == "__main__":
    pass

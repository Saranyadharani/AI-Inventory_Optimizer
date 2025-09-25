# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
from calculations import *
from model import get_forecast

# Page config
st.set_page_config(
    page_title="AI Inventory Command Center",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for BOLD, CLEAN, PROFESSIONAL look
st.markdown("""
<style>
    /* MAIN HEADERS - BIG, BOLD, CLEAN */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* SECTION HEADERS - BOLD AND CLEAR */
    .section-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #2c3e50;
        border-bottom: 4px solid #667eea;
        padding-bottom: 1rem;
        margin-bottom: 2rem;
        text-transform: uppercase;
    }
    
    /* METRIC CARDS - CLEAN AND PROFESSIONAL */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        border: 3px solid #e0e6ed;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        margin-bottom: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    /* BUTTONS - BOLD AND MODERN */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 15px 30px;
        font-weight: 800;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* SIDEBAR - CLEAN AND ORGANIZED */
    .sidebar-section {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #e0e6ed;
    }
    
    /* STATUS BOXES - BOLD AND CLEAR */
    .status-healthy {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 3px solid #28a745;
        border-radius: 15px;
        padding: 2rem;
        font-weight: 700;
        font-size: 1.3rem;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 3px solid #ffc107;
        border-radius: 15px;
        padding: 2rem;
        font-weight: 700;
        font-size: 1.3rem;
    }
    
    .status-critical {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 3px solid #dc3545;
        border-radius: 15px;
        padding: 2rem;
        font-weight: 700;
        font-size: 1.3rem;
    }
    
    /* BOLD FONT THROUGHOUT */
    body {
        font-weight: 600 !important;
    }
    
    /* CHART CONTAINERS */
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e0e6ed;
        margin-bottom: 2rem;
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
        st.error("❌ DATA FILES NOT FOUND! Please run: python create_pro_dataset.py")
        return None, None

def create_download_link(df, filename):
    """Generate download link for CSV"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="font-weight: 800; font-size: 1.2rem;">📥 DOWNLOAD {filename}</a>'
    return href

# Load data
historical_df, current_df = load_data()
if historical_df is None:
    st.stop()

# Sidebar - Persistent across all pages
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
st.sidebar.markdown('## 🔧 **CONTROL CENTER**')
st.sidebar.markdown("---")

component = st.sidebar.selectbox(
    "**SELECT ELECTRONIC COMPONENT**",
    sorted(historical_df['Component_ID'].unique())
)

lead_time = st.sidebar.slider(
    "**SUPPLIER LEAD TIME (DAYS)**",
    min_value=7, max_value=90, value=30
)

service_level = st.sidebar.slider(
    "**TARGET SERVICE LEVEL**",
    min_value=0.85, max_value=0.99, value=0.95
)

# Get component data
comp_data = historical_df[historical_df['Component_ID'] == component]
current_stock = current_df[current_df['Component_ID'] == component]['Current_Stock'].values[0]
unit_cost = current_df[current_df['Component_ID'] == component]['Unit_Cost'].values[0]
category = current_df[current_df['Component_ID'] == component]['Category'].values[0]

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**COMPONENT DETAILS:**
- **CATEGORY**: {category}
- **CURRENT STOCK**: {current_stock:,} units
- **UNIT COST**: ₹{unit_cost:,.2f}
""")

# AI Analysis Button
if st.sidebar.button("🚀 **GENERATE AI INSIGHTS**", type="primary"):
    with st.spinner('🤖 AI IS ANALYZING DEMAND PATTERNS...'):
        try:
            forecast = get_forecast(comp_data, periods=lead_time + 60)
            historical_demand = comp_data['Units_Used'].values
            safety_stock = calculate_safety_stock(historical_demand, lead_time, service_level)
            optimal_inventory = calculate_optimal_inventory(forecast, lead_time, safety_stock)
            order_quantity = calculate_order_quantity(optimal_inventory, current_stock)
            old_method_inventory = estimate_old_method_inventory(historical_demand)
            annual_savings, inventory_reduction, capital_released = calculate_cost_savings(
                optimal_inventory, old_method_inventory, unit_cost
            )
            
            st.session_state.results = {
                'optimal_inventory': optimal_inventory,
                'safety_stock': safety_stock,
                'order_quantity': order_quantity,
                'old_method_inventory': old_method_inventory,
                'annual_savings': annual_savings,
                'inventory_reduction': inventory_reduction,
                'capital_released': capital_released
            }
            st.session_state.analysis_done = True
        except Exception as e:
            st.error(f"❌ ERROR IN AI ANALYSIS: {str(e)}")

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Multi-page navigation
page = st.sidebar.radio("**NAVIGATION**", 
    ["📊 **DASHBOARD OVERVIEW**", "📈 **DEMAND ANALYSIS**", "💰 **FINANCIAL PERFORMANCE**", 
     "🏭 **PORTFOLIO REVIEW**", "📋 **EXPORT REPORTS**"], 
    index=0)

# PAGE 1: DASHBOARD OVERVIEW
if page == "📊 **DASHBOARD OVERVIEW**":
    st.markdown('<h1 class="main-header">🏭 AI INVENTORY COMMAND CENTER</h1>', unsafe_allow_html=True)
    
    # Key Metrics Row - BIG AND BOLD
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("**CURRENT STOCK**", f"{current_stock:,}", "UNITS", delta_color="off")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_daily = comp_data['Units_Used'].mean()
        st.metric("**AVG DAILY DEMAND**", f"{avg_daily:,.0f}", "UNITS/DAY", delta_color="off")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("**UNIT COST**", f"₹{unit_cost:,.2f}", "PER UNIT", delta_color="off")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("**SERVICE LEVEL**", f"{service_level*100:.0f}%", "TARGET", delta_color="off")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # AI Results Section
    if 'results' in st.session_state:
        results = st.session_state.results
        
        st.markdown('<div class="section-header">🎯 AI OPTIMIZATION RESULTS</div>', unsafe_allow_html=True)
        
        # Optimization Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("**OPTIMAL INVENTORY**", f"{results['optimal_inventory']:,}", 
                     f"VS OLD: {results['old_method_inventory']:,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("**SAFETY STOCK**", f"{results['safety_stock']:,}", 
                     f"{service_level*100:.0f}% SERVICE LEVEL")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("**ORDER QUANTITY**", f"{results['order_quantity']:,}", "RECOMMENDED ORDER")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Status Box
        if current_stock < results['safety_stock']:
            st.markdown('<div class="status-critical">🚨 CRITICAL: RISK OF IMMINENT STOCKOUT! ORDER IMMEDIATELY.</div>', unsafe_allow_html=True)
        elif current_stock < results['optimal_inventory']:
            st.markdown('<div class="status-warning">⚠️ WARNING: STOCK LEVELS BELOW OPTIMAL. MONITOR CLOSELY.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-healthy">✅ HEALTHY: STOCK LEVELS ARE OPTIMAL OR ABOVE.</div>', unsafe_allow_html=True)
    
    else:
        st.markdown('<div class="section-header">🚀 GET STARTED</div>', unsafe_allow_html=True)
        st.info("**CLICK 'GENERATE AI INSIGHTS' IN THE SIDEBAR TO BEGIN ANALYSIS**")

# PAGE 2: DEMAND ANALYSIS
elif page == "📈 **DEMAND ANALYSIS**":
    st.markdown('<h1 class="main-header">📈 DEMAND ANALYSIS</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-header">📊 DEMAND FORECAST ANALYSIS</div>', unsafe_allow_html=True)
        
        # Chart customization
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            chart_type = st.selectbox("**CHART STYLE**", ["Line", "Area", "Bar"])
        with chart_col2:
            time_frame = st.selectbox("**TIME FRAME**", ["Last 90 Days", "Last 180 Days", "Last Year", "All Time"])
        
        # Filter data
        if time_frame == "Last 90 Days": chart_data = comp_data.tail(90)
        elif time_frame == "Last 180 Days": chart_data = comp_data.tail(180)
        elif time_frame == "Last Year": chart_data = comp_data[comp_data['Date'] >= comp_data['Date'].max() - pd.DateOffset(days=365)]
        else: chart_data = comp_data
        
        # Create chart
        if chart_type == "Line":
            fig = px.line(chart_data, x='Date', y='Units_Used', template='plotly_white')
        elif chart_type == "Area":
            fig = px.area(chart_data, x='Date', y='Units_Used', template='plotly_white')
        else:
            fig = px.bar(chart_data, x='Date', y='Units_Used', template='plotly_white')
        
        fig.update_layout(
            height=600,
            title=f"**{component} - {time_frame} Demand Pattern**",
            title_font_size=20,
            title_font_weight="bold"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header">📈 QUICK STATS</div>', unsafe_allow_html=True)
        
        stats_data = {
            'Statistic': ['Max Daily Demand', 'Min Daily Demand', 'Average Demand', 'Demand Volatility', 'Trend'],
            'Value': [
                f"{comp_data['Units_Used'].max():,}",
                f"{comp_data['Units_Used'].min():,}",
                f"{comp_data['Units_Used'].mean():.0f}",
                f"{comp_data['Units_Used'].std():.0f}",
                '📈 Growing' if comp_data['Units_Used'].iloc[-30:].mean() > comp_data['Units_Used'].iloc[:30].mean() else '📉 Declining'
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

# PAGE 3: FINANCIAL PERFORMANCE
elif page == "💰 **FINANCIAL PERFORMANCE**":
    st.markdown('<h1 class="main-header">💰 FINANCIAL PERFORMANCE</h1>', unsafe_allow_html=True)
    
    if 'results' in st.session_state:
        results = st.session_state.results
        
        # Financial Metrics - BIG AND BOLD
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("**INVENTORY REDUCTION**", f"{results['inventory_reduction']:,}", "UNITS")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("**CAPITAL RELEASED**", f"₹{results['capital_released']:,}", "IMMEDIATE BENEFIT")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("**ANNUAL SAVINGS**", f"₹{results['annual_savings']:,}", "20% HOLDING COST")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            roi = (results['annual_savings'] / results['capital_released'] * 100) if results['capital_released'] > 0 else 0
            st.metric("**ROI**", f"{roi:.1f}%", "FIRST YEAR")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Financial Visualizations
        st.markdown('<div class="section-header">📊 FINANCIAL ANALYTICS</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            savings_data = pd.DataFrame({
                'Category': ['Annual Savings', 'Capital Released'],
                'Amount': [results['annual_savings'], results['capital_released']]
            })
            fig1 = px.bar(savings_data, x='Category', y='Amount', 
                         title='**💵 FINANCIAL IMPACT BREAKDOWN**',
                         template='plotly_white')
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            inventory_data = pd.DataFrame({
                'Method': ['Old System', 'AI Optimized'],
                'Inventory': [results['old_method_inventory'], results['optimal_inventory']]
            })
            fig2 = px.bar(inventory_data, x='Method', y='Inventory', 
                         title='**📦 INVENTORY LEVEL COMPARISON**',
                         template='plotly_white')
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.info("**GENERATE AI INSIGHTS FIRST TO VIEW FINANCIAL PERFORMANCE**")

# PAGE 4: PORTFOLIO REVIEW
elif page == "🏭 **PORTFOLIO REVIEW**":
    st.markdown('<h1 class="main-header">🏭 PORTFOLIO REVIEW</h1>', unsafe_allow_html=True)
    
    # Portfolio Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        total_components = len(current_df)
        st.metric("**TOTAL COMPONENTS**", f"{total_components}", "PRODUCTS")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        total_inventory_value = (current_df['Current_Stock'] * current_df['Unit_Cost']).sum()
        st.metric("**TOTAL INVENTORY VALUE**", f"₹{total_inventory_value:,.0f}", "TOTAL VALUE")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        total_categories = current_df['Category'].nunique()
        st.metric("**PRODUCT CATEGORIES**", f"{total_categories}", "CATEGORIES")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Visualizations
    st.markdown('<div class="section-header">📊 PORTFOLIO ANALYTICS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig1 = px.pie(current_df, values='Current_Stock', names='Category', 
                     title='**📦 INVENTORY DISTRIBUTION BY CATEGORY**',
                     template='plotly_white')
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig2 = px.bar(current_df, x='Component_ID', y='Unit_Cost', color='Category',
                     title='**💵 UNIT COST BY COMPONENT**',
                     template='plotly_white')
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# PAGE 5: EXPORT REPORTS
elif page == "📋 **EXPORT REPORTS**":
    st.markdown('<h1 class="main-header">📋 EXPORT REPORTS</h1>', unsafe_allow_html=True)
    
    if 'results' in st.session_state:
        results = st.session_state.results
        
        st.markdown('<div class="section-header">📄 PURCHASE RECOMMENDATION REPORT</div>', unsafe_allow_html=True)
        
        # Comprehensive Report
        report_data = pd.DataFrame({
            'PARAMETER': [
                'COMPONENT ID', 'ANALYSIS DATE', 'CURRENT STOCK', 
                'OPTIMAL INVENTORY LEVEL', 'SAFETY STOCK', 'RECOMMENDED ORDER QUANTITY',
                'UNIT COST', 'TOTAL ORDER VALUE', 'LEAD TIME', 'SERVICE LEVEL',
                'INVENTORY REDUCTION', 'CAPITAL RELEASED', 'ANNUAL SAVINGS', 'ROI'
            ],
            'VALUE': [
                component, datetime.now().strftime('%Y-%m-%d'), f"{current_stock:,}",
                f"{results['optimal_inventory']:,}", f"{results['safety_stock']:,}", f"{results['order_quantity']:,}",
                f"₹{unit_cost:,.2f}", f"₹{results['order_quantity'] * unit_cost:,}", f"{lead_time} days", f"{service_level*100}%",
                f"{results['inventory_reduction']:,}", f"₹{results['capital_released']:,}", 
                f"₹{results['annual_savings']:,}", f"{(results['annual_savings']/results['capital_released']*100):.1f}%" if results['capital_released'] > 0 else "N/A"
            ]
        })
        
        st.dataframe(report_data, use_container_width=True)
        
        # Download Section
        st.markdown('<div class="section-header">📥 DOWNLOAD REPORTS</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(create_download_link(report_data, f"PURCHASE_RECOMMENDATION_{component}.csv"), unsafe_allow_html=True)
        
        with col2:
            comprehensive_report = pd.DataFrame({
                'COMPONENT': [component],
                'CURRENT_STOCK': [current_stock],
                'OPTIMAL_INVENTORY': [results['optimal_inventory']],
                'SAFETY_STOCK': [results['safety_stock']],
                'ORDER_QUANTITY': [results['order_quantity']],
                'UNIT_COST': [unit_cost],
                'TOTAL_ORDER_VALUE': [results['order_quantity'] * unit_cost],
                'INVENTORY_REDUCTION': [results['inventory_reduction']],
                'CAPITAL_RELEASED': [results['capital_released']],
                'ANNUAL_SAVINGS': [results['annual_savings']],
                'ROI_PERCENTAGE': [results['annual_savings']/results['capital_released']*100 if results['capital_released'] > 0 else 0],
                'LEAD_TIME_DAYS': [lead_time],
                'SERVICE_LEVEL': [service_level],
                'ANALYSIS_DATE': [datetime.now().strftime('%Y-%m-%d')]
            })
            st.markdown(create_download_link(comprehensive_report, f"COMPREHENSIVE_REPORT_{component}.csv"), unsafe_allow_html=True)
    
    else:
        st.info("**GENERATE AI INSIGHTS FIRST TO EXPORT REPORTS**")

# Footer
st.markdown("---")


if __name__ == "__main__":
    pass

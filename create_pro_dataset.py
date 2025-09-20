# Add this section to your existing streamlit_app.py

# After your main analysis, add these visualizations:

# Show component categories
st.subheader("📊 Component Categories Analysis")
category_summary = current_df.groupby('Category').agg({
    'Component_ID': 'count',
    'Current_Stock': 'sum',
    'Unit_Cost': 'mean'
}).rename(columns={'Component_ID': 'Count', 'Unit_Cost': 'Avg_Cost'})

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Components", len(current_df))
with col2:
    st.metric("Total Inventory Value", f"₹{current_df['Current_Stock'].dot(current_df['Unit_Cost']):,.0f}")
with col3:
    st.metric("Categories", len(category_summary))

# Show inventory value by category
fig1 = px.pie(current_df, values='Current_Stock', names='Category', 
             title='Inventory Distribution by Category')
st.plotly_chart(fig1, use_container_width=True)

# Show cost analysis
fig2 = px.bar(current_df, x='Component_ID', y='Unit_Cost', color='Category',
             title='Unit Cost by Component (₹)')
st.plotly_chart(fig2, use_container_width=True)

# Show potential savings across all components
if st.button("💎 Calculate Total Portfolio Savings", type="secondary"):
    with st.spinner("Analyzing entire inventory portfolio..."):
        total_annual_savings = 0
        total_capital_released = 0
        
        for comp_id in current_df['Component_ID']:
            comp_data = historical_df[historical_df['Component_ID'] == comp_id]
            current_stock = current_df[current_df['Component_ID'] == comp_id]['Current_Stock'].values[0]
            unit_cost = current_df[current_df['Component_ID'] == comp_id]['Unit_Cost'].values[0]
            
            forecast = get_forecast(comp_data, periods=lead_time + 30)
            demand_data = comp_data['Units_Used'].values
            safety_stock = calculate_safety_stock(demand_data, lead_time, service_level)
            optimal_inv = calculate_optimal_inventory(forecast, lead_time, safety_stock)
            old_inv = get_old_method_inventory(comp_data['Units_Used'].mean())
            annual_savings, reduction = calculate_savings(optimal_inv, old_inv, unit_cost)
            
            total_annual_savings += annual_savings
            total_capital_released += reduction * unit_cost
        
        st.success(f"🎯 **Portfolio-Wide Impact**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Annual Savings", f"₹{total_annual_savings:,.0f}")
        with col2:
            st.metric("Capital Released", f"₹{total_capital_released:,.0f}")

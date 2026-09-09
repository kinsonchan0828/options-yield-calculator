import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Options Yield Calculator",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Options Short Put & Wheel Strategy Yield Calculator")
st.caption("Calculate annualized returns, breakeven thresholds, downside buffers, and full-cycle wheel strategy yields.")

st.divider()

# Input Section
st.subheader("1. Trade Input Parameters")
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    current_price = st.number_input("Current Stock Price ($)", value=100.0, step=0.5, min_value=0.01)
    contract_count = st.number_input("Number of Contracts", value=1, step=1, min_value=1)

with col_in2:
    strike_price = st.number_input("Short Put Strike Price ($)", value=95.0, step=0.5, min_value=0.01)
    dte = st.number_input("Days to Expiration (DTE)", value=30, step=1, min_value=1)

with col_in3:
    premium = st.number_input("Option Premium Collected ($/share)", value=2.0, step=0.05, min_value=0.01)

# Core Metric Calculations
collateral = strike_price * 100 * contract_count
total_cash = premium * 100 * contract_count
raw_roc = (premium / strike_price) * 100
aroc = raw_roc * (365 / dte)
breakeven = strike_price - premium
downside_buffer = ((current_price - breakeven) / current_price) * 100

# Automated Trade Health Badge
st.divider()
st.subheader("2. Trade Health & Primary Metrics")

if aroc >= 15 and downside_buffer >= 5:
    st.success("🟢 **High-Quality Setup:** Meets benchmark criteria (>15% Annualized Yield & >5% Downside Buffer).")
elif aroc >= 10 and downside_buffer >= 2:
    st.warning("🟡 **Moderate Setup:** Acceptable yield, but monitor downside risk and stock volatility.")
else:
    st.error("🔴 **Low Buffer / Low Yield Setup:** Yield does not adequately compensate for downside assignment risk.")

# Headline KPI Display
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Annualized Return (AROC)", f"{aroc:.2f}%", f"Raw: {raw_roc:.2f}%")
kpi2.metric("Breakeven Price", f"${breakeven:.2f}")
kpi3.metric("Downside Safety Buffer", f"{downside_buffer:.2f}%")
kpi4.metric("Required Cash Collateral", f"${collateral:,.2f}")

# Secondary & Early Closure Metrics
with st.expander("📊 View Detailed Cash Flow & 50% Profit Rule Target"):
    sec1, sec2, sec3 = st.columns(3)
    sec1.metric("Total Upfront Premium Income", f"${total_cash:,.2f}")
    sec2.metric("50% Max Profit Target (Close Trade)", f"${total_cash / 2:,.2f}")
    sec3.metric("Effective Stock Cost Basis if Assigned", f"${breakeven:.2f}")

# Wheel Strategy Extension
st.divider()
st.subheader("3. Wheel Strategy Phase 2 (Covered Call Toggle)")
enable_wheel = st.checkbox("Enable Covered Call Cycle Modeling (If Put is Assigned)")

if enable_wheel:
    st.info("Model the second half of the Wheel Strategy: selling a Covered Call after put assignment.")
    cc_col1, cc_col2 = st.columns(2)
    
    with cc_col1:
        cc_strike = st.number_input("Covered Call Strike Price ($)", value=100.0, step=0.5, min_value=0.01)
        cc_dte = st.number_input("Covered Call DTE", value=30, step=1, min_value=1)
        
    with cc_col2:
        cc_premium = st.number_input("Covered Call Premium Received ($/share)", value=2.5, step=0.05, min_value=0.01)
    
    total_days = dte + cc_dte
    full_cycle_profit = ((cc_strike - breakeven) + cc_premium) * 100 * contract_count
    full_cycle_roc = (full_cycle_profit / collateral) * 100
    full_cycle_aroc = full_cycle_roc * (365 / total_days)
    
    wc1, wc2, wc3 = st.columns(3)
    wc1.metric("Full Cycle Total Net Profit", f"${full_cycle_profit:,.2f}")
    wc2.metric("Full Cycle Return on Capital", f"{full_cycle_roc:.2f}%")
    wc3.metric("Full Cycle Annualized Return", f"{full_cycle_aroc:.2f}%")

# Expiration Payoff Visualizer
st.divider()
st.subheader("4. Expiration P&L Payoff Diagram")

price_range = np.linspace(current_price * 0.7, current_price * 1.3, 150)
pnl_values = np.where(
    price_range < strike_price,
    (price_range - breakeven) * 100 * contract_count,
    total_cash
)

fig = go.Figure()

# P&L Line
fig.add_trace(go.Scatter(
    x=price_range, 
    y=pnl_values, 
    mode='lines', 
    name='P&L at Expiration', 
    line=dict(color='#00CC96', width=3)
))

# Zero Line
fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)

# Key Reference Lines
fig.add_vline(x=current_price, line_dash="dot", line_color="#636EFA", annotation_text="Current Price", annotation_position="top left")
fig.add_vline(x=strike_price, line_dash="dot", line_color="#FFA15A", annotation_text="Short Put Strike", annotation_position="top right")
fig.add_vline(x=breakeven, line_dash="dot", line_color="#EF553B", annotation_text="Breakeven", annotation_position="bottom left")

fig.update_layout(
    title="Net Profit / Loss ($) vs. Underlying Stock Price at Expiration",
    xaxis_title="Stock Price at Expiration ($)",
    yaxis_title="Total Profit / Loss ($)",
    template="plotly_dark",
    height=450,
    margin=dict(l=20, r=20, t=50, b=20)
)

st.plotly_chart(fig, use_container_width=True)

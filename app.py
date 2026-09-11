import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Short Put Option Calculator", page_icon="📉", layout="wide"
)

st.title("📉 Short Put Option Strategy Calculator (Baseline)")
st.markdown(
    "Interactive payoff analysis and return profile for cash-secured short put options."
)

# ---------------------------------------------------------
# Sidebar Inputs
# ---------------------------------------------------------
st.sidebar.header("Trade Inputs")

stock_price = st.sidebar.number_input(
    "Current Stock Price ($)",
    min_value=0.01,
    value=100.00,
    step=1.00,
    format="%.2f",
)

strike_price = st.sidebar.number_input(
    "Strike Price ($)",
    min_value=0.01,
    value=95.00,
    step=1.00,
    format="%.2f",
)

premium = st.sidebar.number_input(
    "Option Premium Received ($/share)",
    min_value=0.01,
    value=2.50,
    step=0.10,
    format="%.2f",
)

dte = st.sidebar.number_input(
    "Days to Expiration (DTE)", min_value=1, value=30, step=1
)

num_contracts = st.sidebar.number_input(
    "Number of Contracts", min_value=1, value=1, step=1
)

# ---------------------------------------------------------
# Financial Calculations
# ---------------------------------------------------------
breakeven = strike_price - premium
max_profit = premium * 100 * num_contracts
cash_collateral = strike_price * 100 * num_contracts
max_risk_net = (strike_price - premium) * 100 * num_contracts

roc = (max_profit / cash_collateral) * 100 if cash_collateral > 0 else 0.0
annualized_roc = roc * (365 / dte) if dte > 0 else 0.0

# ---------------------------------------------------------
# Top KPI Metric Cards
# ---------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Max Profit", f"${max_profit:,.2f}")
col2.metric("Breakeven Price", f"${breakeven:,.2f}")
col3.metric("Required Collateral", f"${cash_collateral:,.2f}")
col4.metric("Return on Collateral (ROC)", f"{roc:.2f}%")
col5.metric("Annualized ROC", f"{annualized_roc:.2f}%")

st.markdown("---")

# ---------------------------------------------------------
# Payoff Diagram (Plotly)
# ---------------------------------------------------------
s_min = max(0.0, min(stock_price, strike_price) * 0.7)
s_max = max(stock_price, strike_price) * 1.3
s_range = np.linspace(s_min, s_max, 500)

payoff_per_share = np.minimum(s_range - strike_price, 0) + premium
total_payoff = payoff_per_share * 100 * num_contracts

fig = go.Figure()

# Main Payoff Curve
fig.add_trace(
    go.Scatter(
        x=s_range,
        y=total_payoff,
        mode="lines",
        name="Payoff at Expiration",
        line=dict(color="#1f77b4", width=3),
        hovertemplate="Stock Price: %{x:$.2f}<br>P/L: %{y:$.2f}<extra></extra>",
    )
)

# Zero Line
fig.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.5)

# Reference Lines
fig.add_vline(
    x=stock_price,
    line_dash="dot",
    line_color="#2b5c8f",
    annotation_text=f"Stock Price: ${stock_price:.2f}",
    annotation_position="top left",
)

fig.add_vline(
    x=strike_price,
    line_dash="dash",
    line_color="#d9534f",
    annotation_text=f"Strike: ${strike_price:.2f}",
    annotation_position="bottom right",
)

fig.add_vline(
    x=breakeven,
    line_dash="dash",
    line_color="#5cb85c",
    annotation_text=f"Breakeven: ${breakeven:.2f}",
    annotation_position="bottom left",
)

fig.update_layout(
    title="Short Put Payoff Curve at Expiration",
    xaxis_title="Underlying Stock Price ($)",
    yaxis_title="Profit / Loss ($)",
    hovermode="x unified",
    template="plotly_white",
    height=520,
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# Summary Table
# ---------------------------------------------------------
st.markdown("### 📊 Trade Summary & Risk Breakdown")

summary_df = pd.DataFrame(
    {
        "Parameter / Metric": [
            "Current Stock Price",
            "Strike Price",
            "Premium Received (per share)",
            "Days to Expiration (DTE)",
            "Contracts Traded",
            "Breakeven Price",
            "Maximum Profit Potential",
            "Max Loss Potential (Assumes Stock to $0)",
            "Total Cash Collateral Reserved",
            "Return on Collateral (ROC)",
            "Annualized Return on Collateral (Annualized ROC)",
        ],
        "Value": [
            f"${stock_price:.2f}",
            f"${strike_price:.2f}",
            f"${premium:.2f}",
            f"{dte} days",
            f"{num_contracts}",
            f"${breakeven:.2f}",
            f"${max_profit:,.2f}",
            f"${max_risk_net:,.2f}",
            f"${cash_collateral:,.2f}",
            f"{roc:.2f}%",
            f"{annualized_roc:.2f}%",
        ],
    }
)

st.table(summary_df)

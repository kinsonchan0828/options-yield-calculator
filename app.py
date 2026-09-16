import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf

# Page Configuration
st.set_page_config(
    page_title="Options Yield & Income Calculator", page_icon="📈", layout="wide"
)


# Helper function to search Yahoo Finance for tickers
def search_yahoo_finance(query: str):
    if not query or len(query.strip()) == 0:
        return []
    url = f"https://query2.finance.yahoo.com/1/finance/search?q={query}&quotesCount=5"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code == 200:
            data = res.json()
            matches = []
            for item in data.get("quotes", []):
                if item.get("quoteType") in ["EQUITY", "ETF"]:
                    symbol = item.get("symbol")
                    name = item.get("shortname") or item.get("longname") or symbol
                    exchange = item.get("exchDisp") or ""
                    matches.append((f"{symbol} - {name} ({exchange})", symbol))
            return matches
    except Exception:
        pass
    return []


st.title("📈 Options Yield & Income Calculator (Pro)")
st.caption(
    "Calculate gross vs. net annualized returns, live stock prices, commission drag, and export trade logs."
)

st.divider()

# Sidebar: Inputs & Controls
st.sidebar.header("1. Stock Search & Live Data")
search_query = st.sidebar.text_input(
    "Search Company or Ticker:",
    value="NVDA",
    help="Type name (e.g. Tencent, Apple) or ticker (e.g. AAPL, 700, TSLA)",
)

search_results = search_yahoo_finance(search_query)

if search_results:
    selected_label = st.sidebar.selectbox(
        "Select Matching Asset:", [r[0] for r in search_results]
    )
    selected_symbol = dict(search_results)[selected_label]
else:
    selected_symbol = search_query.strip().upper()

# Fetch live stock price
live_price = 100.0
if selected_symbol:
    try:
        ticker_obj = yf.Ticker(selected_symbol)
        price_val = ticker_obj.fast_info.get(
            "lastPrice"
        ) or ticker_obj.fast_info.get("previousClose")
        if price_val and not np.isnan(price_val):
            live_price = float(price_val)
    except Exception:
        pass

current_price = st.sidebar.number_input(
    "Stock Price ($) [Auto-Fetched / Editable]",
    value=round(live_price, 2),
    step=0.5,
    min_value=0.01,
)

st.sidebar.divider()
st.sidebar.header("2. Option Contract Details")
strike_price = st.sidebar.number_input(
    "Short Put Strike Price ($)",
    value=round(current_price * 0.95, 2),
    step=0.5,
    min_value=0.01,
)
premium = st.sidebar.number_input(
    "Option Premium Collected ($/share)", value=2.50, step=0.05, min_value=0.01
)
dte = st.sidebar.number_input(
    "Days to Expiration (DTE)", value=30, step=1, min_value=1
)
contract_count = st.sidebar.number_input(
    "Number of Contracts", value=1, step=1, min_value=1
)

st.sidebar.divider()
st.sidebar.header("3. Broker Commission Deductions")
comm_per_contract = st.sidebar.number_input(
    "Commission per Contract ($)",
    value=0.65,
    step=0.05,
    min_value=0.00,
    help="Standard options fee (e.g. $0.65 for IBKR/Webull)",
)
flat_ticket_fee = st.sidebar.number_input(
    "Flat Base Fee per Trade ($)",
    value=0.00,
    step=0.50,
    min_value=0.00,
    help="Optional ticket fee charged per order",
)

# Core Financial Calculations
# Assuming round-trip (entry + exit/expiration fee)
total_commissions = (
    comm_per_contract * contract_count * 2
) + flat_ticket_fee
collateral = strike_price * 100 * contract_count

gross_income = premium * 100 * contract_count
net_income = gross_income - total_commissions

gross_roc = (premium / strike_price) * 100
net_roc = (net_income / collateral) * 100 if collateral > 0 else 0

gross_aroc = gross_roc * (365 / dte)
net_aroc = net_roc * (365 / dte)

gross_breakeven = strike_price - premium
net_breakeven = strike_price - (net_income / (100 * contract_count))
downside_buffer = ((current_price - net_breakeven) / current_price) * 100

# Top KPI Metric Cards: Gross vs Net Comparison
st.subheader("1. Trade Health & Return Profile")

if net_aroc >= 15 and downside_buffer >= 5:
    st.success(
        "🟢 **High-Quality Setup:** Net yield exceeds 15% AROC with >5% downside buffer after fees."
    )
elif net_aroc >= 10 and downside_buffer >= 2:
    st.warning(
        "🟡 **Moderate Setup:** Acceptable yield, but commission drag or buffer warrants monitoring."
    )
else:
    st.error(
        "🔴 **Low Buffer / Low Yield:** Return after commissions does not compensate for assignment risk."
    )

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(
    "Net Annualized Return (AROC)",
    f"{net_aroc:.2f}%",
    f"Gross: {gross_aroc:.2f}%",
)
kpi2.metric(
    "Net Breakeven Price",
    f"${net_breakeven:.2f}",
    f"Gross: ${gross_breakeven:.2f}",
)
kpi3.metric("Downside Safety Buffer", f"{downside_buffer:.2f}%")
kpi4.metric(
    "Total Fees & Commissions",
    f"${total_commissions:.2f}",
    f"${comm_per_contract}/contract",
)

st.divider()

# Detailed Breakdown & Payoff Curve
st.subheader("2. Net Payoff Curve at Expiration")

price_range = np.linspace(
    max(0.01, current_price * 0.7), current_price * 1.3, 200
)
net_pnl_values = (
    np.where(
        price_range < strike_price,
        (price_range - strike_price) * 100 * contract_count + gross_income,
        gross_income,
    )
    - total_commissions
)

fig = go.Figure()

# Net P&L Line
fig.add_trace(
    go.Scatter(
        x=price_range,
        y=net_pnl_values,
        mode="lines",
        name="Net P&L (After Fees)",
        line=dict(color="#00CC96", width=3),
    )
)

# Reference Lines
fig.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.5)
fig.add_vline(
    x=current_price,
    line_dash="dot",
    line_color="#636EFA",
    annotation_text=f"Current: ${current_price:.2f}",
    annotation_position="top left",
)
fig.add_vline(
    x=strike_price,
    line_dash="dot",
    line_color="#FFA15A",
    annotation_text=f"Strike: ${strike_price:.2f}",
    annotation_position="top right",
)
fig.add_vline(
    x=net_breakeven,
    line_dash="dot",
    line_color="#EF553B",
    annotation_text=f"Net Breakeven: ${net_breakeven:.2f}",
    annotation_position="bottom left",
)

fig.update_layout(
    title="Net Profit / Loss ($) vs. Stock Price at Expiration",
    xaxis_title="Stock Price at Expiration ($)",
    yaxis_title="Net Profit / Loss ($)",
    template="plotly_dark",
    height=450,
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# Trade Summary & CSV Log Export
st.subheader("3. Trade Log & Export Summary")

summary_data = {
    "Metric / Parameter": [
        "Selected Ticker Symbol",
        "Current Stock Price",
        "Strike Price",
        "Premium Collected (per share)",
        "Days to Expiration (DTE)",
        "Contract Count",
        "Required Collateral",
        "Gross Upfront Income",
        "Total Broker Commissions",
        "Net Upfront Income",
        "Gross Annualized Return (AROC)",
        "Net Annualized Return (AROC)",
        "Net Breakeven Price",
        "Downside Safety Buffer",
    ],
    "Value": [
        selected_symbol,
        f"${current_price:.2f}",
        f"${strike_price:.2f}",
        f"${premium:.2f}",
        f"{dte} days",
        f"{contract_count}",
        f"${collateral:,.2f}",
        f"${gross_income:,.2f}",
        f"${total_commissions:.2f}",
        f"${net_income:,.2f}",
        f"{gross_aroc:.2f}%",
        f"{net_aroc:.2f}%",
        f"${net_breakeven:.2f}",
        f"{downside_buffer:.2f}%",
    ],
}

summary_df = pd.DataFrame(summary_data)

col_tbl, col_dl = st.columns([3, 1])

with col_tbl:
    st.table(summary_df)

with col_dl:
    st.markdown("### Export Trade Data")
    st.write(
        "Download this trade setup as a clean CSV file to track your portfolio or backtest history."
    )

    csv_data = summary_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download CSV Summary",
        data=csv_data,
        file_name=f"short_put_{selected_symbol}_{dte}DTE.csv",
        mime="text/csv",
    )

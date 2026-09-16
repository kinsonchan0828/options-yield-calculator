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

# Currency Symbol Map
CURRENCY_MAP = {
    "USD": "$",
    "HKD": "HK$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "TWD": "NT$",
    "CAD": "CA$",
    "AUD": "A$",
    "CNY": "CN¥",
}


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
    "Calculate gross vs. net annualized returns with dynamic multi-currency stock fetching."
)

st.divider()

# Sidebar: Inputs & Controls
st.sidebar.header("1. Stock Search & Live Data")
search_query = st.sidebar.text_input(
    "Search Company or Ticker:",
    value="0700.HK",
    help="Type name (e.g. Tencent, Apple) or ticker (e.g. AAPL, 0700.HK, TSLA)",
)

search_results = search_yahoo_finance(search_query)

if search_results:
    selected_label = st.sidebar.selectbox(
        "Select Matching Asset:", [r[0] for r in search_results]
    )
    selected_symbol = dict(search_results)[selected_label]
else:
    selected_symbol = search_query.strip().upper()

# Robust Multi-Layer Price & Currency Fetcher
live_price = 100.0
currency_code = "USD"
price_fetched = False

if selected_symbol:
    try:
        ticker_obj = yf.Ticker(selected_symbol)

        # 1. Fetch Currency
        try:
            raw_curr = ticker_obj.fast_info.get(
                "currency"
            ) or ticker_obj.info.get("currency")
            if raw_curr:
                currency_code = str(raw_curr).upper()
        except Exception:
            currency_code = "USD"

        # 2. Fetch Price (Method A: fast_info)
        try:
            price_val = ticker_obj.fast_info.get(
                "lastPrice"
            ) or ticker_obj.fast_info.get("previousClose")
            if price_val and not np.isnan(price_val) and price_val > 0:
                live_price = float(price_val)
                price_fetched = True
        except Exception:
            pass

        # Method B: Recent History (Most reliable for HK / International stocks)
        if not price_fetched:
            hist = ticker_obj.history(period="5d")
            if not hist.empty:
                live_price = float(hist["Close"].iloc[-1])
                price_fetched = True

        # Method C: info dictionary fallback
        if not price_fetched:
            info_price = ticker_obj.info.get(
                "currentPrice"
            ) or ticker_obj.info.get("regularMarketPrice")
            if info_price and not np.isnan(info_price) and info_price > 0:
                live_price = float(info_price)
                price_fetched = True

    except Exception:
        pass

curr_sym = CURRENCY_MAP.get(currency_code, f"{currency_code} ")

if not price_fetched and selected_symbol:
    st.sidebar.warning(
        f"⚠️ Could not auto-fetch price for {selected_symbol}. Please enter price manually."
    )

current_price = st.sidebar.number_input(
    f"Stock Price ({currency_code}) [Auto-Fetched / Editable]",
    value=round(live_price, 2),
    step=0.5,
    min_value=0.01,
)

st.sidebar.divider()
st.sidebar.header("2. Option Contract Details")
strike_price = st.sidebar.number_input(
    f"Short Put Strike Price ({currency_code})",
    value=round(current_price * 0.95, 2),
    step=0.5,
    min_value=0.01,
)
premium = st.sidebar.number_input(
    f"Option Premium Collected ({currency_code}/share)",
    value=round(current_price * 0.025, 2),
    step=0.05,
    min_value=0.01,
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
    f"Commission per Contract ({currency_code})",
    value=15.0 if currency_code == "HKD" else 0.65,
    step=0.50 if currency_code == "HKD" else 0.05,
    min_value=0.00,
    help="Standard options fee per contract",
)
flat_ticket_fee = st.sidebar.number_input(
    f"Flat Base Fee per Trade ({currency_code})",
    value=0.00,
    step=0.50,
    min_value=0.00,
)

# Core Financial Calculations
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
st.subheader(f"1. Trade Health & Return Profile ({currency_code})")

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
    f"{curr_sym}{net_breakeven:.2f}",
    f"Gross: {curr_sym}{gross_breakeven:.2f}",
)
kpi3.metric("Downside Safety Buffer", f"{downside_buffer:.2f}%")
kpi4.metric(
    "Total Fees & Commissions",
    f"{curr_sym}{total_commissions:.2f}",
    f"{curr_sym}{comm_per_contract}/contract",
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
    annotation_text=f"Current: {curr_sym}{current_price:.2f}",
    annotation_position="top left",
)
fig.add_vline(
    x=strike_price,
    line_dash="dot",
    line_color="#FFA15A",
    annotation_text=f"Strike: {curr_sym}{strike_price:.2f}",
    annotation_position="top right",
)
fig.add_vline(
    x=net_breakeven,
    line_dash="dot",
    line_color="#EF553B",
    annotation_text=f"Net Breakeven: {curr_sym}{net_breakeven:.2f}",
    annotation_position="bottom left",
)

fig.update_layout(
    title=f"Net Profit / Loss ({currency_code}) vs. Stock Price at Expiration",
    xaxis_title=f"Stock Price at Expiration ({currency_code})",
    yaxis_title=f"Net Profit / Loss ({currency_code})",
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
        "Currency Code",
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
        currency_code,
        f"{curr_sym}{current_price:.2f}",
        f"{curr_sym}{strike_price:.2f}",
        f"{curr_sym}{premium:.2f}",
        f"{dte} days",
        f"{contract_count}",
        f"{curr_sym}{collateral:,.2f}",
        f"{curr_sym}{gross_income:,.2f}",
        f"{curr_sym}{total_commissions:.2f}",
        f"{curr_sym}{net_income:,.2f}",
        f"{gross_aroc:.2f}%",
        f"{net_aroc:.2f}%",
        f"{curr_sym}{net_breakeven:.2f}",
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
        file_name=f"short_put_{selected_symbol}_{dte}DTE_{currency_code}.csv",
        mime="text/csv",
    )

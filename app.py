import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf

import streamlit as st

st.set_page_config(
    page_title="Options Yield & Income Calculator", page_icon="📈", layout="wide"
)

# Google Analytics 4 Tracking Code
st.html("""
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-H7L758ZHC5');
    </script>
""")

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
    "SGD": "S$",
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
    "Calculate gross vs. net annualized returns with dynamic multi-currency stock fetching and customizable broker fee currency."
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
stock_currency = "USD"
price_fetched = False

if selected_symbol:
    try:
        ticker_obj = yf.Ticker(selected_symbol)

        # 1. Fetch Stock Currency
        try:
            raw_curr = ticker_obj.fast_info.get(
                "currency"
            ) or ticker_obj.info.get("currency")
            if raw_curr:
                stock_currency = str(raw_curr).upper()
        except Exception:
            stock_currency = "USD"

        # 2. Fetch Stock Price
        try:
            price_val = ticker_obj.fast_info.get(
                "lastPrice"
            ) or ticker_obj.fast_info.get("previousClose")
            if price_val and not np.isnan(price_val) and price_val > 0:
                live_price = float(price_val)
                price_fetched = True
        except Exception:
            pass

        if not price_fetched:
            hist = ticker_obj.history(period="5d")
            if not hist.empty:
                live_price = float(hist["Close"].iloc[-1])
                price_fetched = True

        if not price_fetched:
            info_price = ticker_obj.info.get(
                "currentPrice"
            ) or ticker_obj.info.get("regularMarketPrice")
            if info_price and not np.isnan(info_price) and info_price > 0:
                live_price = float(info_price)
                price_fetched = True

    except Exception:
        pass

stock_curr_sym = CURRENCY_MAP.get(stock_currency, f"{stock_currency} ")

if not price_fetched and selected_symbol:
    st.sidebar.warning(
        f"⚠️ Could not auto-fetch price for {selected_symbol}. Please enter price manually."
    )

current_price = st.sidebar.number_input(
    f"Stock Price ({stock_currency}) [Auto-Fetched / Editable]",
    value=round(live_price, 2),
    step=0.5,
    min_value=0.01,
)

st.sidebar.divider()
st.sidebar.header("2. Option Contract Details")
strike_price = st.sidebar.number_input(
    f"Short Put Strike Price ({stock_currency})",
    value=round(current_price * 0.95, 2),
    step=0.5,
    min_value=0.01,
)
premium = st.sidebar.number_input(
    f"Option Premium Collected ({stock_currency}/share)",
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

# Broker Home Currency Selection
broker_currency = st.sidebar.selectbox(
    "Select Your Broker Account Currency:",
    options=[
        "USD",
        "HKD",
        "EUR",
        "GBP",
        "CAD",
        "AUD",
        "SGD",
        "JPY",
        "TWD",
        "CNY",
    ],
    index=0,
    help="The currency your broker charges you for commission fees.",
)

broker_curr_sym = CURRENCY_MAP.get(broker_currency, f"{broker_currency} ")

# Exchange Rate Handling
fx_rate = 1.0  # Default 1:1 if currencies match
if broker_currency != stock_currency:
    try:
        fx_pair = f"{broker_currency}{stock_currency}=X"
        fx_ticker = yf.Ticker(fx_pair)
        fetched_fx = fx_ticker.fast_info.get(
            "lastPrice"
        ) or fx_ticker.fast_info.get("previousClose")
        if fetched_fx and not np.isnan(fetched_fx):
            fx_rate = float(fetched_fx)
    except Exception:
        pass

    fx_rate = st.sidebar.number_input(
        f"FX Rate (1 {broker_currency} = ? {stock_currency})",
        value=round(fx_rate, 4),
        step=0.01,
        format="%.4f",
        help=f"Auto-fetched live rate to convert {broker_currency} fees into {stock_currency}.",
    )

comm_per_contract = st.sidebar.number_input(
    f"Commission per Contract ({broker_currency})",
    value=0.65 if broker_currency == "USD" else 15.00,
    step=0.05 if broker_currency == "USD" else 0.50,
    min_value=0.00,
    help=f"Fee in your broker's native currency ({broker_currency})",
)

flat_ticket_fee = st.sidebar.number_input(
    f"Flat Base Fee per Trade ({broker_currency})",
    value=0.00,
    step=0.50,
    min_value=0.00,
)

# Core Financial Calculations
# Round-trip commission in Broker Currency
total_comm_broker_curr = (
    comm_per_contract * contract_count * 2
) + flat_ticket_fee

# Convert commission to Stock Currency for net trade P&L
total_comm_stock_curr = total_comm_broker_curr * fx_rate

collateral = strike_price * 100 * contract_count

gross_income = premium * 100 * contract_count
net_income = gross_income - total_comm_stock_curr

gross_roc = (premium / strike_price) * 100
net_roc = (net_income / collateral) * 100 if collateral > 0 else 0

gross_aroc = gross_roc * (365 / dte)
net_aroc = net_roc * (365 / dte)

gross_breakeven = strike_price - premium
net_breakeven = strike_price - (net_income / (100 * contract_count))
downside_buffer = ((current_price - net_breakeven) / current_price) * 100

# Top KPI Metric Cards: Gross vs Net Comparison
st.subheader(f"1. Trade Health & Return Profile ({stock_currency})")

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
    f"{stock_curr_sym}{net_breakeven:.2f}",
    f"Gross: {stock_curr_sym}{gross_breakeven:.2f}",
)
kpi3.metric("Downside Safety Buffer", f"{downside_buffer:.2f}%")

if broker_currency != stock_currency:
    kpi4.metric(
        "Total Fees & Commissions",
        f"{broker_curr_sym}{total_comm_broker_curr:.2f}",
        f"≈ {stock_curr_sym}{total_comm_stock_curr:.2f} ({stock_currency})",
    )
else:
    kpi4.metric(
        "Total Fees & Commissions",
        f"{broker_curr_sym}{total_comm_broker_curr:.2f}",
        f"{broker_curr_sym}{comm_per_contract}/contract",
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
    - total_comm_stock_curr
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
    annotation_text=f"Current: {stock_curr_sym}{current_price:.2f}",
    annotation_position="top left",
)
fig.add_vline(
    x=strike_price,
    line_dash="dot",
    line_color="#FFA15A",
    annotation_text=f"Strike: {stock_curr_sym}{strike_price:.2f}",
    annotation_position="top right",
)
fig.add_vline(
    x=net_breakeven,
    line_dash="dot",
    line_color="#EF553B",
    annotation_text=f"Net Breakeven: {stock_curr_sym}{net_breakeven:.2f}",
    annotation_position="bottom left",
)

fig.update_layout(
    title=f"Net Profit / Loss ({stock_currency}) vs. Stock Price at Expiration",
    xaxis_title=f"Stock Price at Expiration ({stock_currency})",
    yaxis_title=f"Net Profit / Loss ({stock_currency})",
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
        "Stock Currency",
        "Current Stock Price",
        "Strike Price",
        "Premium Collected (per share)",
        "Days to Expiration (DTE)",
        "Contract Count",
        "Required Collateral",
        "Gross Upfront Income",
        "Broker Fee Currency",
        "Total Broker Commissions (Native)",
        "Converted Commissions (Stock Curr)",
        "Net Upfront Income",
        "Gross Annualized Return (AROC)",
        "Net Annualized Return (AROC)",
        "Net Breakeven Price",
        "Downside Safety Buffer",
    ],
    "Value": [
        selected_symbol,
        stock_currency,
        f"{stock_curr_sym}{current_price:.2f}",
        f"{stock_curr_sym}{strike_price:.2f}",
        f"{stock_curr_sym}{premium:.2f}",
        f"{dte} days",
        f"{contract_count}",
        f"{stock_curr_sym}{collateral:,.2f}",
        f"{stock_curr_sym}{gross_income:,.2f}",
        broker_currency,
        f"{broker_curr_sym}{total_comm_broker_curr:.2f}",
        f"{stock_curr_sym}{total_comm_stock_curr:.2f}",
        f"{stock_curr_sym}{net_income:,.2f}",
        f"{gross_aroc:.2f}%",
        f"{net_aroc:.2f}%",
        f"{stock_curr_sym}{net_breakeven:.2f}",
        f"{downside_buffer:.2f}%",
    ],
}

summary_df = pd.DataFrame(summary_data)

col_tbl, col_dl = st.columns([3, 1])

with col_tbl:
    st.table(summary_df)

with col_dl:
    st.markdown("### Export Trade Data")
    st.write("Download this trade setup as a clean CSV file.")

    csv_data = summary_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download CSV Summary",
        data=csv_data,
        file_name=f"short_put_{selected_symbol}_{dte}DTE_{stock_currency}.csv",
        mime="text/csv",
    )
    st.divider()

# Educational & SEO Content Section
st.markdown("""
## 📚 Cash-Secured Put (CSP) Yield & Ticker Guide

### 1. How Cash-Secured Put (CSP) Net Yield is Calculated
A Cash-Secured Put involves selling an out-of-the-money put option while reserving cash equal to $ \text{Strike Price} \times 100 \times \text{Contracts} $. 

To measure your true risk-adjusted return, **ThetaYield** calculates both Gross and Net Annualized Return on Capital (AROC):

* **Net Premium Income:** $\text{Gross Premium} - \text{Total Broker Commissions}$
* **Net AROC (%):** $\left(\frac{\text{Net Income}}{\text{Required Collateral}}\right) \times \left(\frac{365}{\text{Days to Expiration}}\right) \times 100$
* **Net Breakeven Price:** $\text{Strike Price} - \left(\frac{\text{Net Income}}{100 \times \text{Contracts}}\right)$
* **Downside Safety Buffer (%):** $\left(\frac{\text{Current Stock Price} - \text{Net Breakeven}}{\text{Current Stock Price}}\right) \times 100$

---

### 2. Global Ticker Search & Formatting Rules
Our live search engine automatically fetches stock prices and exchange currencies powered by Yahoo Finance. Depending on the market, use the following ticker conventions:

* **US Stocks & ETFs:** Enter standard symbols directly without suffixes.
  * Example: **`NVDA`** (NVIDIA), **`AAPL`** (Apple), **`TSLA`** (Tesla), **`VOO`** (Vanguard S&P 500 ETF).
* **Hong Kong (HKEX) Stocks:** Append **`.HK`** after the 4-digit numeric stock code.
  * Example: **`0700.HK`** (Tencent Holdings), **`9988.HK`** (Alibaba Group).
* **Japan (TSE) Stocks:** Append **`.T`** after the 4-digit numeric ticker code.
  * Example: **`7203.T`** (Toyota Motor), **`9984.T`** (SoftBank Group).
* **Other International Markets:** If you are unsure of a stock's exchange suffix, search the company name directly in the search bar above or check the symbol on [Yahoo Finance Search](https://finance.yahoo.com).

---

### 3. Why Commission & FX Drag Matter
Options sellers often focus purely on upfront premium yields while ignoring hidden transaction costs. 

1. **Broker Friction:** Paying $0.65 to $1.50 per contract on low-premium options ($0.10–$0.30) can wipe out **5% to 15%** of your total trade profit upon entry and exit.
2. **Foreign Exchange (FX) Drag:** When selling US options in a foreign account currency (or vice-versa), currency conversion markups impact your bottom-line breakeven price. 

Factoring in net commissions ensures you only sell options that compensate for assignment risk and trading costs.
""")

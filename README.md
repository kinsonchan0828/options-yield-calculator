# ThetaYield - Options Cash-Secured Put (CSP) Yield Calculator

ThetaYield is a free, web-based financial utility designed for options traders executing the Wheel Strategy. It calculates real-time annualized yield, downside buffer, and commission drag for Cash-Secured Puts (CSP).

🚀 **Live App:** [https://options-yield-calculator-54dyt3r6bzbqpelafbvdzx.streamlit.app/](https://options-yield-calculator-54dyt3r6bzbqpelafbvdzx.streamlit.app/)

---

## 💡 Key Features
- **Real-Time Data Integration:** Pulls underlying equity prices, option chains, and volatility metrics via `yfinance`.
- **Annualized Return Metrics:** Computes raw yield, annualized return on collateral, and strike distance (downside margin of safety).
- **Interactive Visualizations:** Renders interactive payoff diagrams using `plotly`.
- **Multi-Currency Support:** Evaluates options yield across US and regional markets.

---

## 🛠️ Tech Stack
- **Framework:** [Streamlit](https://streamlit.io/)
- **Data Source:** [yfinance](https://pypi.org/project/yfinance/)
- **Plotting Engine:** [Plotly](https://plotly.com/python/)
- **Data Manipulation:** `pandas`, `numpy`

---

## 🚀 Local Installation & Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/options-yield-calculator.git](https://github.com/YOUR_GITHUB_USERNAME/options-yield-calculator.git)
   cd options-yield-calculator

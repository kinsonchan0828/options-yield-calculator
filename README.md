# ThetaYield - Options Cash-Secured Put (CSP) Yield Calculator

ThetaYield is a free, web-based financial utility designed for options traders executing the Wheel Strategy. It calculates real-time annualized yield, downside buffer, and commission drag for Cash-Secured Puts (CSP).

🚀 **Live App:** https://options-yield-calculator-54dyt3r6bzbqpelafbvdzx.streamlit.app/

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

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/kinsonchan0828/options-yield-calculator.git](https://github.com/kinsonchan0828/options-yield-calculator.git)
   cd options-yield-calculator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

## 📁 Repository Structure
```text
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependency manifest
└── README.md           # Project documentation & quickstart
```

---

## ⚠️ Disclaimer
*ThetaYield is for educational and informational purposes only. It does not constitute financial or investment advice. Options trading involves significant risk of capital loss.*

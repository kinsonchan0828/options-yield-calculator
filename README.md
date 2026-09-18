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
   git clone [https://github.com/kinsonchan0828/options-yield-calculator.git](https://github.com/kinsonchan0828/options-yield-calculator.git)
   cd options-yield-calculator

pip install -r requirements.txt

streamlit run app.py

## 📁 Repository Structure
```text
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependency manifest
└── README.md           # Project documentation & quickstart

⚠️ Disclaimer
ThetaYield is for educational and informational purposes only. It does not constitute financial or investment advice. Options trading involves significant risk of capital loss.

<ElicitationsGroup message="What would you like to set up next?">
  <Elicitation label="Show me exact text for requirements.txt" query="What exact text should I put inside my requirements.txt file on GitHub?"/>
  <Elicitation label="Draft a post for the Streamlit Community Forum" query="Give me a copy-paste post template to share ThetaYield on the official Streamlit Community Forum."/>
</ElicitationsGroup>

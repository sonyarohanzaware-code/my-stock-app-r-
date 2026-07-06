import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.ensemble import RandomForestClassifier
import streamlit as st

# ==========================================
# 1. MATHEMATICAL MODEL (Black-Scholes Formula)
# ==========================================
def calculate_black_scholes(S, K, T, r, sigma, option_type="call"):
    """
    S: Underlying Price (Nifty Spot)
    K: Strike Price
    T: Time to expiration in years (e.g., 5 days = 5/365)
    r: Risk-free interest rate (e.g., 0.07 for 7%)
    sigma: Implied Volatility (IV) (e.g., 0.15 for 15%)
    """
    if T <= 0:
        return (max(0.0, S - K) if option_type == "call" else max(0.0, K - S)), 0, 0, 0
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
        theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
                 - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else: # put option
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
        theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
                 + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = (S * np.sqrt(T) * norm.pdf(d1)) / 100 # per 1% change in IV
    
    return round(price, 2), round(delta, 3), round(gamma, 4), round(theta, 2), round(vega, 2)

# ==========================================
# 2. AI SMARTNESS ENGINE (Predictive Machine Learning)
# ==========================================
def generate_ai_signals(data):
    """
    Historical data parameters aur features par predictive AI signals generate karta hai.
    """
    # Feature Engineering
    data['Price_Change'] = data['Close'].pct_change()
    data['IV_Change'] = data['IV'].pct_change()
    data['PCR_Change'] = data['PCR'].pct_change()
    data.dropna(inplace=True)
    
    # Target Variable: Agar agle din premium badha to 1 (Buy), nahi to 0
    data['Target'] = np.where(data['Close'].shift(-1) > data['Close'], 1, 0)
    
    # Train/Test Split logic for AI model
    X = data[['Price_Change', 'IV_Change', 'PCR_Change']]
    y = data['Target']
    
    if len(data) < 10: # Safe check if data is low
        return "HOLD (Insufficient Data for AI)"
        
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X[:-1], y[:-1]) # training except last row
    
    # Latest live row par prediction
    last_row = X.iloc[[-1]]
    prediction = model.predict(last_row)[0]
    probability = model.predict_proba(last_row)[0][prediction]
    
    return "BUY CALL / SELL PUT" if prediction == 1 else "BUY PUT / SELL CALL", round(probability * 100, 2)

# ==========================================
# 3. WEB INTERFACE / WEB APP INTEGRATION
# ==========================================
st.set_page_config(page_title="Nifty 50 Advance Algo Suite", layout="wide")
st.title("🎯 Nifty 50 Smart Option Trading Algorithm Suite")
st.markdown("---")

# Sidebar Controls for Real-time Data Input
st.sidebar.header("📥 Live Market Input Variables")
nifty_spot = st.sidebar.number_input("Nifty 50 Spot Price", value=24300.0, step=0.5)
strike_price = st.sidebar.number_input("Strike Price (K)", value=24300.0, step=50.0)
days_to_expiry = st.sidebar.slider("Days to Expiry", min_value=0, max_value=30, value=4)
iv = st.sidebar.slider("Implied Volatility (IV %)", min_value=5.0, max_value=80.0, value=14.5) / 100
option_type = st.sidebar.selectbox("Option Type", ["call", "put"])

# Mathematical Calculations Execution
T = days_to_expiry / 365
r = 0.07 # 7% Risk-Free Rate in India

price, delta, gamma, theta, vega = calculate_black_scholes(nifty_spot, strike_price, T, r, iv, option_type)

# Dummy dataset for AI analysis simulation (Live market me isse database se fill karein)
simulated_data = pd.DataFrame({
    'Close': [120, 125, 118, 130, 128, 135, 142, 139, 145, price],
    'IV': [0.14, 0.142, 0.145, 0.138, 0.141, 0.144, 0.146, 0.142, 0.143, iv],
    'PCR': [0.9, 0.95, 0.92, 1.05, 1.01, 1.10, 1.15, 1.12, 1.18, 1.14]
})
ai_signal, confidence = generate_ai_signals(simulated_data)

# Layout Design for Web Display
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Mathematical Valuation & Option Greeks")
    st.metric(label=f"Theoretical Premium ({option_type.upper()})", value=f"₹ {price}")
    
    greeks_df = pd.DataFrame({
        "Greek": ["Delta (Directional Sensitivity)", "Gamma (Delta Acceleration)", "Theta (Time Decay / Day)", "Vega (Volatility Sensitivity)"],
        "Value": [delta, gamma, theta, vega]
    })
    st.table(greeks_df)

with col2:
    st.subheader("🤖 AI Smartness & Trend Prediction")
    st.info(f"**AI Core System Signal:** {ai_signal}")
    st.metric(label="AI Signal Confidence Strength", value=f"{confidence}%")
    
    st.warning("⚠️ **Risk Alert:** Time decay (Theta) is losing **₹ " + str(abs(theta)) + "** per day. Adjust your position positioning accordingly.")

st.markdown("---")
st.caption("Developed for High-Frequency Web Integration. Powered by Black-Scholes and Random Forest Classification Algorithms.")

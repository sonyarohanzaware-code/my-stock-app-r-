import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.ensemble import RandomForestClassifier
import streamlit as st

# ==========================================
# 1. MATHEMATICAL ENGINE (Black-Scholes Model)
# ==========================================
def calculate_black_scholes(S, K, T, r, sigma, option_type="call"):
    """
    S: Underlying Price (Nifty Spot)
    K: Strike Price
    T: Time to expiration in years
    r: Risk-free interest rate
    sigma: Implied Volatility (IV)
    """
    # Expiry din par ya minus me handling for stability
    if T <= 0:
        price = max(0.0, S - K) if option_type == "call" else max(0.0, K - S)
        return round(price, 2), 0.0, 0.0, 0.0, 0.0
    
    # Mathematical components d1 and d2
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
        theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
                 - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:  # Put Option
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
        theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
                 + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = (S * np.sqrt(T) * norm.pdf(d1)) / 100  # Per 1% change in IV
    
    return round(price, 2), round(delta, 3), round(gamma, 4), round(theta, 2), round(vega, 2)


# ==========================================
# 2. AI SMARTNESS ENGINE (Strict Column Mapping)
# ==========================================
def generate_ai_signals(data):
    """
    Historical aur features matrices ko strictly align karke AI signals deta hai.
    """
    df = data.copy()
    
    # Feature Engineering (Math Percentages)
    df['Price_Change'] = df['Close'].pct_change()
    df['IV_Change'] = df['IV'].pct_change()
    df['PCR_Change'] = df['PCR'].pct_change()
    
    # Pehli row NaN hogi, use remove kiya
    df.dropna(inplace=True)
    
    # Strict validation data length check
    if len(df) < 5:
        return "HOLD (Insufficient Data)", 0.0
        
    # Predict direction: Agla Close badhega toh 1, nahi toh 0
    df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    
    feature_cols = ['Price_Change', 'IV_Change', 'PCR_Change']
    
    # Split train and predict matrix safely to avoid ValueError
    X_train = df[feature_cols].iloc[:-1]
    y_train = df['Target'].iloc[:-1]
    X_predict = df[feature_cols].iloc[[-1]]  # Keep as DataFrame structure
    
    # AI Engine Model fitting
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    prediction = model.predict(X_predict)[0]
    probability = model.predict_proba(X_predict)[0][prediction]
    
    signal = "BUY CALL / SELL PUT" if prediction == 1 else "BUY PUT / SELL CALL"
    return signal, round(probability * 100, 2)


# ==========================================
# 3. WEB INTERFACE (Streamlit Layout)
# ==========================================
st.set_page_config(page_title="Nifty 50 Advance Algo Suite", layout="wide")
st.title("🎯 Nifty 50 Smart Option Trading Algorithm Suite")
st.markdown("---")

# Sidebar Controls
st.sidebar.header("📥 Live Market Input Variables")
nifty_spot = st.sidebar.number_input("Nifty 50 Spot Price", value=24300.0, step=0.5)
strike_price = st.sidebar.number_input("Strike Price (K)", value=24300.0, step=50.0)
days_to_expiry = st.sidebar.slider("Days to Expiry", min_value=0, max_value=30, value=4)
iv_input = st.sidebar.slider("Implied Volatility (IV %)", min_value=5.0, max_value=80.0, value=14.5)
option_type = st.sidebar.selectbox("Option Type", ["call", "put"])

# Mathematical Conversion
T = days_to_expiry / 365
r = 0.07  # India Risk-free rate (7%)
sigma = iv_input / 100

# Calculate Greeks & Premium
price, delta, gamma, theta, vega = calculate_black_scholes(nifty_spot, strike_price, T, r, sigma, option_type)

# Simulated Historical Data Stream (In production, replace with live DB/API data)
simulated_data = pd.DataFrame({
    'Close': [120, 125, 118, 130, 128, 135, 142, 139, 145, price],
    'IV': [0.14, 0.142, 0.145, 0.138, 0.141, 0.144, 0.146, 0.142, 0.143, sigma],
    'PCR': [0.9, 0.95, 0.92, 1.05, 1.01, 1.10, 1.15, 1.12, 1.18, 1.14]
})

# Run AI Analytics
ai_signal, confidence = generate_ai_signals(simulated_data)

# Main UI layout grid split
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Mathematical Valuation & Option Greeks")
    st.metric(label=f"Theoretical Premium ({option_type.upper()})", value=f"₹ {price}")
    
    greeks_df = pd.DataFrame({
        "Greek Parameter": ["Delta (Directional)", "Gamma (Acceleration)", "Theta (Time Decay/Day)", "Vega (Volatility Vol)"],
        "Value Output": [delta, gamma, theta, vega]
    })
    st.table(greeks_df)

with col2:
    st.subheader("🤖 AI Smartness & Trend Prediction")
    st.info(f"**AI Core System Signal:** {ai_signal}")
    st.metric(label="AI Signal Confidence Strength", value=f"{confidence}%")
    
    st.warning(f"⚠️ **Risk Alert:** Time decay (Theta) is melting **₹ {abs(theta)}** per day. Plan trades accordingly.")

st.markdown("---")
st.caption("Developed for High-Frequency Web Integration. Powered by Black-Scholes and Random Forest Classification Algorithms.")

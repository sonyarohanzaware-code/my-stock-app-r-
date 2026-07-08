import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.ensemble import RandomForestClassifier
import streamlit as st

# ====================================================================
# 1. MATHEMATICAL MODEL ENGINE (Black-Scholes Model for Options Greeks)
# ====================================================================
def calculate_black_scholes(S, K, T, r, sigma, option_type="call"):
    """
    S: Underlying Price (Nifty Spot)
    K: Strike Price
    T: Time to expiration in years
    r: Risk-free interest rate
    sigma: Implied Volatility (IV)
    """
    if T <= 0:
        theoretical_price = max(0.0, S - K) if option_type == "call" else max(0.0, K - S)
        return round(theoretical_price, 2), 0.0, 0.0, 0.0, 0.0
    
    try:
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == "call":
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            delta = norm.cdf(d1)
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
                     - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        else: # Put Option
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            delta = norm.cdf(d1) - 1
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
                     + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
            
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = (S * np.sqrt(T) * norm.pdf(d1)) / 100 # 1% change behavior
        
        return round(price, 2), round(delta, 3), round(gamma, 4), round(theta, 2), round(vega, 2)
    except Exception:
        return 0.0, 0.0, 0.0, 0.0, 0.0

# ====================================================================
# 2. AI SMARTNESS ENGINE (Strict Column Aligned Random Forest Engine)
# ====================================================================
def generate_ai_signals(data):
    """
    Predictive AI Engine using explicit feature names to avoid ValueError.
    """
    df = data.copy()
    
    # Feature Engineering
    df['Price_Change'] = df['Close'].pct_change()
    df['IV_Change'] = df['IV'].pct_change()
    df['PCR_Change'] = df['PCR'].pct_change()
    
    # Clean NaN values safely
    df.dropna(inplace=True)
    
    feature_cols = ['Price_Change', 'IV_Change', 'PCR_Change']
    
    # Validation Check
    if len(df) < 5:
        return "HOLD (Insufficient Historical Context)", 50.0
        
    # Target Mapping: 1 if premium closes higher tomorrow, else 0
    df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    
    # Strict alignment slicing
    X_train = df[feature_cols].iloc[:-1]
    y_train = df['Target'].iloc[:-1]
    X_predict = df[feature_cols].iloc[[-1]]
    
    # Fit & Predict Execution
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    prediction = model.predict(X_predict)[0]
    probability = model.predict_proba(X_predict)[0][prediction]
    
    signal = "BUY CALL / SELL PUT (BULLISH)" if prediction == 1 else "BUY PUT / SELL CALL (BEARISH)"
    return signal, round(probability * 100, 2)

# ====================================================================
# 3. WEB INTERFACE (Streamlit Architecture)
# ====================================================================
st.set_page_config(page_title="Nifty 50 Smart Algosuite", layout="wide", page_icon="🎯")

st.title("🎯 Nifty 50 Advance Option Analytics & AI Dashboard")
st.markdown("---")

# Sidebar - Live Controllers
st.sidebar.header("📥 Live Control Stream")
nifty_spot = st.sidebar.number_input("Nifty 50 Spot Price", value=24300.0, step=0.5)
strike_price = st.sidebar.number_input("Strike Price (K)", value=24300.0, step=50.0)
days_to_expiry = st.sidebar.slider("Days to Expiry", min_value=0, max_value=30, value=5)
iv_input = st.sidebar.slider("Implied Volatility (IV %)", min_value=5.0, max_value=80.0, value=15.0)
option_type = st.sidebar.selectbox("Option Contract Type", ["call", "put"])

# Variables Formatting
T = days_to_expiry / 365
r = 0.07 # India Risk-Free Rate (7%)
sigma = iv_input / 100

# Math Process Call
price, delta, gamma, theta, vega = calculate_black_scholes(nifty_spot, strike_price, T, r, sigma, option_type)

# Simulated Historical Pipeline for ML Training (Replace with broker API arrays in production)
simulated_dataset = pd.DataFrame({
    'Close': [110, 115, 112, 122, 119, 126, 131, 128, 134, price],
    'IV': [0.14, 0.141, 0.143, 0.139, 0.142, 0.145, 0.147, 0.143, 0.144, sigma],
    'PCR': [0.85, 0.90, 0.88, 1.01, 0.98, 1.05, 1.12, 1.08, 1.15, 1.12]
})

# AI Process Call
ai_signal, confidence = generate_ai_signals(simulated_dataset)

# Layout Presentation
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Mathematical Valuation & Option Greeks")
    st.metric(label=f"Theoretical Fair Value ({option_type.upper()})", value=f"₹ {price}")
    
    greeks_table = pd.DataFrame({
        "Option Greek Parameter": ["Delta (Directional Velocity)", "Gamma (Delta Acceleration)", "Theta (Time Decay Matrix / Day)", "Vega (Volatility Volumetric Shift)"],
        "Calculated Matrix": [delta, gamma, theta, vega]
    })
    st.table(greeks_table)

with col2:
    st.subheader("🤖 AI Smartness & Predictive Analytics")
    
    if "BULLISH" in ai_signal:
        st.success(f"**AI Core Signal:** {ai_signal}")
    else:
        st.error(f"**AI Core Signal:** {ai_signal}")
        
    st.metric(label="AI Probability Vector Confidence", value=f"{confidence}%")
    
    st.warning(f"⚠️ **Theta Vector Risk:** Theta decay is actively devaluing this contract by **₹ {abs(theta)}** per day.")

st.markdown("---")
st.caption("Quantum Engine Platform v2.1 • Powered by Black-Scholes Formulation and Random Forest Predictive Vectors.")

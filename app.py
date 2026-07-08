import numpy as np
import pandas as pd
from scipy.stats import norm
import streamlit as st

# Mathematical Engine for Option Chain Analysis
def calculate_bs_greeks(S, K, T, r, sigma, option_type="call"):
    if T <= 0:
        return (max(0.0, S - K) if option_type == "call" else max(0.0, K - S)), 0, 0
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
        
    theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))) / 365
    return round(price, 2), round(delta, 2), round(theta, 2)

# Streamlit App Setup
st.set_page_config(page_title="Zerodha Like Option Chain Predictor", layout="wide")
st.title("📊 Nifty 50 Pro Option Chain & AI Move Predictor")

# Inputs
spot_price = st.sidebar.number_input("Current Nifty Spot Price", value=24300.0, step=50.0)
iv_ce = st.sidebar.slider("Call Implied Volatility (CE IV %)", 10.0, 50.0, 13.5) / 100
iv_pe = st.sidebar.slider("Put Implied Volatility (PE IV %)", 10.0, 50.0, 14.0) / 100
days_to_expiry = st.sidebar.slider("Days to Expiry", 1, 10, 5)
predicted_move = st.sidebar.slider("Expected Nifty Move (Points)", -300, 300, 100, step=50)

st.subheader(f"⚡ Current Nifty Price: ₹{spot_price} | Predicted Move: {predicted_move} Points")
st.markdown("---")

T = days_to_expiry / 365
r = 0.07 # 7% Risk-Free Rate

# Generate Strikes around ATM (10 Strike Prices Up & Down)
atm_strike = round(spot_price / 50) * 50
strikes = [atm_strike + i * 50 for i in range(-5, 6)]

chain_data = []

for K in strikes:
    # Current Calculations
    c_price, c_delta, c_theta = calculate_bs_greeks(spot_price, K, T, r, iv_ce, "call")
    p_price, p_delta, p_theta = calculate_bs_greeks(spot_price, K, T, r, iv_pe, "put")
    
    # Future/Predicted Slices
    future_spot = spot_price + predicted_move
    f_c_price, _, _ = calculate_bs_greeks(future_spot, K, T - (1/365), r, iv_ce, "call")
    f_p_price, _, _ = calculate_bs_greeks(future_spot, K, T - (1/365), r, iv_pe, "put")
    
    # Change Logic
    ce_change = round(f_c_price - c_price, 2)
    pe_change = round(f_p_price - p_price, 2)
    
    chain_data.append({
        "CE Delta": c_delta,
        "CE Current Premium": f"₹{c_price}",
        "CE Expected Change": f"+₹{ce_change}" if ce_change >= 0 else f"₹{ce_change}",
        "STRIKE PRICE": K,
        "PE Expected Change": f"+₹{pe_change}" if pe_change >= 0 else f"₹{pe_change}",
        "PE Current Premium": f"₹{p_price}",
        "PE Delta": p_pe_delta if 'p_pe_delta' in locals() else p_delta
    })

# Format to DataFrame Grid
df_chain = pd.DataFrame(chain_data)

# Highlight ATM strike
def highlight_atm(row):
    return ['background-color: #2b2b2b' if row['STRIKE PRICE'] == atm_strike else '' for _ in row]

st.dataframe(df_chain.style.apply(highlight_atm, axis=1), use_container_width=True)

# Risk & Directional Analysis 
st.markdown("### 🎯 Algorithmic Prediction Analysis:")
if predicted_move > 0:
    st.success(f"📈 Nifty **{predicted_move} points up** jaane par, Call options ka premium tezi se badhega (sabse jyada impact Deep ITM Calls par hoga). Short sellers ko PE buy ya CE sell se exit karna chahiye.")
else:
    st.error(f"📉 Nifty **{abs(predicted_move)} points down** jaane par, Put options ka premium tezi se badhega (Deep ITM Puts me strong gain hoga).")

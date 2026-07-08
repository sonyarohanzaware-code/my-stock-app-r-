import numpy as np
import pandas as pd
from scipy.stats import norm
import streamlit as st
import plotly.graph_objects as go

# ==========================================
# 1. MATHEMATICAL OPTION ENGINE
# ==========================================
def calculate_bs_greeks(S, K, T, r, sigma, option_type="call"):
    if T <= 0:
        return (max(0.0, S - K) if option_type == "call" else max(0.0, K - S)), 0.0, 0.0
    
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

# ==========================================
# 2. WEB APPLICATION INTERFACE (STYLING)
# ==========================================
st.set_page_config(page_title="Nifty Pro Option Chain Engine", layout="wide")

st.markdown("""
    <style>
    .metric-box { background-color: #1e222d; padding: 15px; border-radius: 8px; border: 1px solid #2a2e39; }
    .reason-box { background-color: #131722; padding: 20px; border-radius: 10px; border-left: 5px solid #2962ff; }
    </style>
""", unsafe_with_html=True)

st.title("📊 Nifty 50 Full Option Chain & Predictive Core")
st.markdown("---")

# Sidebar Controllers
st.sidebar.header("📥 Real-time Market Inputs")
spot_price = st.sidebar.number_input("Current Nifty Spot Price", value=24300.0, step=50.0)
pcr_input = st.sidebar.slider("Current PCR (Put-Call Ratio)", 0.5, 1.8, 1.15, step=0.05)
iv_input = st.sidebar.slider("Market Volatility (IV %)", 8.0, 40.0, 14.2, step=0.1) / 100
days_to_expiry = st.sidebar.slider("Days to Expiry", 1, 7, 4)

st.sidebar.header("🔮 Prediction Target Setup")
target_move = st.sidebar.slider("Expected Nifty Move (Points)", -400, 400, 150, step=50)

# Calculations Configurations
T = days_to_expiry / 365
r = 0.07 
future_spot = spot_price + target_move

# ==========================================
# 3. AI REASONING ENGINE (Kyu Movement Karega?)
# ==========================================
st.markdown("### 🤖 Market Trend & Movement Reason Analysis")
with st.container():
    # Technical & Mathematical Data Mapping for Logic Building
    trend = "BULLISH" if target_move > 0 else "BEARISH"
    
    # Reason analysis logic building based on PCR and IV
    if pcr_input > 1.3:
        pcr_reason = "PCR bohot high hai (>1.3), iska matlab Heavy Put Writing (Support) ho rahi hai. Market niche girna mushkil hai."
    elif pcr_input < 0.7:
        pcr_reason = "PCR bohot low hai (<0.7), market Oversold zone me hai ya Heavy Call Writing (Resistance) hai. Upper side par pressure rahega."
    else:
        pcr_reason = "PCR neutral range me hai, market data-driven solid breakout ka wait kar raha hai."

    if iv_input * 100 > 18:
        iv_reason = "IV (Volatility) badhi hui hai, jiski wajah se premiums me bade sharp up/down jumps dekhne ko milenge (High Risk Option Buyers Market)."
    else:
        iv_reason = "IV control me hai, market smooth chalega aur option sellers time decay (Theta) ka fayda uthayenge."

    st.markdown(f"""
    <div class="reason-box">
        <h4>🎯 Expected View: <span style="color:{'#00ff88' if trend=='BULLISH' else '#ff4a4a'}">{trend} ({target_move} Points Shift Target)</span></h4>
        <p><b>1. Volume & OI Context (PCR):</b> {pcr_reason}</p>
        <p><b>2. Premium Speed (Volatility - IV):</b> {iv_reason}</p>
        <p><b>3. Mathematical Trigger:</b> Agar Nifty <b>₹{spot_price}</b> se <b>₹{future_spot}</b> jata hai, toh niche di gayi Option Chain ke mutabik buyers ka profit aur sellers ka risk calculate kiya gaya hai.</p>
    </div>
    """, unsafe_with_html=True)

st.markdown("---")

# ==========================================
# 4. FULL OPTION CHAIN COMPONENT (ZERODHA STYLE)
# ==========================================
st.markdown("### 📋 Complete Interactive Option Chain Table")

# Generate 14 Strike Prices around ATM (7 up, 7 down)
atm_strike = round(spot_price / 50) * 50
strikes = [atm_strike + i * 50 for i in range(-7, 8)]

chain_list = []

for K in strikes:
    # Current Prices & Greeks
    c_price, c_delta, c_theta = calculate_bs_greeks(spot_price, K, T, r, iv_input, "call")
    p_price, p_delta, p_theta = calculate_bs_greeks(spot_price, K, T, r, iv_input, "put")
    
    # Predicted Future Prices (T - 1 day decay added for accuracy)
    f_c_price, _, _ = calculate_bs_greeks(future_spot, K, max(0, T - (1/365)), r, iv_input, "call")
    f_p_price, _, _ = calculate_bs_greeks(future_spot, K, max(0, T - (1/365)), r, iv_input, "put")
    
    c_change = round(f_c_price - c_price, 2)
    p_change = round(f_p_price - p_price, 2)

    chain_list.append({
        "CE Delta": c_delta,
        "CE Expected Premium": f"₹{f_c_price}",
        "CE Price Change": f"🟢 +₹{c_change}" if c_change >= 0 else f"🔴 ₹{c_change}",
        "CE LTP": f"₹{c_price}",
        "STRIKE PRICE": K,
        "PE LTP": f"₹{p_price}",
        "PE Price Change": f"🟢 +₹{p_change}" if p_change >= 0 else f"🔴 ₹{p_change}",
        "PE Expected Premium": f"₹{f_p_price}",
        "PE Delta": p_delta
    })

df_chain = pd.DataFrame(chain_list)

# Highlight ATM Style Function
def style_chain(row):
    color = 'background-color: #1a2a3a' if row['STRIKE PRICE'] == atm_strike else ''
    return [color] * len(row)

st.dataframe(df_chain.style.apply(style_chain, axis=1), use_container_width=True, height=550)

st.info("💡 **Aasan Bhasha Me Samjhein:** Agar Nifty aapke direction me move karega, toh jis contract ka **Delta** jitna zyada hoga (jaise 0.70 ya 0.80), uska premium utni hi bullet speed se badhega!")

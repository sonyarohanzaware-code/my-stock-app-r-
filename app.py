import streamlit as st
import yfinance as yf
import pandas as pd

# 1. PAGE CONFIGURATION (Web Page ki Settings)
st.set_page_config(page_title="Indian Market Smart Analyzer", page_icon="📊", layout="centered")

st.title("📊 Indian Market Smart Predictor Tool")
st.markdown("Yeh web tool algorithm aur live news ke aadhar par market ka mood (Bullish/Bearish %) batata hai.")
st.markdown("---")

# RSI Calculation Function
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

# 2. WEB USER INTERFACE (Dropdown aur Input)
# Aap list mein aur bhi stocks jod sakte hain
popular_stocks = {
    "Nifty 50 Index": "^NSEI",
    "Bank Nifty Index": "^NSEBANK",
    "Reliance Industries": "RELIANCE.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "TCS": "TCS.NS",
    "State Bank of India (SBI)": "SBIN.NS",
    "HDFC Bank": "HDFCBANK.NS"
}

selected_stock_name = st.selectbox("Apna Stock ya Index Chune:", list(popular_stocks.keys()))
ticker_symbol = popular_stocks[selected_stock_name]

# Custom Input Box agar user ko koi aur stock search karna ho
custom_ticker = st.text_input("Ya phir koi dusra NSE Ticker daalein (e.g., TATASTEEL.NS):", "")
if custom_ticker:
    ticker_symbol = custom_ticker.upper()

# 3. ANALYSIS BUTTON
if st.button("📊 Live Market Analysis Karein"):
    with st.spinner('Live market data fetch ho raha hai...'):
        try:
            stock = yf.Ticker(ticker_symbol)
            df = stock.history(period="60d")
            
            if df.empty or len(df) < 20:
                st.error(f"❌ '{ticker_symbol}' ka data nahi mila. Kripya sahi ticker daalein (Jaise: INFY.NS)")
            else:
                # ALGORITHM CALCULATIONS
                df['SMA_20'] = df['Close'].rolling(window=20).mean()
                df['SMA_50'] = df['Close'].rolling(window=50).mean()
                df['RSI'] = calculate_rsi(df['Close'], period=14)
                
                latest_close = df['Close'].iloc[-1]
                sma_20 = df['SMA_20'].iloc[-1]
                sma_50 = df['SMA_50'].iloc[-1]
                rsi = df['RSI'].iloc[-1]
                
                bullish_signals = 0
                if latest_close > sma_20: bullish_signals += 1
                if sma_20 > sma_50: bullish_signals += 1
                if rsi > 50: bullish_signals += 1

                algo_bullish_pct = (bullish_signals / 3) * 100
                algo_bearish_pct = 100 - algo_bullish_pct

                # NEWS SENTIMENT ANALYSIS
                news_list = stock.news
                news_bullish_pct, news_bearish_pct = 50.0, 50.0
                
                bullish_keywords = ['growth', 'profit', 'rise', 'buy', 'bull', 'gain', 'high', 'deal', 'hike', 'bonus']
                bearish_keywords = ['fall', 'drop', 'loss', 'sell', 'bear', 'slump', 'down', 'crash', 'risk', 'fine']

                if news_list:
                    news_score = 0
                    for article in news_list[:5]:
                        title = article.get('title', '').lower()
                        for word in bullish_keywords:
                            if word in title: news_score += 1
                        for word in bearish_keywords:
                            if word in title: news_score -= 1
                            
                    if news_score > 0:
                        news_bullish_pct, news_bearish_pct = 75.0, 25.0
                    elif news_score < 0:
                        news_bullish_pct, news_bearish_pct = 25.0, 75.0

                # FINAL WEIGHTED SCORE
                final_bullish = (algo_bullish_pct * 0.60) + (news_bullish_pct * 0.40)
                final_bearish = (algo_bearish_pct * 0.60) + (news_bearish_pct * 0.40)

                # SHOW METRICS ON WEB
                col1, col2, col3 = st.columns(3)
                col1.metric("Live Price", f"₹{latest_close:.2f}")
                col2.metric("RSI (Momentum)", f"{rsi:.2f}")
                col3.metric("News Scanned", f"{len(news_list) if news_list else 0} Articles")

                st.markdown("---")
                
                # SHOW FINAL PERCENTAGE WITH BEAUTIFUL BARS
                st.subheader("📊 Market Direction Percentage")
                
                st.write(f"🟢 **BULLISH (Tezi): {final_bullish:.2f}%**")
                st.progress(int(final_bullish))
                
                st.write(f"🔴 **BEARISH (Mandi): {final_bearish:.2f}%**")
                st.progress(int(final_bearish))
                
                st.markdown("---")
                
                # CONCLUSION BOX
                if abs(final_bullish - final_bearish) < 5:
                    st.warning("⚖️ **MARKET MOMENTUM: NEUTRAL** (Market ek range mein reh sakta hai)")
                elif final_bullish > final_bearish:
                    st.success("📈 **MARKET MOMENTUM: STRONG BULLISH** (Tezi ka jhukaav zyada hai)")
                else:
                    st.error("📉 **MARKET MOMENTUM: STRONG BEARISH** (Mandi ka jhukaav zyada hai)")

        except Exception as e:
            st.error(f"Data load karne mein dikkat aayi: {e}")
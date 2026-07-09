import requests
import pandas as pd
import streamlit as st
import yfinance as yf

BASE_URL = "https://www.nseindia.com"
OPTION_CHAIN_API = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
    "Connection": "keep-alive"
}


class NSEDataEngine:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._initialize()

    def _initialize(self):
        """
        Initialize NSE session cookies.
        """
        try:
            self.session.get(BASE_URL, timeout=10)
        except Exception:
            pass

    @st.cache_data(ttl=20)
    def get_option_chain(_self):
        """
        Fetch complete Nifty option chain JSON.
        """
        try:
            response = _self.session.get(
                OPTION_CHAIN_API,
                timeout=10
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:
            st.error(f"Option Chain Error : {e}")
            return None

    @st.cache_data(ttl=20)
    def get_expiry_dates(_self):

        data = _self.get_option_chain()

        if data is None:
            return []

        return data["records"]["expiryDates"]

    @st.cache_data(ttl=20)
    def get_nifty_spot(_self):
        """
        Live Nifty Spot using Yahoo Finance.
        """

        try:

            ticker = yf.Ticker("^NSEI")

            hist = ticker.history(period="1d")

            spot = float(hist["Close"].iloc[-1])

            return round(spot,2)

        except:

            return None

    @st.cache_data(ttl=60)
    def get_india_vix(_self):

        try:

            ticker = yf.Ticker("^INDIAVIX")

            hist = ticker.history(period="1d")

            return round(float(hist["Close"].iloc[-1]),2)

        except:

            return None

    def get_market_snapshot(self):

        return {

            "spot": self.get_nifty_spot(),

            "vix": self.get_india_vix(),

            "expiry": self.get_expiry_dates()

        }


engine = NSEDataEngine()
# config.py

import os
from datetime import datetime

# ==========================
# APP CONFIG
# ==========================

APP_NAME = "Nifty AI Pro"

APP_VERSION = "1.0.0"

AUTO_REFRESH = 30000

CACHE_TIME = 20

# ==========================
# NSE API
# ==========================

NSE_BASE = "https://www.nseindia.com"

OPTION_CHAIN_API = (
    "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
    "Connection": "keep-alive",
}

# ==========================
# Yahoo Symbols
# ==========================

NIFTY_SYMBOL = "^NSEI"

VIX_SYMBOL = "^INDIAVIX"

BANKNIFTY_SYMBOL = "^NSEBANK"

# ==========================
# Black-Scholes
# ==========================

RISK_FREE_RATE = 0.07

DEFAULT_IV = 0.15

TRADING_DAYS = 365

# ==========================
# Option Chain
# ==========================

STRIKE_STEP = 50

STRIKE_RANGE = 20

LOT_SIZE = 75

# ==========================
# AI SETTINGS
# ==========================

AI_MIN_CONFIDENCE = 55

AI_MAX_CONFIDENCE = 95

PCR_BULLISH = 1.20

PCR_BEARISH = 0.80

HIGH_IV = 20

LOW_IV = 12

TARGET_MULTIPLIER = 1.50

STOPLOSS_MULTIPLIER = 0.60

# ==========================
# Export
# ==========================

EXPORT_FOLDER = "exports"

if not os.path.exists(EXPORT_FOLDER):
    os.makedirs(EXPORT_FOLDER)

# ==========================
# Colors
# ==========================

GREEN = "#00C853"

RED = "#FF1744"

BLUE = "#2962FF"

YELLOW = "#FFD600"

ORANGE = "#FF9100"

# ==========================
# Theme
# ==========================

BACKGROUND = "#0E1117"

CARD = "#1E222D"

TEXT = "#FFFFFF"

BORDER = "#333333"

# ==========================
# Refresh Options
# ==========================

REFRESH_OPTIONS = {
    "OFF": 0,
    "30 Sec": 30000,
    "1 Min": 60000,
    "2 Min": 120000,
    "5 Min": 300000,
}

# ==========================
# Expiry
# ==========================

EXPIRY_TYPES = [
    "Current Weekly",
    "Next Weekly",
    "Monthly",
]

# ==========================
# Time
# ==========================

NOW = datetime.now()

TODAY = NOW.date()

CURRENT_TIME = NOW.strftime("%H:%M:%S")
# data_engine.py (Part-1)

import requests
import pandas as pd
import yfinance as yf
import streamlit as st
from config import *

class NSEDataEngine:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(HEADERS)

        self.initialize()

    def initialize(self):

        try:

            self.session.get(NSE_BASE, timeout=10)

        except Exception:

            pass

    @st.cache_data(ttl=CACHE_TIME)
    def option_chain(_self):

        try:

            response = _self.session.get(
                OPTION_CHAIN_API,
                timeout=15
            )

            response.raise_for_status()

            return response.json()

        except Exception:

            return None

    @st.cache_data(ttl=CACHE_TIME)
    def expiry_list(_self):

        data = _self.option_chain()

        if data is None:

            return []

        return data["records"]["expiryDates"]

    @st.cache_data(ttl=CACHE_TIME)
    def nifty_spot(_self):

        try:

            ticker = yf.Ticker(NIFTY_SYMBOL)

            hist = ticker.history(period="1d")

            return round(float(hist["Close"].iloc[-1]),2)

        except Exception:

            return None

    @st.cache_data(ttl=60)
    def india_vix(_self):

        try:

            ticker = yf.Ticker(VIX_SYMBOL)

            hist = ticker.history(period="1d")

            return round(float(hist["Close"].iloc[-1]),2)

        except Exception:

            return None

    def atm_strike(self, spot):

        return round(spot / STRIKE_STEP) * STRIKE_STEP

engine = NSEDataEngine()
# data_engine.py (Part-2)

    @st.cache_data(ttl=CACHE_TIME)
    def option_chain_dataframe(_self, expiry=None):

        data = _self.option_chain()

        if data is None:
            return pd.DataFrame()

        rows = []

        records = data.get("records", {}).get("data", [])

        for item in records:

            if expiry is not None:

                if item.get("expiryDate") != expiry:
                    continue

            strike = item.get("strikePrice")

            ce = item.get("CE", {})
            pe = item.get("PE", {})

            rows.append({

                "Strike": strike,

                "Expiry": item.get("expiryDate"),

                "CE_OI": ce.get("openInterest", 0),
                "CE_Chg_OI": ce.get("changeinOpenInterest", 0),
                "CE_Volume": ce.get("totalTradedVolume", 0),
                "CE_IV": ce.get("impliedVolatility", 0.0),
                "CE_LTP": ce.get("lastPrice", 0.0),

                "PE_OI": pe.get("openInterest", 0),
                "PE_Chg_OI": pe.get("changeinOpenInterest", 0),
                "PE_Volume": pe.get("totalTradedVolume", 0),
                "PE_IV": pe.get("impliedVolatility", 0.0),
                "PE_LTP": pe.get("lastPrice", 0.0)

            })

        df = pd.DataFrame(rows)

        if not df.empty:
            df = df.sort_values("Strike").reset_index(drop=True)

        return df

    def current_expiry(self):

        expiry = self.expiry_list()

        if len(expiry) == 0:
            return None

        return expiry[0]

    def next_expiry(self):

        expiry = self.expiry_list()

        if len(expiry) < 2:
            return None

        return expiry[1]

    def monthly_expiry(self):

        expiry = self.expiry_list()

        if len(expiry) == 0:
            return None

        return expiry[-1]

    def get_chain(self, expiry_type="Current Weekly"):

        if expiry_type == "Current Weekly":
            exp = self.current_expiry()

        elif expiry_type == "Next Weekly":
            exp = self.next_expiry()

        else:
            exp = self.monthly_expiry()

        return self.option_chain_dataframe(exp)
        # data_engine.py (Part-3)

    def calculate_pcr(self, df):

        if df.empty:
            return 0.0

        total_put_oi = df["PE_OI"].sum()
        total_call_oi = df["CE_OI"].sum()

        if total_call_oi == 0:
            return 0.0

        return round(total_put_oi / total_call_oi, 2)

    def max_pain(self, df):

        if df.empty:
            return None

        pain = []

        strikes = df["Strike"].tolist()

        for strike in strikes:

            call_loss = (
                ((strike - df["Strike"]).clip(lower=0)) *
                df["CE_OI"]
            ).sum()

            put_loss = (
                ((df["Strike"] - strike).clip(lower=0)) *
                df["PE_OI"]
            ).sum()

            pain.append(call_loss + put_loss)

        result = pd.DataFrame({
            "Strike": strikes,
            "Pain": pain
        })

        return int(result.loc[result["Pain"].idxmin(), "Strike"])

    def support_resistance(self, df):

        if df.empty:
            return None, None

        support = int(
            df.loc[df["PE_OI"].idxmax(), "Strike"]
        )

        resistance = int(
            df.loc[df["CE_OI"].idxmax(), "Strike"]
        )

        return support, resistance

    def market_summary(self, expiry_type="Current Weekly"):

        df = self.get_chain(expiry_type)

        if df.empty:
            return None

        spot = self.nifty_spot()
        vix = self.india_vix()
        pcr = self.calculate_pcr(df)
        max_pain = self.max_pain(df)
        support, resistance = self.support_resistance(df)

        return {
            "spot": spot,
            "vix": vix,
            "pcr": pcr,
            "max_pain": max_pain,
            "support": support,
            "resistance": resistance,
            "option_chain": df
        }


engine = NSEDataEngine()
# black_scholes.py

import numpy as np
from scipy.stats import norm
from config import RISK_FREE_RATE

class BlackScholes:

    def __init__(self, r=RISK_FREE_RATE):
        self.r = r

    def d1(self, S, K, T, sigma):

        return (
            np.log(S / K) +
            (self.r + 0.5 * sigma**2) * T
        ) / (sigma * np.sqrt(T))

    def d2(self, S, K, T, sigma):

        return self.d1(S, K, T, sigma) - sigma * np.sqrt(T)

    def call_price(self, S, K, T, sigma):

        if T <= 0:
            return max(0, S - K)

        d1 = self.d1(S, K, T, sigma)
        d2 = self.d2(S, K, T, sigma)

        return (
            S * norm.cdf(d1)
            - K * np.exp(-self.r * T) * norm.cdf(d2)
        )

    def put_price(self, S, K, T, sigma):

        if T <= 0:
            return max(0, K - S)

        d1 = self.d1(S, K, T, sigma)
        d2 = self.d2(S, K, T, sigma)

        return (
            K * np.exp(-self.r * T) * norm.cdf(-d2)
            - S * norm.cdf(-d1)
        )

    def delta_call(self, S, K, T, sigma):

        return norm.cdf(self.d1(S, K, T, sigma))

    def delta_put(self, S, K, T, sigma):

        return norm.cdf(self.d1(S, K, T, sigma)) - 1

    def gamma(self, S, K, T, sigma):

        d1 = self.d1(S, K, T, sigma)

        return (
            norm.pdf(d1)
            / (S * sigma * np.sqrt(T))
        )

    def theta_call(self, S, K, T, sigma):

        d1 = self.d1(S, K, T, sigma)
        d2 = self.d2(S, K, T, sigma)

        theta = (
            -(S * norm.pdf(d1) * sigma)
            / (2 * np.sqrt(T))
            - self.r
            * K
            * np.exp(-self.r * T)
            * norm.cdf(d2)
        )

        return theta / 365

    def theta_put(self, S, K, T, sigma):

        d1 = self.d1(S, K, T, sigma)
        d2 = self.d2(S, K, T, sigma)

        theta = (
            -(S * norm.pdf(d1) * sigma)
            / (2 * np.sqrt(T))
            + self.r
            * K
            * np.exp(-self.r * T)
            * norm.cdf(-d2)
        )

        return theta / 365


bs = BlackScholes()
# greeks.py

import numpy as np
from scipy.stats import norm
from config import RISK_FREE_RATE

class Greeks:

    def __init__(self, r=RISK_FREE_RATE):
        self.r = r

    def d1(self, S, K, T, sigma):

        if T <= 0 or sigma <= 0:
            return 0

        return (
            np.log(S / K)
            + (self.r + 0.5 * sigma**2) * T
        ) / (sigma * np.sqrt(T))

    def d2(self, S, K, T, sigma):

        return self.d1(S, K, T, sigma) - sigma * np.sqrt(T)

    def delta_call(self, S, K, T, sigma):

        if T <= 0:
            return 1 if S > K else 0

        return norm.cdf(self.d1(S, K, T, sigma))

    def delta_put(self, S, K, T, sigma):

        if T <= 0:
            return -1 if S < K else 0

        return norm.cdf(self.d1(S, K, T, sigma)) - 1

    def gamma(self, S, K, T, sigma):

        if T <= 0:
            return 0

        d1 = self.d1(S, K, T, sigma)

        return norm.pdf(d1) / (S * sigma * np.sqrt(T))

    def vega(self, S, K, T, sigma):

        if T <= 0:
            return 0

        d1 = self.d1(S, K, T, sigma)

        return (S * norm.pdf(d1) * np.sqrt(T)) / 100

    def theta_call(self, S, K, T, sigma):

        if T <= 0:
            return 0

        d1 = self.d1(S, K, T, sigma)
        d2 = self.d2(S, K, T, sigma)

        theta = (
            -(S * norm.pdf(d1) * sigma)
            / (2 * np.sqrt(T))
            - self.r
            * K
            * np.exp(-self.r * T)
            * norm.cdf(d2)
        )

        return theta / 365

    def theta_put(self, S, K, T, sigma):

        if T <= 0:
            return 0

        d1 = self.d1(S, K, T, sigma)
        d2 = self.d2(S, K, T, sigma)

        theta = (
            -(S * norm.pdf(d1) * sigma)
            / (2 * np.sqrt(T))
            + self.r
            * K
            * np.exp(-self.r * T)
            * norm.cdf(-d2)
        )

        return theta / 365

    def rho_call(self, S, K, T, sigma):

        if T <= 0:
            return 0

        d2 = self.d2(S, K, T, sigma)

        return (K * T * np.exp(-self.r * T) * norm.cdf(d2)) / 100

    def rho_put(self, S, K, T, sigma):

        if T <= 0:
            return 0

        d2 = self.d2(S, K, T, sigma)

        return (-K * T * np.exp(-self.r * T) * norm.cdf(-d2)) / 100

    def all_greeks(self, S, K, T, sigma):

        return {

            "CE_DELTA": round(self.delta_call(S, K, T, sigma), 4),

            "PE_DELTA": round(self.delta_put(S, K, T, sigma), 4),

            "GAMMA": round(self.gamma(S, K, T, sigma), 6),

            "VEGA": round(self.vega(S, K, T, sigma), 4),

            "CE_THETA": round(self.theta_call(S, K, T, sigma), 4),

            "PE_THETA": round(self.theta_put(S, K, T, sigma), 4),

            "CE_RHO": round(self.rho_call(S, K, T, sigma), 4),

            "PE_RHO": round(self.rho_put(S, K, T, sigma), 4),

        }


greeks = Greeks()
# option_chain.py

import pandas as pd
from black_scholes import bs
from greeks import greeks
from config import RISK_FREE_RATE, DEFAULT_IV


class OptionChainAnalyzer:

    def __init__(self):
        self.r = RISK_FREE_RATE

    def prepare_chain(self, df, spot, days_to_expiry):

        if df.empty:
            return pd.DataFrame()

        T = max(days_to_expiry / 365, 1 / 365)

        output = []

        for _, row in df.iterrows():

            strike = float(row["Strike"])

            iv = row["CE_IV"]

            if iv is None or iv <= 0:
                iv = DEFAULT_IV * 100

            sigma = iv / 100

            ce_fair = bs.call_price(
                spot,
                strike,
                T,
                sigma
            )

            pe_fair = bs.put_price(
                spot,
                strike,
                T,
                sigma
            )

            g = greeks.all_greeks(
                spot,
                strike,
                T,
                sigma
            )

            ce_diff = row["CE_LTP"] - ce_fair
            pe_diff = row["PE_LTP"] - pe_fair

            output.append({

                "Strike": strike,

                "CE_LTP": row["CE_LTP"],
                "CE_Fair": round(ce_fair, 2),
                "CE_Mispricing": round(ce_diff, 2),

                "CE_OI": row["CE_OI"],
                "CE_Chg_OI": row["CE_Chg_OI"],
                "CE_Volume": row["CE_Volume"],

                "PE_LTP": row["PE_LTP"],
                "PE_Fair": round(pe_fair, 2),
                "PE_Mispricing": round(pe_diff, 2),

                "PE_OI": row["PE_OI"],
                "PE_Chg_OI": row["PE_Chg_OI"],
                "PE_Volume": row["PE_Volume"],

                "Delta CE": g["CE_DELTA"],
                "Delta PE": g["PE_DELTA"],
                "Gamma": g["GAMMA"],
                "Vega": g["VEGA"],
                "Theta CE": g["CE_THETA"],
                "Theta PE": g["PE_THETA"]

            })

        chain = pd.DataFrame(output)

        chain = chain.sort_values(
            "Strike"
        ).reset_index(drop=True)

        return chain

    def atm(self, chain, spot):

        idx = (
            chain["Strike"] - spot
        ).abs().idxmin()

        return int(chain.loc[idx, "Strike"])

    def itm_calls(self, chain, spot):

        return chain[
            chain["Strike"] < spot
        ]

    def otm_calls(self, chain, spot):

        return chain[
            chain["Strike"] > spot
        ]

    def itm_puts(self, chain, spot):

        return chain[
            chain["Strike"] > spot
        ]

    def otm_puts(self, chain, spot):

        return chain[
            chain["Strike"] < spot
        ]


option_chain = OptionChainAnalyzer()
# ai_engine.py

import pandas as pd
from config import (
    PCR_BULLISH,
    PCR_BEARISH,
    TARGET_MULTIPLIER,
    STOPLOSS_MULTIPLIER,
    AI_MIN_CONFIDENCE,
    AI_MAX_CONFIDENCE,
)


class AIEngine:

    def __init__(self):
        pass

    def trend(self, pcr, spot, max_pain):

        if pcr >= PCR_BULLISH and spot < max_pain:
            return "STRONG BULLISH"

        if pcr >= PCR_BULLISH:
            return "BULLISH"

        if pcr <= PCR_BEARISH and spot > max_pain:
            return "STRONG BEARISH"

        if pcr <= PCR_BEARISH:
            return "BEARISH"

        return "SIDEWAYS"

    def confidence(self, pcr, vix):

        score = 70

        if pcr > 1:
            score += (pcr - 1) * 20
        else:
            score -= (1 - pcr) * 20

        if vix > 20:
            score -= 10

        score = max(AI_MIN_CONFIDENCE,
                    min(AI_MAX_CONFIDENCE, score))

        return round(score, 1)

    def best_ce(self, chain):

        ce = chain.copy()

        ce["Score"] = (
            ce["CE_OI"] * 0.35
            + ce["CE_Volume"] * 0.25
            + ce["Delta CE"] * 10000
            - abs(ce["Theta CE"]) * 1000
        )

        ce = ce.sort_values(
            "Score",
            ascending=False
        )

        return ce.iloc[0]

    def best_pe(self, chain):

        pe = chain.copy()

        pe["Score"] = (
            pe["PE_OI"] * 0.35
            + pe["PE_Volume"] * 0.25
            + abs(pe["Delta PE"]) * 10000
            - abs(pe["Theta PE"]) * 1000
        )

        pe = pe.sort_values(
            "Score",
            ascending=False
        )

        return pe.iloc[0]

    def target(self, premium):

        return round(
            premium * TARGET_MULTIPLIER,
            2
        )

    def stoploss(self, premium):

        return round(
            premium * STOPLOSS_MULTIPLIER,
            2
        )

    def recommendation(
        self,
        chain,
        spot,
        pcr,
        vix,
        max_pain
    ):

        trend = self.trend(
            pcr,
            spot,
            max_pain
        )

        confidence = self.confidence(
            pcr,
            vix
        )

        ce = self.best_ce(chain)

        pe = self.best_pe(chain)

        return {

            "TREND": trend,

            "CONFIDENCE": confidence,

            "BEST_CE_STRIKE":
                int(ce["Strike"]),

            "BEST_PE_STRIKE":
                int(pe["Strike"]),

            "CE_PRICE":
                ce["CE_LTP"],

            "PE_PRICE":
                pe["PE_LTP"],

            "CE_TARGET":
                self.target(
                    ce["CE_LTP"]
                ),

            "PE_TARGET":
                self.target(
                    pe["PE_LTP"]
                ),

            "CE_STOPLOSS":
                self.stoploss(
                    ce["CE_LTP"]
                ),

            "PE_STOPLOSS":
                self.stoploss(
                    pe["PE_LTP"]
                )

        }


ai = AIEngine()
# max_pain.py

import pandas as pd


class MaxPainAnalyzer:

    def __init__(self):
        pass

    def calculate(self, df):

        if df.empty:
            return None

        strikes = sorted(df["Strike"].unique())

        pain_data = []

        for strike in strikes:

            call_pain = 0
            put_pain = 0

            for _, row in df.iterrows():

                if row["Strike"] < strike:
                    call_pain += (
                        strike - row["Strike"]
                    ) * row["CE_OI"]

                if row["Strike"] > strike:
                    put_pain += (
                        row["Strike"] - strike
                    ) * row["PE_OI"]

            total = call_pain + put_pain

            pain_data.append({
                "Strike": strike,
                "CallPain": call_pain,
                "PutPain": put_pain,
                "TotalPain": total
            })

        pain_df = pd.DataFrame(pain_data)

        idx = pain_df["TotalPain"].idxmin()

        return int(
            pain_df.loc[idx, "Strike"]
        )

    def top_supports(self, df, n=5):

        supports = (
            df.sort_values(
                "PE_OI",
                ascending=False
            )
            [["Strike", "PE_OI"]]
            .head(n)
        )

        return supports.reset_index(drop=True)

    def top_resistances(self, df, n=5):

        resistances = (
            df.sort_values(
                "CE_OI",
                ascending=False
            )
            [["Strike", "CE_OI"]]
            .head(n)
        )

        return resistances.reset_index(drop=True)

    def oi_summary(self, df):

        return {

            "TOTAL_CE_OI":
                int(df["CE_OI"].sum()),

            "TOTAL_PE_OI":
                int(df["PE_OI"].sum()),

            "TOTAL_CE_VOLUME":
                int(df["CE_Volume"].sum()),

            "TOTAL_PE_VOLUME":
                int(df["PE_Volume"].sum()),

            "MAX_CE_OI":
                int(df["CE_OI"].max()),

            "MAX_PE_OI":
                int(df["PE_OI"].max())

        }


max_pain = MaxPainAnalyzer()
# charts.py

import plotly.graph_objects as go
import plotly.express as px


class Charts:

    def oi_chart(self, chain):

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=chain["Strike"],
                y=chain["CE_OI"],
                name="CE OI"
            )
        )

        fig.add_trace(
            go.Bar(
                x=chain["Strike"],
                y=chain["PE_OI"],
                name="PE OI"
            )
        )

        fig.update_layout(
            barmode="group",
            template="plotly_dark",
            height=500,
            title="Open Interest"
        )

        return fig

    def volume_chart(self, chain):

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=chain["Strike"],
                y=chain["CE_Volume"],
                name="CE Volume"
            )
        )

        fig.add_trace(
            go.Bar(
                x=chain["Strike"],
                y=chain["PE_Volume"],
                name="PE Volume"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            barmode="group",
            height=500,
            title="Volume"
        )

        return fig

    def premium_chart(self, chain):

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=chain["Strike"],
                y=chain["CE_LTP"],
                mode="lines+markers",
                name="CE"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=chain["Strike"],
                y=chain["PE_LTP"],
                mode="lines+markers",
                name="PE"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            height=500,
            title="Premium Curve"
        )

        return fig

    def pcr_gauge(self, pcr):

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=pcr,
                title={"text": "PCR"},
                gauge={
                    "axis": {"range": [0, 2]},
                    "bar": {"color": "green"}
                }
            )
        )

        fig.update_layout(
            template="plotly_dark",
            height=350
        )

        return fig

    def heatmap(self, chain):

        cols = [
            "CE_OI",
            "PE_OI",
            "CE_Volume",
            "PE_Volume"
        ]

        fig = px.imshow(
            chain[cols].T,
            labels=dict(
                x="Strike",
                y="Metric"
            ),
            x=chain["Strike"],
            y=cols,
            aspect="auto",
            color_continuous_scale="Viridis"
        )

        fig.update_layout(
            template="plotly_dark",
            height=500,
            title="OI / Volume Heatmap"
        )

        return fig


charts = Charts()
# app.py (Part-1)

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from config import *
from data_engine import engine
from option_chain import option_chain
from max_pain import max_pain
from ai_engine import ai
from charts import charts

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📈",
    layout="wide"
)

st_autorefresh(
    interval=AUTO_REFRESH,
    key="refresh"
)

# ==========================
# TITLE
# ==========================

st.title(APP_NAME)

st.caption("Professional Nifty Option Chain AI")

# ==========================
# SIDEBAR
# ==========================

st.sidebar.title("Settings")

expiry_type = st.sidebar.selectbox(
    "Expiry",
    EXPIRY_TYPES
)

days = st.sidebar.slider(
    "Days To Expiry",
    1,
    30,
    5
)

# ==========================
# LIVE DATA
# ==========================

summary = engine.market_summary(expiry_type)

if summary is None:

    st.error("Unable to Fetch Live Data")

    st.stop()

spot = summary["spot"]

vix = summary["vix"]

pcr = summary["pcr"]

support = summary["support"]

resistance = summary["resistance"]

maxpain = summary["max_pain"]

raw_chain = summary["option_chain"]

chain = option_chain.prepare_chain(
    raw_chain,
    spot,
    days
)

signal = ai.recommendation(
    chain,
    spot,
    pcr,
    vix,
    maxpain
)

# ==========================
# TOP METRICS
# ==========================

c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric(
    "NIFTY",
    spot
)

c2.metric(
    "VIX",
    vix
)

c3.metric(
    "PCR",
    pcr
)

c4.metric(
    "MAX PAIN",
    maxpain
)

c5.metric(
    "SUPPORT",
    support
)

c6.metric(
    "RESISTANCE",
    resistance
)

st.divider()

# ==========================
# AI SIGNAL
# ==========================

st.subheader("AI Decision")

x1,x2,x3,x4 = st.columns(4)

x1.metric(
    "TREND",
    signal["TREND"]
)

x2.metric(
    "CONFIDENCE",
    f'{signal["CONFIDENCE"]}%'
)

x3.metric(
    "BEST CE",
    signal["BEST_CE_STRIKE"]
)

x4.metric(
    "BEST PE",
    signal["BEST_PE_STRIKE"]
)

st.divider()
# app.py (Part-2)

# ==========================
# TARGET / STOPLOSS
# ==========================

st.subheader("AI Trade Setup")

a1, a2 = st.columns(2)

with a1:

    st.success("CALL SETUP")

    st.metric(
        "Entry",
        f'₹ {signal["CE_PRICE"]}'
    )

    st.metric(
        "Target",
        f'₹ {signal["CE_TARGET"]}'
    )

    st.metric(
        "Stop Loss",
        f'₹ {signal["CE_STOPLOSS"]}'
    )

with a2:

    st.error("PUT SETUP")

    st.metric(
        "Entry",
        f'₹ {signal["PE_PRICE"]}'
    )

    st.metric(
        "Target",
        f'₹ {signal["PE_TARGET"]}'
    )

    st.metric(
        "Stop Loss",
        f'₹ {signal["PE_STOPLOSS"]}'
    )

st.divider()

# ==========================
# TABS
# ==========================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Option Chain",
    "Charts",
    "Heatmap",
    "Support/Resistance",
    "AI Report"
])

# ==========================
# OPTION CHAIN
# ==========================

with tab1:

    st.dataframe(
        chain,
        use_container_width=True,
        height=700
    )

# ==========================
# CHARTS
# ==========================

with tab2:

    st.plotly_chart(
        charts.oi_chart(chain),
        use_container_width=True
    )

    st.plotly_chart(
        charts.volume_chart(chain),
        use_container_width=True
    )

    st.plotly_chart(
        charts.premium_chart(chain),
        use_container_width=True
    )

# ==========================
# HEATMAP
# ==========================

with tab3:

    st.plotly_chart(
        charts.heatmap(chain),
        use_container_width=True
    )

    st.plotly_chart(
        charts.pcr_gauge(pcr),
        use_container_width=True
    )

# ==========================
# SUPPORT / RESISTANCE
# ==========================

with tab4:

    s = max_pain.top_supports(chain)

    r = max_pain.top_resistances(chain)

    c1, c2 = st.columns(2)

    with c1:

        st.subheader("Top Supports")

        st.dataframe(
            s,
            use_container_width=True
        )

    with c2:

        st.subheader("Top Resistances")

        st.dataframe(
            r,
            use_container_width=True
        )

# ==========================
# AI REPORT
# ==========================

with tab5:

    st.subheader("AI Analysis")

    st.write(f"Trend : **{signal['TREND']}**")

    st.write(f"Confidence : **{signal['CONFIDENCE']}%**")

    st.write(f"Best CE Strike : **{signal['BEST_CE_STRIKE']}**")

    st.write(f"Best PE Strike : **{signal['BEST_PE_STRIKE']}**")

    st.write(f"Support : **{support}**")

    st.write(f"Resistance : **{resistance}**")

    st.write(f"Max Pain : **{maxpain}**")

    st.write(f"PCR : **{pcr}**")

st.divider()

st.success("Nifty AI Pro Loaded Successfully")

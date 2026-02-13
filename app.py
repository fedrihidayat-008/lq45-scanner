import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

st.set_page_config(layout="wide")

st.title("📈 LQ45 Technical + Fractal + News Scanner")

# =============================
# SETTINGS
# =============================

mode_agresif = st.sidebar.toggle("Mode Agresif 🔥")

bobot_teknikal = st.sidebar.slider(
    "Bobot Teknikal",
    0.0, 1.0, 0.7
)

bobot_sentimen = 1 - bobot_teknikal
st.sidebar.write(f"Bobot Sentimen: {bobot_sentimen:.2f}")

# =============================
# LIST SAHAM
# =============================

LQ45 = [
    "BBCA.JK","BBRI.JK","BMRI.JK",
    "ASII.JK","TLKM.JK","ICBP.JK"
]

# =============================
# FUNCTION RSI
# =============================

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# =============================
# FUNCTION SCAN
# =============================

def run_scan():
    results = []

    for ticker in LQ45:
        try:
            data = yf.download(ticker, period="3mo", progress=False)

            if data.empty or len(data) < 30:
                continue

            close = data["Close"]

            last_price = float(close.iloc[-1])
            ma20 = float(close.rolling(20).mean().iloc[-1])

            # RSI
            rsi_series = calculate_rsi(close)
            rsi = float(rsi_series.iloc[-1])

            # =============================
            # SCORING LOGIC (NO SERIES HERE)
            # =============================

            score = 0

            # MA condition
            if last_price > ma20:
                score += 1

            # RSI condition
            if rsi > 50:
                score += 1

            # Mode agresif
            if mode_agresif:
                if rsi > 45:
                    score += 1

            # Normalisasi
            score_teknikal = score /_

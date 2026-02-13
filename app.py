import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

st.set_page_config(layout="wide")

st.title("📈 LQ45 PRO Scanner | EMA + RSI + Breakout + Sentiment")

# ======================================================
# SIDEBAR
# ======================================================

mode_agresif = st.sidebar.toggle("Mode Agresif 🔥", value=False)

bobot_teknikal = st.sidebar.slider(
    "Bobot Teknikal",
    0.0, 1.0, 0.7
)

bobot_sentimen = 1 - bobot_teknikal
st.sidebar.write(f"Bobot Sentimen: {bobot_sentimen:.2f}")

# ======================================================
# LIST SAHAM
# ======================================================

LQ45 = [
    "BBCA.JK","BBRI.JK","BMRI.JK",
    "ASII.JK","TLKM.JK","ICBP.JK"
]

# ======================================================
# RSI FUNCTION
# ======================================================

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ======================================================
# SCAN FUNCTION
# ======================================================

def run_scan():

    results = []

    for ticker in LQ45:
        try:
            data = yf.download(
                ticker,
                period="3mo",
                interval="1d",
                progress=False,
                threads=False
            )

            if data.empty or len(data) < 30:
                continue

            close = data["Close"]
            volume = data["Volume"]

            last_price = float(close.iloc[-1])
            prev_price = float(close.iloc[-2])

            ma20 = float(close.rolling(20).mean().iloc[-1])

            ema9 = float(close.ewm(span=9).mean().iloc[-1])
            ema21 = float(close.ewm(span=21).mean().iloc[-1])

            rsi_series = calculate_rsi(close)
            rsi = float(rsi_series.iloc[-1])
            rsi_prev = float(rsi_series.iloc[-2])

            high20 = float(close.rolling(20).max().iloc[-2])
            avg_vol = float(volume.rolling(20).mean().iloc[-1])
            last_vol = float(volume.iloc[-1])

            # ======================
            # SCORING
            # ======================

            score = 0
            max_score = 7

            # Trend
            if ema9 > ema21:
                score += 1

            if last_price > ma20:
                score += 1

            # Momentum
            if rsi > 55:
                score += 1

            if rsi > rsi_prev:
                score += 1

            # Breakout
            if last_price > high20:
                score += 1

            if last_vol > avg_vol * 1.5:
                score += 1

            # Sentiment proxy (5-day return)
            if (last_price / float(close.iloc[-5]) - 1) > 0:
                score += 1

            # Mode Agresif
            if mode_agresif and rsi > 50:
                score += 1
                max_score += 1

            score_teknikal = score / max_score
            score_sentimen = score_teknikal  # sementara sinkron

            final_score = (
                bobot_teknikal * score_teknikal +
                bobot_sentimen * score_sentimen
            )

            signal = "BUY 🔥" if final_score > 0.6 else "WAIT"

            results.append({
                "Ticker": ticker,
                "Harga": round(last_price,2),
                "RSI": round(rsi,1),
                "EMA9>21": ema9 > ema21,
                "Breakout": last_price > high20,
                "Volume Spike": last_vol > avg_vol * 1.5,
                "Score": round(final_score,2),
                "Signal": signal
            })

        except Exception as e:
            st.error(f"Error {ticker}: {e}")

    return pd.DataFrame(results)

# ======================================================
# BUTTON
# ======================================================

if st.button("🚀 Scan Sekarang"):

    with st.spinner("Scanning PRO mode..."):
        df = run_scan()

    if df.empty:
        st.warning("Tidak ada data yang berhasil diproses.")
    else:
        st.success("Scan selesai!")
        st.dataframe(
            df.sort_values("Score", ascending=False),
            use_container_width=True
        )

st.markdown("---")
st.caption("PRO Scanner | EMA + RSI + Breakout + Volume + Sentiment Proxy")

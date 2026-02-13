import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

st.set_page_config(layout="wide")

st.title("📈 LQ45 Technical + Fractal + News Scanner")

# ======================================================
# SIDEBAR SETTINGS
# ======================================================

mode_agresif = st.sidebar.toggle("Mode Agresif 🔥", value=False)

bobot_teknikal = st.sidebar.slider(
    "Bobot Teknikal",
    min_value=0.0,
    max_value=1.0,
    value=0.7
)

bobot_sentimen = 1 - bobot_teknikal
st.sidebar.write(f"Bobot Sentimen: {bobot_sentimen:.2f}")

# ======================================================
# LIST SAHAM (Sample dulu biar ringan)
# ======================================================

LQ45 = [
    "BBCA.JK","BBRI.JK","BMRI.JK",
    "ASII.JK","TLKM.JK","ICBP.JK"
]

# ======================================================
# FUNCTION RSI
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
# FUNCTION SCAN
# ======================================================

def run_scan():

    results = []

    for ticker in LQ45:
        try:
            data = yf.download(
                ticker,
                period="2mo",
                interval="1d",
                progress=False,
                threads=False
            )

            if data.empty:
                st.warning(f"{ticker} tidak ada data.")
                continue

            close = data["Close"]

            if len(close) < 25:
                continue

            last_price = float(close.iloc[-1])
            ma20 = float(close.rolling(20).mean().iloc[-1])

            rsi_series = calculate_rsi(close)
            rsi = float(rsi_series.iloc[-1])

            # ======================
            # SCORING
            # ======================

            score = 0

            # MA Trend
            if last_price > ma20:
                score += 1

            # RSI Momentum
            if rsi > 50:
                score += 1

            # Mode Agresif
            if mode_agresif and rsi > 45:
                score += 1

            score_teknikal = score / 3

            # Dummy Sentiment sementara
            score_sentimen = 0.5

            final_score = (
                bobot_teknikal * score_teknikal +
                bobot_sentimen * score_sentimen
            )

            results.append({
                "Ticker": ticker,
                "Harga": round(last_price, 2),
                "MA20": round(ma20, 2),
                "RSI": round(rsi, 2),
                "Score": round(final_score, 2)
            })

        except Exception as e:
            st.error(f"Error {ticker}: {e}")

    return pd.DataFrame(results)

# ======================================================
# BUTTON SCAN
# ======================================================

if st.button("🚀 Scan Sekarang"):

    with st.spinner("Scanning saham..."):
        df = run_scan()

    if df.empty:
        st.warning("Tidak ada data yang berhasil diproses.")
    else:
        st.success("Scan selesai!")
        st.dataframe(
            df.sort_values("Score", ascending=False),
            use_container_width=True
        )

# ======================================================
# FOOTER
# ======================================================

st.markdown("---")
st.caption("LQ45 Scanner | EMA + RSI + Fractal + Lightweight News Sentiment")

import streamlit as st
import pandas as pd
import yfinance as yf

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
# FUNCTION SCAN
# =============================

def run_scan():
    results = []

    for ticker in LQ45:
        try:
            data = yf.download(ticker, period="3mo", progress=False)

            if data.empty:
                continue

            close = data["Close"]

            ma20 = close.rolling(20).mean().iloc[-1]
            last = close.iloc[-1]

            score_teknikal = 1 if last > ma20 else 0

            score_sentimen = 0.5  # dummy dulu

            final_score = (
                bobot_teknikal * score_teknikal +
                bobot_sentimen * score_sentimen
            )

            results.append({
                "Ticker": ticker,
                "Harga": round(float(last),2),
                "Score": round(final_score,2)
            })

        except Exception as e:
            st.error(f"Error {ticker}: {e}")

    return pd.DataFrame(results)

# =============================
# BUTTON
# =============================

if st.button("🚀 Scan Sekarang"):

    with st.spinner("Scanning saham..."):
        df = run_scan()

    if df.empty:
        st.warning("Tidak ada data ditemukan.")
    else:
        st.success("Scan selesai!")
        st.dataframe(df.sort_values("Score", ascending=False))

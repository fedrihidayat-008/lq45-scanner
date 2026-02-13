import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="LQ45 Golden Momentum", layout="wide")

st.title("🔥 LQ45 Golden Momentum Screener")
st.write("Universe: LQ45 - Bursa Efek Indonesia")

lq45 = [
"BBRI.JK","BMRI.JK","BBCA.JK","TLKM.JK","ASII.JK",
"ADRO.JK","ANTM.JK","INCO.JK","MDKA.JK","PGAS.JK",
"CPIN.JK","ICBP.JK","UNTR.JK","ITMG.JK","GOTO.JK"
]

# Tombol Scan
if st.button("🚀 Scan Now"):

    st.info("Scanning saham LQ45... mohon tunggu")
    results = []

    progress = st.progress(0)
    total = len(lq45)

    for i, ticker in enumerate(lq45):
        try:
            df = yf.download(ticker, period="1y", progress=False)

            df["EMA50"] = ta.trend.ema_indicator(df["Close"], window=50)
            df["EMA200"] = ta.trend.ema_indicator(df["Close"], window=200)
            df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
            df["MACD"] = ta.trend.macd_diff(df["Close"])

            latest = df.iloc[-1]
            score = 0

            if latest["EMA50"] > latest["EMA200"]:
                score += 25
            if latest["Close"] > latest["EMA50"]:
                score += 15
            if latest["Close"] >= df["High"].rolling(20).max().iloc[-1]:
                score += 20
            if latest["Volume"] > df["Volume"].rolling(20).mean().iloc[-1] * 1.5:
                score += 15
            if 55 < latest["RSI"] < 70:
                score += 10
            if latest["MACD"] > 0:
                score += 10

            if score >= 85:
                signal = "🔥 Strong Buy"
            elif score >= 75:
                signal = "🟢 Buy"
            elif score >= 65:
                signal = "🟡 Watchlist"
            else:
                signal = "❌ No Trade"

            results.append([ticker, score, signal])

        except:
            pass

        progress.progress((i + 1) / total)

    df_result = pd.DataFrame(results, columns=["Ticker", "Score", "Signal"])
    df_result = df_result.sort_values(by="Score", ascending=False)

    st.success("Scan selesai!")
    st.dataframe(df_result, use_container_width=True)

else:
    st.warning("Klik tombol 'Scan Now' untuk mulai screening.")

import feedparser
from transformers import pipeline

@st.cache_resource
def load_sentiment_model():
    return pipeline("sentiment-analysis")

sentiment_model = load_sentiment_model()

def get_news_sentiment(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}+saham+Indonesia&hl=id&gl=ID&ceid=ID:id"
    feed = feedparser.parse(url)

    scores = []
    for entry in feed.entries[:5]:
        result = sentiment_model(entry.title)[0]
        scores.append(result["label"])

    positive = scores.count("POSITIVE")
    negative = scores.count("NEGATIVE")

    if positive > negative:
        return "POSITIVE"
    elif negative > positive:
        return "NEGATIVE"
    else:
        return "NEUTRAL"

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="LQ45 Golden Momentum", layout="wide")
st.title("🔥 LQ45 Golden Momentum Screener")

lq45 = [
"BBRI.JK","BMRI.JK","BBCA.JK","TLKM.JK","ASII.JK",
"ADRO.JK","ANTM.JK","INCO.JK","MDKA.JK","PGAS.JK",
"CPIN.JK","ICBP.JK","UNTR.JK","ITMG.JK","GOTO.JK"
]

# ===== FUNCTIONS =====

def EMA(series, window):
    return series.ewm(span=window, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ===== BUTTON =====

if st.button("🚀 Scan Now"):

    results = []
    progress = st.progress(0)

    for i, ticker in enumerate(lq45):

        df = yf.download(ticker, period="1y", progress=False)

        if df.empty:
            continue

        # FIX MultiIndex column issue
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df["EMA50"] = EMA(df["Close"], 50)
        df["EMA200"] = EMA(df["Close"], 200)
        df["RSI"] = RSI(df["Close"])

        latest = df.iloc[-1]
        score = 0

        # Golden Cross
        if latest["EMA50"] > latest["EMA200"]:
            score += 25

        # Price above EMA50
        if latest["Close"] > latest["EMA50"]:
            score += 15

        # Breakout 20 hari
        if latest["Close"] >= df["High"].rolling(20).max().iloc[-1]:
            score += 20

        # Volume spike
        if latest["Volume"] > df["Volume"].rolling(20).mean().iloc[-1] * 1.5:
            score += 15

        # RSI sehat
        if 55 < latest["RSI"] < 70:
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

        progress.progress((i + 1) / len(lq45))

    df_result = pd.DataFrame(results, columns=["Ticker","Score","Signal"])
    df_result = df_result.sort_values(by="Score", ascending=False)

    st.success("Scan selesai!")
    st.dataframe(df_result, use_container_width=True)

else:
    st.info("Klik tombol 'Scan Now' untuk mulai scanning.")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import feedparser
from transformers import pipeline

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="LQ45 AI Scanner", layout="wide")
st.title("📈 LQ45 AI Technical + News Sentiment Scanner")

# ===============================
# LOAD AI MODEL (cached)
# ===============================
@st.cache_resource
def load_sentiment_model():
    return pipeline("sentiment-analysis")

sentiment_model = load_sentiment_model()

# ===============================
# LQ45 LIST (bisa update manual)
# ===============================
LQ45 = [
    "BBCA.JK","BBRI.JK","BMRI.JK","TLKM.JK","ASII.JK",
    "ADRO.JK","ICBP.JK","UNTR.JK","MDKA.JK","ANTM.JK"
]

# ===============================
# TECHNICAL FUNCTIONS
# ===============================
def calculate_rsi(data, period=14):
    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_technical_score(df, aggressive=False):
    score = 0

    # EMA
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
        score += 1

    # RSI
    df["RSI"] = calculate_rsi(df)

    if aggressive:
        if df["RSI"].iloc[-1] < 60:
            score += 1
    else:
        if df["RSI"].iloc[-1] < 50:
            score += 1

    return score

# ===============================
# NEWS SENTIMENT
# ===============================
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

# ===============================
# SIDEBAR
# ===============================
st.sidebar.header("⚙️ Settings")
aggressive_mode = st.sidebar.toggle("Mode Agresif 🔥", value=False)

technical_weight = st.sidebar.slider("Bobot Teknikal", 0.0, 1.0, 0.7)
sentiment_weight = 1 - technical_weight

st.sidebar.write(f"Bobot Sentimen: {sentiment_weight:.2f}")

# ===============================
# MAIN SCAN
# ===============================
if st.button("🚀 Scan Sekarang"):

    results = []

    progress = st.progress(0)

    for i, ticker in enumerate(LQ45):

        try:
            df = yf.download(ticker, period="3mo", interval="1d", progress=False)

            if df.empty:
                continue

            technical_score = calculate_technical_score(df, aggressive_mode)

            sentiment = get_news_sentiment(ticker.replace(".JK", ""))

            if sentiment == "POSITIVE":
                sentiment_score = 1
            elif sentiment == "NEGATIVE":
                sentiment_score = -1
            else:
                sentiment_score = 0

            final_score = (technical_score * technical_weight) + (sentiment_score * sentiment_weight)

            if final_score >= 1:
                signal = "🔥 STRONG BUY"
            elif final_score > 0:
                signal = "🟢 BUY"
            elif final_score == 0:
                signal = "⚖️ HOLD"
            else:
                signal = "🔴 AVOID"

            results.append({
                "Ticker": ticker,
                "Technical Score": technical_score,
                "Sentiment": sentiment,
                "Final Score": round(final_score, 2),
                "Signal": signal
            })

        except:
            continue

        progress.progress((i + 1) / len(LQ45))

    df_result = pd.DataFrame(results)
    df_result = df_result.sort_values(by="Final Score", ascending=False)

    st.dataframe(df_result, use_container_width=True)

    st.success("Scan selesai!")

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("AI Powered LQ45 Scanner | Technical + News Sentiment")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import feedparser

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(page_title="LQ45 Scanner", layout="wide")
st.title("📈 LQ45 Technical + Fractal + News Scanner")

# =====================================
# LQ45 LIST
# =====================================
LQ45 = [
    "BBCA.JK","BBRI.JK","BMRI.JK","TLKM.JK","ASII.JK",
    "ADRO.JK","ICBP.JK","UNTR.JK","MDKA.JK","ANTM.JK"
]

# =====================================
# RSI FUNCTION
# =====================================
def calculate_rsi(data, period=14):
    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

# =====================================
# TECHNICAL SCORE
# =====================================
def calculate_technical_score(df, aggressive=False):
    score = 0

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
        score += 1

    df["RSI"] = calculate_rsi(df)

    if aggressive:
        if df["RSI"].iloc[-1] < 60:
            score += 1
    else:
        if df["RSI"].iloc[-1] < 50:
            score += 1

    return score

# =====================================
# FRACTAL SUPPORT & RESISTANCE
# =====================================
def detect_fractal_levels(df):
    highs = df["High"].values
    lows = df["Low"].values

    swing_highs = []
    swing_lows = []

    for i in range(2, len(df)-2):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            swing_highs.append(highs[i])

        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            swing_lows.append(lows[i])

    resistance = swing_highs[-1] if swing_highs else df["High"].max()
    support = swing_lows[-1] if swing_lows else df["Low"].min()

    return support, resistance

# =====================================
# LIGHTWEIGHT NEWS SENTIMENT (Keyword Based)
# =====================================
def get_news_sentiment(keyword):
    try:
        url = f"https://news.google.com/rss/search?q={keyword}+saham+Indonesia&hl=id&gl=ID&ceid=ID:id"
        feed = feedparser.parse(url)

        positive_keywords = ["laba", "untung", "naik", "ekspansi", "dividen", "akuisisi"]
        negative_keywords = ["rugi", "turun", "gugatan", "utang", "investigasi"]

        score = 0

        for entry in feed.entries[:5]:
            title = entry.title.lower()

            for word in positive_keywords:
                if word in title:
                    score += 1

            for word in negative_keywords:
                if word in title:
                    score -= 1

        if score > 0:
            return "POSITIVE"
        elif score < 0:
            return "NEGATIVE"
        else:
            return "NEUTRAL"

    except:
        return "NEUTRAL"

# =====================================
# SIDEBAR
# =====================================
st.sidebar.header("⚙️ Settings")

aggressive_mode = st.sidebar.toggle("Mode Agresif 🔥", value=False)

technical_weight = st.sidebar.slider("Bobot Teknikal", 0.0, 1.0, 0.7)
sentiment_weight = 1 - technical_weight

st.sidebar.write(f"Bobot Sentimen: {sentiment_weight:.2f}")

# =====================================
# SCANNER
# =====================================
if st.button("🚀 Scan Sekarang"):

    results = []
    progress = st.progress(0)

    for i, ticker in enumerate(LQ45):

        try:
            df = yf.download(ticker, period="3mo", interval="1d", progress=False)

            if df.empty:
                continue

            technical_score = calculate_technical_score(df, aggressive_mode)

            support, resistance = detect_fractal_levels(df)
            current_price = df["Close"].iloc[-1]

            dist_sup = (current_price - support) / current_price
            dist_res = (resistance - current_price) / current_price

            if dist_sup < 0.02:
                technical_score += 1

            if dist_res < 0.02:
                technical_score -= 1

            sentiment = get_news_sentiment(ticker.replace(".JK", ""))

            if sentiment == "POSITIVE":
                sentiment_score = 1
            elif sentiment == "NEGATIVE":
                sentiment_score = -1
            else:
                sentiment_score = 0

            final_score = (technical_score * technical_weight) + (sentiment_score * sentiment_weight)

            if final_score >= 1.5:
                signal = "🔥 STRONG BUY"
            elif final_score >= 1:
                signal = "🟢 BUY"
            elif final_score >= 0:
                signal = "⚖️ HOLD"
            else:
                signal = "🔴 AVOID"

            results.append({
                "Ticker": ticker,
                "Price": round(current_price, 2),
                "Support": round(support, 2),
                "Resistance": round(resistance, 2),
                "Technical Score": technical_score,
                "Sentiment": sentiment,
                "Final Score": round(final_score, 2),
                "Signal": signal
            })

        except Exception as e:
            print(f"Error di {ticker}: {e}")
            continue

        progress.progress((i + 1) / len(LQ45))

    df_result = pd.DataFrame(results)

    if not df_result.empty and "Final Score" in df_result.columns:
        df_result = df_result.sort_values(by="Final Score", ascending=False)
        st.dataframe(df_result, use_container_width=True)
    else:
        st.warning("Tidak ada data yang berhasil diproses.")

    st.success("Scan selesai!")

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.caption("LQ45 Scanner | EMA + RSI + Fractal + Lightweight News Sentiment")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIG ---
st.set_page_config(page_title="Guardian Research Hub", layout="wide")

@st.cache_data(ttl=300)
def get_full_data(ticker):
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df.empty: return None
        return df
    except: return None

# --- 2. ANALYST ENGINE (HATA DÜZELTİLMİŞ) ---
def generate_dynamic_insights(df):
    # Veriyi seriden tekil sayıya indirgeme
    close_vals = df['Close'].values.flatten()
    last_price = float(close_vals[-1])
    
    ma_20_series = df['Close'].rolling(window=20).mean().values.flatten()
    current_ma = float(ma_20_series[-1])
    
    # Volatilite
    returns = df['Close'].pct_change().dropna().values.flatten()
    vol = float(np.std(returns) * np.sqrt(252) * 100)
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_val = float(100 - (100 / (1 + rs.iloc[-1])).iloc[0] if isinstance(rs.iloc[-1], pd.Series) else 100 - (100 / (1 + rs.iloc[-1])))

    sentiment = "BULLISH" if last_price > current_ma else "BEARISH"
    risk_cat = "Yüksek" if vol > 40 else "Orta" if vol > 20 else "Düşük"
    
    return {
        "price": last_price, "rsi": rsi_val, "vol": vol,
        "sentiment": sentiment, "risk_cat": risk_cat, "ma": current_ma
    }

# --- 3. UI/UX CSS ---
st.markdown("""
<style>
    .report-card { background: #0f172a; border-left: 5px solid #3b82f6; padding: 25px; border-radius: 15px; margin: 10px 0; }
    .learning-card { background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 15px; margin-bottom: 20px; min-height: 250px; }
    .BULLISH { color: #34d399; font-weight: bold; }
    .BEARISH { color: #f87171; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
st.sidebar.title("🛡️ Guardian Hub")
ticker = st.sidebar.text_input("Varlık Ara (Örn: THYAO.IS, BTC-USD)", "THYAO.IS").upper()

df = get_full_data(ticker)

if df is not None:
    res = generate_dynamic_insights(df)
    
    t1, t2, t3 = st.tabs(["📊 Market Insights", "🎓 Learning Hub", "📈 Grafik"])
    
    with t1:
        st.subheader(f"🔍 {ticker} Analitik Raporu")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fiyat", f"{res['price']:.2f}")
        m2.metric("Trend", res['sentiment'])
        m3.metric("RSI (14)", f"{res['rsi']:.1f}")
        m4.metric("Risk", res['risk_cat'])

        st.markdown(f"""
        <div class="report-card">
            <h3>📈 Stratejik Analiz</h3>
            <p>Varlık şu an <span class="{res['sentiment']}">{res['sentiment']}</span> bölgede. 
            20 günlük ortalaması olan {res['ma']:.2f} seviyesine göre konumlanıyor.</p>
            <p><b>Risk Notu:</b> %{res['vol']:.2f} volatilite, portföy yönetimi açısından <b>{res['risk_cat']}</b> dikkat gerektirir.</p>
        </div>
        """, unsafe_allow_html=True)

    with t2:
        st.subheader("🎓 Finansal Eğitim Merkezi")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="learning-card">
                <h4>1. RSI (Momentum)</h4>
                <p>Şu anki değer: <b>{res['rsi']:.1f}</b></p>
                <p>70 üzeri 'aşırı alım', 30 altı 'aşırı satım' sinyalidir. Ekonometrik olarak fiyatın doygunluğa ulaşıp ulaşmadığını gösterir.</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="learning-card">
                <h4>2. Volatilite (Risk)</h4>
                <p>Şu anki oynaklık: <b>%{res['vol']:.1f}</b></p>
                <p>Standart sapma bazlı bu ölçüm, fiyatın ne kadar agresif hareket edebileceğini temsil eder.</p>
            </div>
            """, unsafe_allow_html=True)

    with t3:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Veri bulunamadı. Lütfen geçerli bir sembol girin.")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests

# --- 1. RESEARCH ENGINE: VERİDEN ANALİZ ÜRETİMİ ---
@st.cache_data(ttl=300)
def generate_synthetic_report(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period="60d")
        if df.empty: return None
        
        # Analitik Hesaplamalar
        current_price = df['Close'].iloc[-1]
        change_30d = ((current_price - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
        volatility = df['Close'].pct_change().std() * np.sqrt(252) * 100
        
        # Basit Teknik Sinyaller (MA & RSI)
        ma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
        rsi_delta = df['Close'].diff()
        gain = (rsi_delta.where(rsi_delta > 0, 0)).rolling(window=14).mean()
        loss = (-rsi_delta.where(rsi_delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Momentum & Duyarlılık
        sentiment = "BULL" if current_price > ma_20 and rsi < 70 else "BEAR" if current_price < ma_20 and rsi > 30 else "NEUTRAL"
        
        return {
            "price": current_price,
            "change_30d": change_30d,
            "volatility": volatility,
            "rsi": rsi,
            "sentiment": sentiment,
            "summary": [
                f"Varlık şu an 20 günlük ortalamanın {'üzerinde' if current_price > ma_20 else 'altında'} seyrediyor.",
                f"RSI değeri {rsi:.2f} ile {'aşırı alım' if rsi > 70 else 'aşırı satım' if rsi < 30 else 'nötr'} bölgesinde.",
                f"Yıllıklandırılmış volatilite %{volatility:.2f} ile {'yüksek' if volatility > 40 else 'stabil'} risk profilinde."
            ]
        }
    except: return None

# --- 2. UI/UX: RESEARCH HUB DESIGN ---
st.set_page_config(page_title="Guardian Research Hub", layout="wide")

st.markdown("""
<style>
    .report-card { background: #0f172a; border: 1px solid #1e293b; padding: 25px; border-radius: 20px; margin-top: 20px; }
    .sentiment-badge { padding: 5px 15px; border-radius: 10px; font-weight: 800; }
    .BULL { background: #14532d; color: #4ade80; }
    .BEAR { background: #7f1d1d; color: #f87171; }
    .NEUTRAL { background: #334155; color: #94a3b8; }
    .learning-box { background: #1e293b; border-left: 5px solid #3b82f6; padding: 15px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# --- 3. ANA YAPI: HUB MODÜLLERİ ---
menu = st.tabs(["🔍 Asset Reports", "📊 Market Insights", "🎓 Learning Hub"])

# MODÜL 1: ASSET REPORTS (Otomatik Rapor Üretimi)
with menu[0]:
    st.header("Otomatik Analist Raporu")
    symbol = st.text_input("Analiz edilecek varlık (Örn: THYAO.IS, AAPL, BTC-USD):", "THYAO.IS")
    
    if symbol:
        report = generate_synthetic_report(symbol)
        if report:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"""
                <div class="report-card">
                    <span class="sentiment-badge {report['sentiment']}">{report['sentiment']}</span>
                    <h2 style="margin-top:10px;">{symbol} Stratejik Araştırma Notu</h2>
                    <p style="color:#94a3b8;">Veri Tabanlı Otomatik Analiz • {pd.Timestamp.now().strftime('%d %B %Y')}</p>
                    <hr style="border:0.1px solid #1e293b">
                    <ul>
                        {"".join([f"<li>{item}</li>" for item in report['summary']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.metric("Anlık Fiyat", f"{report['price']:.2f}", f"{report['change_30d']:.2f}% (30G)")
                st.metric("RSI (14)", f"{report['rsi']:.2f}")
                st.metric("Risk (Volatilite)", f"%{report['volatility']:.2f}")

# MODÜL 3: LEARNING HUB (İnteraktif Eğitim)
with menu[2]:
    st.header("Guardian Academy")
    topic = st.selectbox("Bir kavram seçin:", ["Volatilite Nedir?", "RSI Nasıl Okunur?"])
    
    if "Volatilite" in topic:
        st.markdown("""
        <div class="learning-box">
            <b>Ekonometrik Tanım:</b> Volatilite, bir varlığın fiyatındaki belirsizliğin veya riskin ölçüsüdür. 
            Standart sapma kullanılarak hesaplanır.
        </div>
        """, unsafe_allow_html=True)
        # İnteraktif Deney
        val = st.slider("Hisse fiyatı ne kadar hızlı değişiyor?", 1, 100, 20)
        st.info(f"Seçilen volatilite seviyesi ile risk skorun: {val/10}/10")
        st.caption("Görsel: Çizgi grafiğindeki dalgalanma arttıkça volatilite yükselir.")

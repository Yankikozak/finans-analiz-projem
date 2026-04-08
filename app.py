import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIG & OPTİMİZASYON ---
st.set_page_config(page_title="Guardian Research Hub", layout="wide", initial_sidebar_state="expanded")

@st.cache_data(ttl=300)
def get_full_data(ticker):
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df.empty: return None
        return df
    except: return None

# --- 2. ANALYST ENGINE (VERİDEN İÇERİK ÜRETİCİ) ---
def generate_dynamic_insights(ticker, df):
    # Veriyi tekil sayıya indirgeme (HATA DÜZELTME BURADA)
    last_price = float(df['Close'].iloc[-1].iloc[0] if isinstance(df['Close'].iloc[-1], pd.Series) else df['Close'].iloc[-1])
    ma_20 = df['Close'].rolling(window=20).mean()
    current_ma = float(ma_20.iloc[-1].iloc[0] if isinstance(ma_20.iloc[-1], pd.Series) else ma_20.iloc[-1])
    
    ret = df['Close'].pct_change().dropna()
    vol = float(ret.std().iloc[0] if isinstance(ret.std(), pd.Series) else ret.std()) * np.sqrt(252) * 100
    
    # RSI Hesaplama
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = float(100 - (100 / (1 + rs.iloc[-1])).iloc[0] if isinstance(rs.iloc[-1], pd.Series) else 100 - (100 / (1 + rs.iloc[-1])))

    # Sınıflandırma Mantığı
    sentiment = "BULLISH" if last_price > current_ma else "BEARISH"
    risk_cat = "Yüksek" if vol > 40 else "Orta" if vol > 20 else "Düşük"
    
    return {
        "price": last_price,
        "rsi": rsi,
        "vol": vol,
        "sentiment": sentiment,
        "risk_cat": risk_cat,
        "ma": current_ma
    }

# --- 3. UI/UX: MODERN SAAS TEMASI ---
st.markdown("""
<style>
    .report-card { background: #0f172a; border-left: 5px solid #3b82f6; padding: 25px; border-radius: 15px; margin: 10px 0; }
    .learning-card { background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
    .stat-badge { padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.8rem; }
    .BULLISH { background: #064e3b; color: #34d399; }
    .BEARISH { background: #7f1d1d; color: #f87171; }
</style>
""", unsafe_allow_html=True)

# --- 4. ANA TERMİNAL ---
st.sidebar.title("🛡️ Guardian Hub")
ticker = st.sidebar.text_input("Varlık Ara", "THYAO.IS").upper()

df = get_full_data(ticker)

if df is not None:
    res = generate_dynamic_insights(ticker, df)
    
    tab1, tab2, tab3 = st.tabs(["📊 Market Insights", "🎓 Learning Hub", "📈 Veri Terminali"])
    
    with tab1:
        st.subheader(f"🔍 {ticker} Analitik Araştırma Raporu")
        
        # Üst Metrik Paneli
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Anlık Fiyat", f"{res['price']:.2f}")
        m2.metric("Trend Durumu", res['sentiment'])
        m3.metric("RSI (14)", f"{res['rsi']:.1f}")
        m4.metric("Risk Skoru", res['risk_cat'])

        st.markdown(f"""
        <div class="report-card">
            <h3>📈 Stratejik Momentum Analizi</h3>
            <p><b>Durum:</b> Varlık şu an {res['sentiment']} bir yapı sergiliyor. Fiyat {res['ma']:.2f} olan 20 günlük ortalamanın {'üzerinde' if res['sentiment'] == 'BULLISH' else 'altında'} hareket ediyor.</p>
            <p><b>Risk Değerlendirmesi:</b> Yıllık %{res['vol']:.2f} volatilite ile <b>{res['risk_cat']}</b> risk grubundadır. Bu durum yatırımcılar için {'agresif hareketler' if res['risk_cat'] == 'Yüksek' else 'daha dengeli bir seyir'} anlamına gelir.</p>
            <hr style="border:0.1px solid #1e293b">
            <b>Yatırımcı Notu:</b> RSI değeri {res['rsi']:.1f} seviyesinde. Bu, {'piyasanın aşırı alım bölgesinde olduğunu ve kar satışı gelebileceğini' if res['rsi'] > 70 else 'piyasanın dengeli olduğunu'} gösterir.
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.subheader("🎓 Research Learning Hub")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="learning-card">
                <h4>1. RSI (Göreceli Güç Endeksi)</h4>
                <p>Momentumun hızını ölçer. 0-100 arası değer alır.</p>
                <b>Gerçek Örnek:</b> Şu an incelediğin {ticker} için RSI <b>{res['rsi']:.1f}</b>. 
                70 üstü "Doygunluk", 30 altı "Aşırı Satış" demektir.
                <br><br><small>💡 Strateji: RSI 30'un altına indiğinde ekonometrik modeller genellikle 'tepki alımı' bekler.</small>
            </div>
            """, unsafe_allow_html=True)
            

[Image of relative strength index chart]


        with col_b:
            st.markdown(f"""
            <div class="learning-card">
                <h4>2. Volatilite ve Risk</h4>
                <p>Fiyatın standart sapmasını ifade eder. Sakarya Ekonometri temelli hesaplamalarımızda 'belirsizlik' ölçütüdür.</p>
                <b>Analiz:</b> Bu varlıkta volatilite <b>%{res['vol']:.1f}</b>. 
                <br><br><small>⚠️ Not: Volatilite arttıkça, yatırımın risk/getiri oranı yükselir.</small>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.plotly_chart(go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])]), use_container_width=True)

else:
    st.error("Veri çekilemedi. Lütfen sembolü kontrol edin (Örn: THYAO.IS, BTC-USD).")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- PROFESYONEL SAYFA AYARLARI ---
st.set_page_config(page_title="Portfolio Intelligence | Karar Destek Sistemi", layout="wide")

# --- CUSTOM CSS (Ürün Hissi İçin) ---
st.markdown("""
    <style>
    .stMetric { background-color: #111418; border-radius: 12px; padding: 20px; border: 1px solid #1f2937; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2563eb; color: white; font-weight: bold; }
    .reportview-container { background: #0b0e11; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. DEĞER ÖNERİSİ & LANDING (GİRİŞ) ---
if 'started' not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.title("🛡️ Yatırımlarını Şansa Bırakma.")
    st.subheader("Veri Bilimi ve Ekonometrik Modellerle Portföyünü Optimize Et.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 📊 Akıllı Analiz\nSıradan grafiklerin ötesine geç, risklerini matematiksel olarak ölç.")
    with c2:
        st.markdown("### 🤖 AI Stratejist\nKarmaşık verileri senin için yorumlayan ve aksiyon öneren yapay zeka.")
    with c3:
        st.markdown("### 📉 Kayıp Kontrolü\nPiyasa çöküşlerinde ne kadar kaybedebileceğini önceden bil.")
    
    st.markdown("---")
    if st.button("Ücretsiz Analize Başla →"):
        st.session_state.started = True
        st.rerun()
    st.stop()

# --- 2. VARLIK SÖZLÜĞÜ ---
asset_db = {
    "THYAO": "THYAO.IS", "ASELS": "ASELS.IS", "EREGL": "EREGL.IS", "TUPRS": "TUPRS.IS",
    "BTC": "BTC-USD", "ETH": "ETH-USD", "GOLD": "GC=F", "SILVER": "SI=F", "NASDAQ": "^IXIC"
}

# --- 3. ANA PANEL ---
st.sidebar.title("💎 Intelligence Panel")
menu = st.sidebar.selectbox("Menü", ["Varlık Analiz Merkezi", "Portföy Strateji Odası", "Metodoloji & Güven"])

# --- MODÜL 1: ANALİZ MERKEZİ ---
if menu == "Varlık Analiz Merkezi":
    st.header("🔍 Akıllı Varlık Sorgulama")
    query = st.text_input("Hisse veya Kripto Yazın (Örn: THYAO, BTC, GOLD)", "THYAO")
    
    ticker = asset_db.get(query.upper(), f"{query.upper()}.IS" if "." not in query else query)
    
    data = yf.download(ticker, period="1y", progress=False)['Close']
    if not data.empty:
        if isinstance(data, pd.Series): data = data.to_frame()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        ret = ((data.iloc[-1] / data.iloc[0]) - 1).values[0] * 100
        vol = (data.pct_change().std() * np.sqrt(252)).values[0] * 100
        
        col_m1.metric("Son Fiyat", f"{data.iloc[-1].values[0]:.2f}")
        col_m2.metric("Yıllık Getiri", f"%{ret:.2f}")
        col_m3.metric("Oynaklık (Risk)", f"%{vol:.2f}")
        
        st.plotly_chart(px.line(data, template="plotly_dark", title=f"{ticker} Trend"), use_container_width=True)
        
        # WOW EFFECT: AI YORUM
        st.subheader("🤖 AI Analist Yorumu")
        if vol > 35:
            st.error(f"**Yüksek Risk Uyarısı:** {ticker} varlığı çok agresif hareket ediyor. Portföydeki ağırlığı %15'i geçmemeli.")
        elif ret < 0:
            st.warning(f"**Dip Arayışı:** {ticker} negatif trendde. Ekonometrik modeller 'bekle-gör' sinyali veriyor.")
        else:
            st.success(f"**Pozitif Momentum:** Trend güçlü. Mevcut pozisyonlar stratejik hedefler doğrultusunda tutulabilir.")

# --- MODÜL 2: PORTFÖY STRATEJİSİ ---
elif menu == "Portföy Strateji Odası":
    st.header("📂 Stratejik Portföy Yönetimi")
    p_input = st.sidebar.multiselect("Varlık Seçin", list(asset_db.keys()), default=["THYAO", "GOLD"])
    
    if p_input:
        tickers = [asset_db[x] for x in p_input]
        p_data = yf.download(tickers, period="1y", progress=False)['Close']
        
        if not p_data.empty:
            p_ret = p_data.pct_change().dropna()
            weights = np.array([1/len(p_input)]*len(p_input))
            port_daily = (p_ret * weights).sum(axis=1)
            port_cum = (1 + port_daily).cumprod()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Portföy Getirisi", f"%{(port_cum.iloc[-1]-1)*100:.2f}")
            c2.metric("Max Kayıp (DD)", f"%{((port_cum / port_cum.cummax()) - 1).min()*100:.2f}")
            c3.metric("Günlük VaR", f"%{abs(np.percentile(port_daily, 5)*100):.2f}")
            
            st.plotly_chart(px.line(port_cum, title="Strateji Performansı", template="plotly_dark"), use_container_width=True)
            
            # KARAR VERDİREN SİSTEM (AKSİYON ÖNERİSİ)
            st.markdown("### 🎯 Stratejik Aksiyon Planı")
            if abs(np.percentile(port_daily, 5)*100) > 3:
                st.markdown("> 🔴 **KRİTİK:** Portföyün günlük kayıp riski çok yüksek. Nakit veya Altın ağırlığını artırarak 'hedge' yapmalısın.")
            else:
                st.markdown("> 🟢 **GÜVENLİ:** Portföy dağılımı stabil. Mevcut yapıyı bozmadan orta vadeli hedeflere odaklanabilirsin.")

# --- MODÜL 3: GÜVEN & METODOLOJİ ---
elif menu == "Metodoloji & Güven":
    st.header("🛡️ Şeffaflık ve Metodoloji")
    st.write("""
    **Bu panel nasıl çalışıyor?**
    Analizlerimizde Yahoo Finance üzerinden alınan gerçek zamanlı veriler kullanılır. 
    Risk skorları, **Modern Portföy Teorisi (MPT)** ve **Riske Maruz Değer (VaR)** modelleriyle hesaplanır.
    
    **Geliştirici Künyesi:**
    Bu proje, Sakarya Üniversitesi Ekonometri Bölümü öğrencisi **Yankı** tarafından, akademik verilerin finansal okuryazarlığa dönüştürülmesi amacıyla geliştirilmiştir.
    """)
    st.info("⚠️ Not: Bu bir yatırım tavsiyesi değil, istatistiksel bir simülasyon aracıdır.")

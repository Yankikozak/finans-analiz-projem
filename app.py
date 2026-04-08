import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Sayfa Yapılandırması
st.set_page_config(page_title="Risk & Analiz Terminali", layout="wide")

# --- DEV BIST & KÜRESEL VARLIK SÖZLÜĞÜ ---
search_engine_db = {
    "THY": "THYAO.IS", "TÜRK HAVA YOLLARI": "THYAO.IS", "ASELSAN": "ASELS.IS",
    "EREĞLİ": "EREGL.IS", "TÜPRAŞ": "TUPRS.IS", "ŞİŞECAM": "SISE.IS",
    "SASA": "SASA.IS", "HEKTAŞ": "HEKTS.IS", "ASTOR": "ASTOR.IS",
    "BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD", "ALTIN": "GC=F", "GÜMÜŞ": "SI=F",
    "APPLE": "AAPL", "TESLA": "TSLA", "NVIDIA": "NVDA"
}

def smart_search(input_text):
    clean_input = input_text.upper().strip()
    if clean_input in search_engine_db: return search_engine_db[clean_input]
    if "." not in clean_input and "-" not in clean_input: return f"{clean_input}.IS"
    return clean_input

# --- ÜST BAŞLIK ---
st.title("🛡️ Risk & Portföy Analiz Terminali")
st.markdown("---")

# --- SEKMELİ YAPI (ANA AYRIŞMA) ---
tab1, tab2 = st.tabs(["🔍 Varlık Analiz Merkezi", "📂 Portföy Strateji Odası"])

# ==========================================
# SEKME 1: VARLIK ANALİZ MERKEZİ (Arama Motoru)
# ==========================================
with tab1:
    st.subheader("Akıllı Varlık Arama")
    col_search, col_empty = st.columns([2, 2])
    
    with col_search:
        search_query = st.selectbox("İncelemek istediğiniz varlığı seçin veya yazın:", 
                                   options=[""] + sorted(list(search_engine_db.keys())),
                                   index=0)
        manual_search = st.text_input("Veya manuel kod girin (Örn: FROTO):")
        
    target_ticker = ""
    if manual_search: target_ticker = smart_search(manual_search)
    elif search_query: target_ticker = search_engine_db[search_query]

    if target_ticker:
        data_single = yf.download(target_ticker, period="1y", progress=False)['Close']
        if not data_single.empty:
            if isinstance(data_single, pd.Series): data_single = data_single.to_frame()
            
            # Tekli Analiz Metrikleri
            m1, m2, m3 = st.columns(3)
            current_price = data_single.iloc[-1].values[0]
            change = ((data_single.iloc[-1] / data_single.iloc[0]) - 1).values[0] * 100
            
            m1.metric("Güncel Fiyat", f"{current_price:.2f}")
            m2.metric("Yıllık Değişim", f"%{change:.2f}")
            m3.metric("Sembol", target_ticker)
            
            st.plotly_chart(px.line(data_single, title=f"{target_ticker} Fiyat Grafiği", template="plotly_dark"), use_container_width=True)
            
            # OTOMATİK YORUM
            st.info(f"### 💡 {target_ticker} Analiz Notu")
            if change > 0:
                st.write("📈 Varlık pozitif trendde. Mevcut momentum korunuyor.")
            else:
                st.write("📉 Negatif bir seyir hakim. Destek seviyeleri takip edilmeli.")
        else:
            st.error("Veri bulunamadı.")

# ==========================================
# SEKME 2: PORTFÖY STRATEJİ ODASI
# ==========================================
with tab2:
    st.subheader("Portföy Risk & Getiri Analizi")
    
    col_p1, col_p2 = st.columns([1, 2])
    
    with col_p1:
        portfolio_selection = st.multiselect("Portföyünüze varlık ekleyin:", 
                                           options=sorted(list(search_engine_db.keys())),
                                           default=["THY", "ALTIN"])
        days_p = st.slider("Geçmiş Veri (Gün)", 30, 730, 365)
    
    if portfolio_selection:
        tickers_p = [search_engine_db[name] for name in portfolio_selection]
        data_p = yf.download(tickers_p, start=(datetime.now() - timedelta(days=days_p)), progress=False)['Close']
        
        if not data_p.empty:
            returns_p = data_p.pct_change().dropna()
            weights = np.array([1/len(tickers_p)] * len(tickers_p))
            port_returns = (returns_p * weights).sum(axis=1)
            cum_returns = (1 + port_returns).cumprod()
            
            # Portföy Metrikleri
            pm1, pm2, pm3 = st.columns(3)
            pm1.metric("Toplam Getiri", f"%{((cum_returns.iloc[-1]-1)*100):.2f}")
            pm2.metric("Portföy Riski", f"%{(port_returns.std() * np.sqrt(252) * 100):.2f}")
            pm3.metric("Max Kayıp (Drawdown)", f"%{(((cum_returns / cum_returns.cummax()) - 1).min() * 100):.2f}")
            
            st.plotly_chart(px.line(cum_returns, title="Portföy Kümülatif Getiri", template="plotly_dark"), use_container_width=True)
            
            # AKSİYON ÖNERİSİ
            st.success("### 🎯 Stratejik Aksiyon Planı")
            st.write(f"Varlık dağılımınız şu an **eşittir (%{100/len(tickers_p):.1f} her biri)**. Riski azaltmak için korelasyonu düşük varlıklar ekleyebilirsiniz.")
    else:
        st.info("Analiz için sol taraftan portföy varlıklarını seçin.")

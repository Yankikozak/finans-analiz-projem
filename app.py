import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Sayfa Yapılandırması
st.set_page_config(page_title="Yankı Risk Paneli", layout="wide")

st.title("📊 Yankı Finansal Risk & Portföy Terminali")
st.markdown("---")

# --- FONKSİYONLAR ---
def format_ticker(symbol):
    symbol = symbol.upper().strip()
    if not symbol: return None
    if "-" in symbol or "." in symbol: return symbol
    # Basit varsayım: 3-5 harf ve rakam yoksa BIST, yoksa Kripto dene
    if any(char.isdigit() for char in symbol): return f"{symbol}-USD"
    return f"{symbol}.IS"

# --- SIDEBAR: Portföy Girişi ---
st.sidebar.header("📂 Portföy Yönetimi")
raw_tickers = st.sidebar.text_input("Sembolleri virgülle ayırın (Örn: THYAO, BTC, AAPL)", "THYAO, EREGL, BTC")
tickers = [format_ticker(s) for s in raw_tickers.split(",") if s.strip()]

start_date = st.sidebar.date_input("Başlangıç Tarihi", datetime.now() - timedelta(days=365))

# --- VERİ ÇEKME ---
@st.cache_data
def get_data(ticker_list, start):
    try:
        df = yf.download(ticker_list, start=start)['Close']
        if len(ticker_list) == 1:
            df = df.to_frame()
            df.columns = ticker_list
        return df
    except:
        return None

data = get_data(tickers, start_date)

if data is not None and not data.empty:
    # Getirileri hesapla
    returns = data.pct_change().dropna()
    
    # --- ÜST METRİKLER ---
    col1, col2, col3, col4 = st.columns(4)
    
    # 1. Toplam Getiri
    total_ret = (data.iloc[-1] / data.iloc[0] - 1).mean() * 100
    col1.metric("Ort. Toplam Getiri", f"%{total_ret:.2f}")
    
    # 2. Volatilite (Yıllık)
    vol = returns.std().mean() * np.sqrt(252) * 100
    col2.metric("Yıllık Volatilite", f"%{vol:.2f}")
    
    # 3. VaR (%95 Güvenle Günlük)
    var_95 = np.percentile(returns.mean(axis=1), 5) * 100
    col3.metric("Günlük VaR (%95)", f"%{var_95:.2f}", delta_color="inverse")
    
    # 4. RİSK SKORU (0-10)
    # Volatiliteye göre basit bir skorlama (Örn: %40+ volatilite 10 puandır)
    risk_score = min(10, max(1, vol / 5))
    risk_label = "Yüksek" if risk_score > 7 else "Orta" if risk_score > 4 else "Düşük"
    col4.metric("Risk Skoru", f"{risk_score:.1f} / 10", help=f"Risk Seviyesi: {risk_label}")

    st.markdown("---")

    # --- GRAFİKLER ---
    g_col1, g_col2 = st.columns(2)

    with g_col1:
        st.subheader("📈 Kümülatif Getiri (Equity Curve)")
        cum_ret = (1 + returns.mean(axis=1)).cumprod()
        fig_curve = px.line(cum_ret, labels={'value': 'Getiri Çarpanı', 'index': 'Tarih'})
        st.plotly_chart(fig_curve, use_container_width=True)

    with g_col2:
        st.subheader("🥧 Portföy Dağılımı")
        # Basitlik için eşit ağırlık varsayıyoruz (İleride manuel ağırlık eklenebilir)
        weights = [1/len(tickers)] * len(tickers)
        fig_pie = px.pie(values=weights, names=tickers, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- EKONOMETRİK ANALİZ ---
    st.subheader("📉 Maksimum Kayıp (Drawdown) Analizi")
    rolling_max = cum_ret.cummax()
    drawdown = (cum_ret - rolling_max) / rolling_max
    fig_dd = px.area(drawdown, labels={'value': 'Kayıp Oranı', 'index': 'Tarih'}, color_discrete_sequence=['red'])
    st.plotly_chart(fig_dd, use_container_width=True)

    # --- ÖNERİ SİSTEMİ ---
    st.info("💡 **Yankı'nın Analizi:** " + 
            (f"Portföy volatiliten (%{vol:.1f}) oldukça yüksek. " if vol > 30 else "Dengeli bir portföy yapın var. ") +
            "Daha düşük risk için emtia (Altın/Gümüş) eklemeyi düşünebilirsin.")

else:
    st.warning("⚠️ Veri çekilemedi. Lütfen sembollerin doğruluğunu (THYAO, BTC, AAPL vb.) kontrol edin.")
    

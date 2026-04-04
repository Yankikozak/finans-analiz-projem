import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Sayfa Yapılandırması
st.set_page_config(page_title="Yankı Risk Paneli", layout="wide")

st.title("📊 Yankı Finansal Risk & Portföy Terminali")
st.markdown("---")

# --- SEMBOL FORMATLAYICI ---
def format_ticker(symbol):
    symbol = symbol.upper().strip()
    if not symbol: return None
    if "-" in symbol or "." in symbol: return symbol
    return f"{symbol}.IS" # Varsayılan Borsa İstanbul

# --- SIDEBAR ---
st.sidebar.header("📂 Portföy Girişi")
raw_tickers = st.sidebar.text_input("Semboller (Virgülle ayırın)", "THYAO, EREGL")
tickers = [format_ticker(s) for s in raw_tickers.split(",") if s.strip()]
start_date = st.sidebar.date_input("Başlangıç", datetime.now() - timedelta(days=365))

# --- VERİ ÇEKME ---
@st.cache_data
def get_data(ticker_list, start):
    try:
        df = yf.download(ticker_list, start=start)['Close']
        if df.empty: return None
        # Eğer tek hisse ise DataFrame'e çevir
        if isinstance(df, pd.Series):
            df = df.to_frame()
            df.columns = ticker_list
        return df.ffill().dropna() # Boşlukları doldur ve temizle
    except:
        return None

df_data = get_data(tickers, start_date)

# --- ANALİZ VE GÖRÜNÜM ---
if df_data is not None and not df_data.empty and len(df_data) > 5:
    returns = df_data.pct_change().dropna()
    
    if not returns.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        # 1. Getiri
        total_ret = (df_data.iloc[-1] / df_data.iloc[0] - 1).mean() * 100
        col1.metric("Ort. Getiri", f"%{total_ret:.2f}")
        
        # 2. Volatilite
        vol = returns.std().mean() * np.sqrt(252) * 100
        col2.metric("Yıllık Volatilite", f"%{vol:.2f}")
        
        # 3. VaR (GÜVENLİ HESAPLAMA)
        avg_ret_series = returns.mean(axis=1)
        if len(avg_ret_series) > 0:
            var_value = np.percentile(avg_ret_series, 5) * 100
            col3.metric("Günlük VaR (%95)", f"%{var_value:.2f}")
        
        # 4. Risk Skoru
        r_score = min(10, max(1, vol / 5)) if not np.isnan(vol) else 5.0
        col4.metric("Risk Skoru", f"{r_score:.1f} / 10")

        st.markdown("---")
        st.subheader("📈 Performans Grafikleri")
        c1, c2 = st.columns(2)
        
        with c1:
            cum_ret = (1 + returns.mean(axis=1)).cumprod()
            st.plotly_chart(px.line(cum_ret, title="Kümülatif Getiri"), use_container_width=True)
        with c2:
            st.plotly_chart(px.pie(values=[1]*len(tickers), names=tickers, title="Dağılım", hole=0.4), use_container_width=True)
    else:
        st.error("Hesaplanacak yeterli veri oluşmadı.")
else:
    st.warning("⚠️ Veri çekilemiyor. Lütfen sembolleri (Örn: THYAO, BTC) kontrol edin.")

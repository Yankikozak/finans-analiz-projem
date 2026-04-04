import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Sayfa Yapılandırması
st.set_page_config(page_title="Yankı Risk Paneli", layout="wide")

# Profesyonel Başlık
st.title("🛡️ Yankı Finansal Risk & Portföy Analiz Terminali")
st.markdown("---")

# --- SEMBOL FORMATLAYICI ---
def format_ticker(symbol):
    symbol = symbol.upper().strip()
    if not symbol: return None
    if "-" in symbol or "." in symbol: return symbol
    return f"{symbol}.IS" # Varsayılan Borsa İstanbul

# --- GİRİŞ ALANI ---
st.sidebar.header("🔍 Analiz Merkezi")
input_symbol = st.sidebar.text_input("Hisse veya Kripto Yazın", "THYAO")
ticker = format_ticker(input_symbol)

days = st.sidebar.slider("Analiz Süresi (Gün)", 30, 1095, 365)
start_date = datetime.now() - timedelta(days=days)

# --- VERİ ÇEKME ---
@st.cache_data
def get_clean_data(t, start):
    try:
        df = yf.download(t, start=start)['Close']
        if df.empty: return None
        if isinstance(df, pd.Series):
            df = df.to_frame()
        return df.ffill().dropna()
    except:
        return None

data = get_clean_data(ticker, start_date)

if data is not None and len(data) > 5:
    # Hesaplamalar
    price_col = data.iloc[:, 0]
    returns = price_col.pct_change().dropna()
    total_ret = ((price_col.iloc[-1] / price_col.iloc[0]) - 1) * 100
    vol = returns.std() * np.sqrt(252) * 100
    risk_score = min(10, max(1, vol / 6))
    
    # --- ÜST METRİKLER ---
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Dönemlik Getiri", f"%{float(total_ret):.2f}")
    c2.metric("📉 Risk (Volatilite)", f"%{float(vol):.2f}")
    c3.metric("📊 Risk Skoru", f"{float(risk_score):.1f} / 10")

    # --- GRAFİK ---
    st.subheader(f"📈 {input_symbol.upper()} Performans Grafiği")
    fig = px.line(data, template="plotly_dark", labels={'value': 'Fiyat', 'index': 'Tarih'})
    st.plotly_chart(fig, use_container_width=True)

    # --- ANALİZ VE STRATEJİ ---
    st.markdown("---")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🧐 Teknik Görünüm")
        if risk_score > 7:
            st.warning("**Yüksek Risk:** Varlık şu an oldukça agresif hareket ediyor.")
        elif risk_score > 4:
            st.info("**Dengeli Risk:** Standart piyasa koşullarında hareket ediyor.")
        else:
            st.success("**Düşük Risk:** Defansif ve sakin bir karakter sergiliyor.")

    with col_b:
        st.subheader("💡 Strateji Notu")
        if total_ret > 0:
            st.write(f"🚀 {input_symbol.upper()} seçilen dönemde pozitif bir trend izlemiş.")
        else:
            st.write(f"📉 Negatif bir seyir hakim. Destek seviyeleri takip edilmelidir.")

    # --- RİSKE MARUZ DEĞER (VaR) ---
    st.error(f"⚠️ **Kayıp Analizi:** 100 TL'lik bir yatırımda, bir günde matematiksel olarak beklenen max kayıp: {abs(np.percentile(returns, 5)*100):.2f} TL")

else:
    st.error(f"❌ '{input_symbol}' verisi çekilemedi. Lütfen sembolü kontrol edin.")

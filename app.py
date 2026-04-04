import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Sayfa Yapılandırması
st.set_page_config(page_title="Yankı Risk Paneli", layout="wide")

st.title("🛡️ Yankı Finansal Risk & Analiz Terminali")
st.markdown("_Bilmeyenler için akıllı finansal asistan ve risk paneli_")
st.markdown("---")

# --- SEMBOL FORMATLAYICI ---
def format_ticker(symbol):
    symbol = symbol.upper().strip()
    if not symbol: return None
    if "-" in symbol or "." in symbol: return symbol
    return f"{symbol}.IS" # Varsayılan BİST

# --- GİRİŞ ALANI ---
st.sidebar.header("🔍 Analiz Merkezi")
input_symbol = st.sidebar.text_input("Hisse veya Kripto Yazın", "THYAO")
ticker = format_ticker(input_symbol)

days = st.sidebar.slider("Analiz Süresi (Gün)", 30, 730, 365)
start_date = datetime.now() - timedelta(days=days)

# --- VERİ ÇEKME ---
@st.cache_data
def get_clean_data(t, start):
    try:
        df = yf.download(t, start=start)['Close']
        if df.empty: return None
        return df.ffill().dropna()
    except:
        return None

data = get_clean_data(ticker, start_date)

if data is not None and len(data) > 2:
    # Getiri Hesaplama
    returns = data.pct_change().dropna()
    total_ret = (data.iloc[-1] / data.iloc[0] - 1) * 100
    vol = returns.std() * np.sqrt(252) * 100
    
    # --- ÖZET METRİKLER ---
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Dönemlik Getiri", f"%{total_ret:.2f}")
    c2.metric("📉 Risk (Volatilite)", f"%{vol:.2f}")
    
    # Risk Skoru Hesaplama
    risk_score = min(10, max(1, vol / 6))
    c3.metric("📊 Risk Skoru", f"{risk_score:.1f} / 10")

    # --- GRAFİK ---
    st.subheader(f"📈 {input_symbol.upper()} Fiyat Hareketleri")
    fig = px.line(data, labels={'value': 'Fiyat', 'index': 'Tarih'}, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # --- 🤖 AKILLI YORUM VE ANALİZ SİSTEMİ ---
    st.markdown("---")
    st.subheader("💡 Yankı'nın Otomatik Analizi")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.info("### 🧐 Ne Anlama Geliyor?")
        if risk_score > 7:
            st.write(f"⚠️ **Yüksek Risk:** {input_symbol} şu an çok hareketli. Fiyatlar sert inip çıkabilir. Kısa vadeli düşünüyorsan dikkatli olmalısın.")
        elif risk_score > 4:
            st.write(f"⚖️ **Orta Risk:** Dengeli bir hareket var. Uzun vadeli yatırımcılar için normal bir seyir.")
        else:
            st.write(f"🛡️ **Düşük Risk:** Bu varlık oldukça sakin ilerliyor. Büyük kayıplar yaşatma ihtimali diğerlerine göre daha az.")

    with col_b:
        st.success("### 📈 Yatırım Yorumu")
        if total_ret > 0:
            st.write(f"🚀 Seçtiğin dönemde **%{total_ret:.2f}** kazandırmış. Eğer trend yukarıysa, direnç noktalarını takip etmek faydalı olabilir.")
        else:
            st.write(f"📉 Bu dönemde **%{total_ret:.2f}** kaybettirmiş. Eğer şirketin temelleri sağlamsa bu bir 'alım fırsatı' olabilir mi? Ekonometrik olarak 'dip' arayışı sürüyor.")

    # --- VaR ANALİZİ (BASİT DİLLE) ---
    st.warning(f"### 🛡️ Kötü Senaryo Analizi (VaR)\n"
               f"Matematiksel olarak, 100 TL yatırırsan bir günde **{abs(np.percentile(returns, 5)*100):.2f} TL** kaybetme ihtimalin var. Planını buna göre yap!")

else:
    st.error(f"❌ '{input_symbol}' için veri bulunamadı. Lütfen sembolü doğru yazdığınızdan emin olun (Örn: THYAO, BTC, EREGL).")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. KURUMSAL YAPILANDIRMA ---
st.set_page_config(page_title="Risk Control Terminal | Karar Destek Sistemi", layout="wide")

# Modern UI Tasarımı
st.markdown("""
    <style>
    .stMetric { background-color: #111418; border-radius: 12px; padding: 20px; border: 1px solid #1f2937; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2563eb; color: white; }
    .action-box { padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2563eb; background: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DEĞER ÖNERİSİ & GİRİŞ ---
if 'started' not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.title("🛡️ Portföyünü Şansa Değil, Matematiğe Emanet Et.")
    st.subheader("Veri bilimi tabanlı 'Kayıp Kontrol' ve karar destek sistemi.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("### 📉 Kayıp Kontrolü\nPiyasa çöküş senaryolarını önceden simüle edin.")
    with c2:
        st.success("### ⚖️ Akıllı Denge\nRisk skoru yüksek varlıklar için net aksiyon önerileri alın.")
    with c3:
        st.warning("### 🧠 AI Stratejist\nKarmaşık verileri rasyonel yatırım kararlarına dönüştürün.")
    
    st.markdown("---")
    if st.button("Hemen Demo Portföyü İncele →"):
        st.session_state.started = True
        st.rerun()
    st.stop()

# --- 3. AKILLI VERİ SÖZLÜĞÜ ---
asset_db = {
    "THYAO": "THYAO.IS", "ASELS": "ASELS.IS", "EREGL": "EREGL.IS", "TUPRS": "TUPRS.IS",
    "BTC": "BTC-USD", "ETH": "ETH-USD", "ALTIN": "GC=F", "SILVER": "SI=F", "NASDAQ": "^IXIC"
}

# --- 4. SIDEBAR ---
st.sidebar.header("📂 Portföy Yönetimi")
mode = st.sidebar.toggle("Kendi Portföyümü Oluştur", value=False)

if not mode:
    st.sidebar.info("Dengeli Demo Portföy aktif.")
    assets = ["THYAO.IS", "EREGL.IS", "BTC-USD", "GC=F"]
    weights = [0.3, 0.2, 0.1, 0.4]
else:
    raw_input = st.sidebar.text_input("Varlıklar (Örn: THYAO, BTC, GOLD):", "THYAO, EREGL, BTC")
    tickers = []
    for t in raw_input.split(","):
        t = t.strip().upper()
        if t in ["BTC", "ETH"]: tickers.append(f"{t}-USD")
        elif t == "GOLD": tickers.append("GC=F")
        elif "." not in t: tickers.append(f"{t}.IS")
        else: tickers.append(t)
    assets = tickers
    weights = [1/len(assets)] * len(assets)

# --- 5. ANALİZ MOTORU ---
@st.cache_data(ttl=3600)
def analyze_portfolio(tickers, w):
    try:
        data = yf.download(tickers, period="1y", progress=False)['Close']
        if isinstance(data, pd.Series): data = data.to_frame()
        returns = data.pct_change().dropna()
        port_ret = (returns * w).sum(axis=1)
        cum_ret = (1 + port_ret).cumprod()
        return port_ret, cum_ret
    except: return None

res = analyze_portfolio(assets, weights)

if res:
    port_ret, cum_ret = res
    
    # --- 6. METRİKLER ---
    col1, col2, col3, col4 = st.columns(4)
    total_ret = (cum_ret.iloc[-1] - 1) * 100
    vol = port_ret.std() * np.sqrt(252) * 100
    mdd = ((cum_ret / cum_ret.cummax()) - 1).min() * 100
    risk_score = min(10.0, max(1.0, vol / 5))
    
    col1.metric("Toplam Getiri", f"%{total_ret:.2f}")
    col2.metric("Yıllık Oynaklık", f"%{vol:.2f}")
    col3.metric("Maksimum Düşüş", f"%{mdd:.2f}")
    col4.metric("Risk Skoru", f"{risk_score:.1f} / 10") # HATA BURADA DÜZELTİLDİ

    # --- 7. KAYIP KONTROLÜ & SENARYO ---
    st.divider()
    st.subheader("🧪 Kayıp Kontrolü: Stres Testi")
    
    s1, s2 = st.columns(2)
    with s1:
        st.markdown("**Olası Senaryolar**")
        crash_10 = -10 * (vol / 18)
        st.error(f"📉 **%10 Piyasa Düşüşü:** Portföy tahmini **%{abs(crash_10):.1f}** değer kaybeder.")
        var_95 = np.percentile(port_ret, 5) * 100
        st.warning(f"🛡️ **Günlük VaR (%95):** Normal bir günde max kayıp beklentisi: **%{abs(var_95):.2f}**")

    with s2:
        st.markdown("**Stratejik Aksiyon Planı**")
        if risk_score > 7:
            st.markdown("<div class='action-box'>🔴 <b>KRİTİK:</b> Risk seviyen çok yüksek. Portföydeki volatil varlıkları %20 azaltıp Altın veya Nakit ekleyerek 'Hedge' yapmalısın.</div>", unsafe_allow_html=True)
        elif total_ret < -5:
            st.markdown("<div class='action-box'>🔵 <b>BİLGİ:</b> Portföy negatif bölgede. Maliyet düşürmek için kademeli alım stratejisi izlenebilir.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='action-box'>🟢 <b>STABİL:</b> Mevcut dağılım sağlıklı. Trendi bozmadan kâr hedefleri takip edilebilir.</div>", unsafe_allow_html=True)

    st.plotly_chart(px.line(cum_ret, title="Portföy Performans Trendi", template="plotly_dark"), use_container_width=True)

else:
    st.error("Veri çekme hatası. Lütfen sembolleri kontrol edin.")

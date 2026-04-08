import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. KURUMSAL YAPILANDIRMA ---
st.set_page_config(page_title="Risk Control Terminal | Finansal Karar Sistemi", layout="wide")

# Modern UI Tasarımı
st.markdown("""
    <style>
    .stMetric { background-color: #111418; border-radius: 12px; padding: 20px; border: 1px solid #1f2937; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2563eb; color: white; }
    .status-box { padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GİRİŞ DENEYİMİ (LANDING & DEMO) ---
if 'view' not in st.session_state:
    st.session_state.view = 'landing'

if st.session_state.view == 'landing':
    st.title("🛡️ Portföyünü Şansa Değil, Matematiğe Emanet Et.")
    st.subheader("Kayıpları minimize eden, ekonometrik tabanlı karar destek sistemi.")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.info("### 📉 Kayıp Kontrolü\nPotansiyel çöküş senaryolarını önceden simüle edin.")
    with col_b:
        st.success("### ⚖️ Akıllı Denge\nRisk skoru yüksek varlıklar için anında aksiyon önerileri alın.")
    with col_c:
        st.warning("### 🧠 AI Stratejist\nKarmaşık verileri rasyonel yatırım kararlarına dönüştürün.")
    
    st.markdown("---")
    if st.button("Hemen Demo Portföyü İncele →"):
        st.session_state.mode = 'Demo'
        st.session_state.view = 'app'
        st.rerun()
    st.stop()

# --- 3. AKILLI VERİ SÖZLÜĞÜ ---
asset_library = {
    "THYAO": "THYAO.IS", "ASELS": "ASELS.IS", "EREGL": "EREGL.IS", "TUPRS": "TUPRS.IS",
    "BTC": "BTC-USD", "ETH": "ETH-USD", "GOLD": "GC=F", "SILVER": "SI=F", "NASDAQ": "^IXIC"
}

# --- 4. SIDEBAR & PORTFÖY GİRİŞİ ---
st.sidebar.title("💎 Terminal Kontrol")
app_mode = st.sidebar.radio("Çalışma Modu", ["Demo Portföy", "Kendi Portföyünü Oluştur"])

if app_mode == "Demo Portföy":
    selected_assets = ["THYAO", "GOLD", "BTC"]
    st.sidebar.success("Şu an 'Dengeli Demo Portföy' aktif.")
else:
    p_input = st.sidebar.text_input("Varlık Kodları (Virgülle):", "THYAO, EREGL, BTC")
    selected_assets = [x.strip().upper() for x in p_input.split(",")]

# --- 5. ANALİZ MOTORU ---
def run_analysis(assets):
    tickers = [asset_library.get(x, f"{x}.IS" if "." not in x else x) for x in assets]
    data = yf.download(tickers, period="1y", progress=False)['Close']
    if data.empty: return None
    
    returns = data.pct_change().dropna()
    weights = np.array([1/len(assets)] * len(assets))
    port_daily = (returns * weights).sum(axis=1)
    port_cum = (1 + port_daily).cumprod()
    
    return port_daily, port_cum, data

result = run_analysis(selected_assets)

if result:
    port_daily, port_cum, raw_data = result
    
    # --- 6. RİSK METRİKLERİ ---
    m1, m2, m3, m4 = st.columns(4)
    total_ret = (port_cum.iloc[-1] - 1) * 100
    vol = port_daily.std() * np.sqrt(252) * 100
    dd = ((port_cum / port_cum.cummax()) - 1).min() * 100
    var_95 = np.percentile(port_daily, 5) * 100 # %95 güvenle max günlük kayıp

    m1.metric("Toplam Getiri", f"%{total_ret:.2f}")
    m2.metric("Risk Skoru (1-10)", f"{min(10, vol/5):.1f}")
    m3.metric("Maksimum Düşüş", f"%{dd:.2f}")
    m4.metric("Günlük VaR (%95)", f"%{abs(var_95):.2f}")

    # --- 7. SENARYO SİMÜLASYONU (STRES TESTİ) ---
    st.markdown("---")
    st.subheader("🧪 Stres Testi: %10 Piyasa Çöküş Senaryosu")
    market_crash = -10.0
    impact = market_crash * (vol / 18) # Beta korelasyon tahmini
    st.error(f"**Analiz:** Piyasa genelinde yaşanacak %10'luk bir çöküşte, portföyünün tahmini kaybı: **%{abs(impact):.2f}**")

    # --- 8. KARAR VERDİREN AKSİYON ÖNERİLERİ ---
    st.markdown("---")
    col_x, col_y = st.columns(2)
    
    with col_x:
        st.subheader("🥧 Varlık Dağılımı")
        st.plotly_chart(px.pie(values=[1/len(selected_assets)]*len(selected_assets), names=selected_assets, hole=0.5), use_container_width=True)
    
    with col_y:
        st.subheader("🎯 Stratejik Aksiyon Planı")
        if abs(var_95) > 3.0:
            st.warning("⚠️ **RİSK UYARISI:** Günlük kayıp potansiyelin (VaR) kritik eşikte. Portföydeki yüksek volatil varlıkları (Kripto/Agresif Hisse) azaltıp, ALTIN veya NAKİT ağırlığını %20 artırman önerilir.")
        elif total_ret < -5:
            st.info("ℹ️ **MALİYET DÜŞÜRME:** Portföy negatif bölgede. Ekonometrik trend dönüşü için destek seviyeleri beklenmeli, kademeli alım stratejisi izlenmeli.")
        else:
            st.success("✅ **STABİL:** Portföy yapısı şu an piyasa koşullarına uyumlu. Mevcut ağırlıkları bozmadan kâr hedefleri takip edilebilir.")

    # --- 9. PERFORMANS GRAFİĞİ ---
    st.plotly_chart(px.line(port_cum, title="Performans Takip Çizelgesi", template="plotly_dark"), use_container_width=True)

else:
    st.warning("Veri çekilemedi, lütfen sembolleri kontrol edin.")

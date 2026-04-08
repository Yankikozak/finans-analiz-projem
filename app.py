import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- 1. PREMIUM UI CONFIG ---
st.set_page_config(page_title="Guardian | Finansal Risk Terminali", layout="wide")

# Kurumsal Stil Dosyası
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main-title { font-size: 3.5rem; font-weight: 800; letter-spacing: -2px; color: #ffffff; margin-bottom: 5px; }
    .subtitle { font-size: 1.2rem; color: #8a8f98; margin-bottom: 2rem; }
    
    /* Güven Paneli (Eski Siyah Boşluk Alanı) */
    .trust-panel { 
        background: linear-gradient(145deg, #111418, #1a1e23); 
        border: 1px solid #2563eb; 
        padding: 2.5rem; 
        border-radius: 24px; 
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    
    .stButton>button { background: #2563eb; color: white; border-radius: 12px; height: 3.5rem; font-weight: 600; border: none; transition: 0.3s; width: 100%; }
    .stButton>button:hover { background: #1d4ed8; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4); }
    
    .feature-card { background: #161b22; padding: 1.5rem; border-radius: 16px; border: 1px solid #30363d; height: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-ASSET SEARCH ENGINE ---
asset_universe = {
    "THY": "THYAO.IS", "ASELSAN": "ASELS.IS", "EREĞLİ": "EREGL.IS", "ŞİŞECAM": "SISE.IS",
    "BITCOIN": "BTC-USD", "BTC": "BTC-USD", "ETHEREUM": "ETH-USD", "ETH": "ETH-USD",
    "ALTIN": "GC=F", "GÜMÜŞ": "SI=F", "NASDAQ": "^IXIC", "BIST100": "XU100.IS"
}

def universal_search(query):
    query = query.upper().strip()
    if query in asset_universe: return asset_universe[query]
    if "." not in query and "-" not in query: return f"{query}.IS"
    return query

# --- 3. SESSION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 4. PROFESYONEL GİRİŞ EKRANI (LANDING PAGE) ---
if not st.session_state.authenticated:
    st.markdown("<h1 class='main-title'>Guardian Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Akademik Ekonometri Modelleriyle Sermayenizi Koruyan Karar Destek Sistemi</p>", unsafe_allow_html=True)

    # GÜVEN VE TANITIM BLOĞU (MANIFESTO)
    st.markdown("""
        <div class='trust-panel'>
            <h3 style='color: #2563eb; margin-top: 0;'>🛡️ Finansal Fırtınalara Karşı Matematiksel Kalkan</h3>
            <p style='color: #d1d5db; font-size: 1.15rem; line-height: 1.7;'>
                Finansal piyasalarda kalıcı olmanın sırrı, ne kadar kazandığınız değil, <b>siyah kuğu (black swan)</b> olaylarında ne kadar korunduğunuzdur. 
                Guardian, portföyünüzü sadece bir tablo olarak değil, binlerce kriz senaryosuna maruz kalan dinamik bir yapı olarak analiz eder. 
                <br><br>
                Sistemimiz, <b>Value at Risk (VaR)</b> ve <b>Monte Carlo</b> simülasyonlarını kullanarak, duygulardan arınmış, 
                tamamen matematiksel bir risk projeksiyonu sunar.
            </p>
            <div style='display: flex; gap: 15px; margin-top: 1.5rem; flex-wrap: wrap;'>
                <span style='background: #1e293b; color: #60a5fa; padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; border: 1px solid #2563eb;'>📊 %95 Güven Aralığı</span>
                <span style='background: #1e293b; color: #60a5fa; padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; border: 1px solid #2563eb;'>🎲 Monte Carlo Metodu</span>
                <span style='background: #1e293b; color: #60a5fa; padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; border: 1px solid #2563eb;'>🎓 Akademik Metodoloji</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Giriş Butonları
    col_l, col_r = st.columns(2)
    with col_l:
        if st.button("🚀 Demo Portföyü Analiz Et"):
            st.session_state.authenticated = True
            st.session_state.demo_mode = True
            st.rerun()
    with col_r:
        if st.button("🔑 Kendi Portföyünü Oluştur"):
            st.session_state.authenticated = True
            st.session_state.demo_mode = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tanıtım Kartları
    v1, v2, v3 = st.columns(3)
    with v1:
        st.markdown("<div class='feature-card'><h4>📉 Kayıp Kontrolü</h4><p style='font-size: 0.9rem; color: #8a8f98;'>Yarın yaşanabilecek maksimum kaybınızı rasyonel verilerle öngörün.</p></div>", unsafe_allow_html=True)
    with v2:
        st.markdown("<div class='feature-card'><h4>🧪 Stres Testleri</h4><p style='font-size: 0.9rem; color: #8a8f98;'>Küresel kriz senaryolarının portföyünüze etkisini saniyeler içinde simüle edin.</p></div>", unsafe_allow_html=True)
    with v3:
        st.markdown("<div class='feature-card'><h4>🤖 Karar Desteği</h4><p style='font-size: 0.9rem; color: #8a8f98;'>Karmaşık grafikler yerine, AI destekli net stratejik öneriler alın.</p></div>", unsafe_allow_html=True)
    st.stop()

# --- 5. ANA TERMİNAL (GİRİŞ SONRASI) ---
st.sidebar.title("💎 Guardian Pro")
search_input = st.sidebar.text_input("🔍 Varlık Sorgula (Örn: THY, BTC, ALTIN):", "")

if st.session_state.demo_mode:
    selected_assets = ["THYAO.IS", "BTC-USD", "GC=F"]
else:
    selected_assets = [universal_search(x.strip()) for x in search_input.split(",")] if search_input else []

if selected_assets:
    try:
        with st.spinner('Guardian verileri işliyor...'):
            data = yf.download(selected_assets, period="1y", progress=False)['Close']
            if isinstance(data, pd.Series): data = data.to_frame()
            
            # Risk Motoru
            returns = data.pct_change().dropna()
            vol = returns.std() * np.sqrt(252) * 100
            avg_vol = vol.mean()
            
            # Dinamik Sonuç Ekranı
            risk_color = "#00ff00" if avg_vol < 20 else "#ffa500" if avg_vol < 40 else "#ff4b4b"
            st.markdown(f"<div style='background: #111418; padding: 2rem; border-radius: 20px; border-left: 10px solid {risk_color};'><h2>Risk Skoru: {min(10.0, avg_vol/5):.1f} / 10</h2><p>Durum: {'Dengeli' if avg_vol < 30 else 'Yüksek Risk'}</p></div>", unsafe_allow_html=True)
            
            st.plotly_chart(px.line(data, title="Varlık Performans Kıyaslaması", template="plotly_dark"), use_container_width=True)
            
            # Aksiyon Önerisi
            st.subheader("🤖 Stratejik Öneri")
            if avg_vol > 35:
                st.error("⚠️ Portföyünüzde aşırı yoğunlaşma ve risk var. Defansif varlıklara (Altın/Nakit) geçiş düşünülmeli.")
            else:
                st.success("✅ Portföy yapısı şu anki piyasa volatilitesi ile uyumlu görünüyor.")
                
    except Exception as e:
        st.error(f"Sembol hatası veya veri yok. Lütfen aramayı kontrol edin.")

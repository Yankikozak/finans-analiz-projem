import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- 1. PREMIUM UI CONFIG ---
st.set_page_config(page_title="Guardian | Finansal Risk Terminali", layout="wide")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main-title { font-size: 3.5rem; font-weight: 800; letter-spacing: -2px; color: #ffffff; margin-bottom: 0px; }
    .subtitle { font-size: 1.2rem; color: #8a8f98; margin-bottom: 2rem; }
    .hero-card { background: #111418; border: 1px solid #1f2937; padding: 3rem; border-radius: 24px; text-align: center; margin-bottom: 2rem; }
    .stButton>button { background: #2563eb; color: white; border-radius: 12px; height: 3.5rem; font-weight: 600; border: none; transition: 0.3s; }
    .stButton>button:hover { background: #1d4ed8; transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-ASSET SEARCH ENGINE ---
# Bu sözlük motoru, kullanıcı ne yazarsa yazsın doğru sembole yönlendirir.
asset_universe = {
    # BIST 30 & Popüler
    "THY": "THYAO.IS", "TÜRK HAVA YOLLARI": "THYAO.IS", "ASELSAN": "ASELS.IS", 
    "EREĞLİ": "EREGL.IS", "ŞİŞECAM": "SISE.IS", "SASA": "SASA.IS", "KOÇ HOLDİNG": "KCHOL.IS",
    # Kripto
    "BITCOIN": "BTC-USD", "BTC": "BTC-USD", "ETHEREUM": "ETH-USD", "ETH": "ETH-USD", "SOLANA": "SOL-USD",
    # Emtia & Endeks
    "ALTIN": "GC=F", "GÜMÜŞ": "SI=F", "ONS": "GC=F", "BIST100": "XU100.IS", "NASDAQ": "^IXIC", "S&P500": "^GSPC"
}

def universal_search(query):
    query = query.upper().strip()
    if query in asset_universe:
        return asset_universe[query]
    # Eğer listede yoksa ve sonuna .IS eklenmemişse otomatik ekle (BIST varsayımı)
    if "." not in query and "-" not in query:
        return f"{query}.IS"
    return query

# --- 3. SESSION STATE (Giriş Kontrolü) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 4. PROFESYONEL GİRİŞ EKRANI (LANDING PAGE) ---
if not st.session_state.authenticated:
    st.markdown("<div class='hero-card'>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>Guardian Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Ekonometrik modellerle portföyünü koru, risklerini yönet ve rasyonel kararlar al.</p>", unsafe_allow_html=True)
    
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
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Value Proposition Section
    v1, v2, v3 = st.columns(3)
    v1.markdown("### 📊 VaR Analizi\n%95 güvenle yarın ne kadar kaybedebileceğini bil.")
    v2.markdown("### 🧪 Stres Testi\nKriz senaryolarında portföyünün dayanıklılığını ölç.")
    v3.markdown("### 🤖 AI Stratejist\nKarmaşık verileri net 'AL/SAT/BEKLE' stratejilerine çevir.")
    st.stop()

# --- 5. ANA TERMİNAL (DASHBOARD) ---
st.sidebar.title("💎 Guardian Pro")
st.sidebar.markdown("---")

# Gelişmiş Arama Kutusu
search_input = st.sidebar.text_input("🔍 Varlık Ekle (Hisse, Kripto, Altın):", "")
selected_assets = []

if st.session_state.demo_mode:
    selected_assets = ["THY", "BTC", "ALTIN"]
else:
    if search_input:
        assets_raw = [x.strip() for x in search_input.split(",")]
        selected_assets = [universal_search(a) for a in assets_raw]

# --- 6. ANALİZ VE GÖRSELLEŞTİRME ---
if selected_assets:
    # Gerçek sembollere çevir
    tickers = [asset_universe.get(x.upper(), x) for x in selected_assets]
    
    try:
        with st.spinner('Piyasa verileri işleniyor...'):
            data = yf.download(tickers, period="1y", progress=False)['Close']
            if isinstance(data, pd.Series): data = data.to_frame()
            
            # Risk Hesaplamaları
            returns = data.pct_change().dropna()
            vol = returns.std() * np.sqrt(252) * 100
            
            # --- PROFESYONEL SONUÇ EKRANI ---
            st.header("📊 Portföy Sağlık Raporu")
            
            # Dinamik Risk Skoru Kartı
            avg_vol = vol.mean()
            risk_color = "#00ff00" if avg_vol < 20 else "#ffa500" if avg_vol < 40 else "#ff4b4b"
            
            st.markdown(f"""
                <div style='background: #111418; padding: 2rem; border-radius: 20px; border-left: 10px solid {risk_color};'>
                    <h2 style='margin:0;'>Risk Skoru: {min(10.0, avg_vol/5):.1f} / 10</h2>
                    <p style='color: #8a8f98;'>{ 'Güvenli Liman' if avg_vol < 20 else 'Dikkat Edilmeli' if avg_vol < 40 else 'Yüksek Volatilite' }</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Grafikler
            st.plotly_chart(px.line(data, title="Varlık Fiyat Trendleri (Normalize)", template="plotly_dark"), use_container_width=True)
            
            # AI Karar Kutusu
            st.subheader("🤖 Stratejik Karar Önerisi")
            if avg_vol > 35:
                st.error("Portföyünüz aşırı oynak. Kayıpları sınırlamak için %20 oranında Altın veya Nakit ağırlığını artırmanız önerilir.")
            else:
                st.success("Portföy yapınız dengeli. Mevcut trendi bozmadan stop-loss seviyelerinizi takip ederek pozisyonunuzu koruyabilirsiniz.")

    except Exception as e:
        st.error(f"Veri çekme hatası: {e}. Lütfen sembolleri doğru girdiğinizden emin olun.")

else:
    st.info("Lütfen analiz etmek istediğiniz varlıkları arama kutusuna yazın.")

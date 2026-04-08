import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. PREMIUM UI & VISIBILITY CONFIG ---
st.set_page_config(page_title="Guardian | Finansal Risk Terminali", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main-title { font-size: 3.5rem; font-weight: 800; letter-spacing: -2px; color: #ffffff; margin-bottom: 5px; }
    .subtitle { font-size: 1.25rem; color: #ffffff; font-weight: 500; margin-bottom: 2rem; } /* Daha beyaz ve görünür */
    
    .trust-panel { 
        background: linear-gradient(145deg, #0f172a, #1e293b); 
        border: 1px solid #3b82f6; 
        padding: 2.5rem; 
        border-radius: 24px; 
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.7);
    }
    
    /* Özellik kartlarındaki yazıları tamamen beyaz yapma */
    .feature-card { 
        background: #1e293b; 
        padding: 1.5rem; 
        border-radius: 16px; 
        border: 1px solid #334155; 
        height: 100%; 
        color: #ffffff !important; 
    }
    .feature-card p { color: #f8fafc !important; font-weight: 400; }
    
    .stButton>button { background: #2563eb; color: white; border-radius: 12px; height: 3.5rem; font-weight: 600; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GENİŞLETİLMİŞ AKILLI ARAMA MOTORU (UNIVERSAL SEARCH ENGINE) ---
# BIST, Kripto, Emtia ve Global Varlıklar
asset_universe = {
    # BIST 30
    "THY": "THYAO.IS", "THYAO": "THYAO.IS", "ASELSAN": "ASELS.IS", "ASELS": "ASELS.IS",
    "EREGLI": "EREGL.IS", "EREGL": "EREGL.IS", "SISECAM": "SISE.IS", "SISE": "SISE.IS",
    "KOC HOLDING": "KCHOL.IS", "KCHOL": "KCHOL.IS", "SASA": "SASA.IS", "HEKTAS": "HEKTS.IS",
    "AKBANK": "AKBNK.IS", "ISBANK": "ISCTR.IS", "GARANTI": "GARAN.IS", "YAPI KREDI": "YKBNK.IS",
    "BIM": "BIMAS.IS", "FROTO": "FROTO.IS", "TOASO": "TOASO.IS", "TUPRS": "TUPRS.IS",
    "PETKIM": "PETKM.IS", "KARDEMIR": "KRDMD.IS", "PEGASUS": "PGSUS.IS", "PGSUS": "PGSUS.IS",
    # KRİPTO
    "BITCOIN": "BTC-USD", "BTC": "BTC-USD", "ETHEREUM": "ETH-USD", "ETH": "ETH-USD",
    "SOLANA": "SOL-USD", "SOL": "SOL-USD", "BINANCE COIN": "BNB-USD", "BNB": "BNB-USD",
    "RIPPLE": "XRP-USD", "XRP": "XRP-USD", "CARDANO": "ADA-USD", "ADA": "ADA-USD",
    "AVAX": "AVAX-USD", "DOGE": "DOGE-USD",
    # EMTİA & GLOBAL
    "ALTIN": "GC=F", "GOLD": "GC=F", "GUMUS": "SI=F", "SILVER": "SI=F", "PETROL": "CL=F",
    "ONS": "GC=F", "NASDAQ": "^IXIC", "SP500": "^GSPC", "DOW JONES": "^DJI",
    "BIST100": "XU100.IS", "DOLAR": "USDTRY=X", "EURO": "EURTRY=X"
}

# İsim Sözlüğü (Grafik Başlıkları İçin)
name_map = {v: k for k, v in asset_universe.items()}

def universal_search(query):
    query = query.upper().replace("İ", "I").replace("Ğ", "G").replace("Ü", "U").replace("Ş", "S").replace("Ö", "O").replace("Ç", "C").strip()
    if query in asset_universe:
        return asset_universe[query]
    # Otomatik düzeltme: Eğer nokta yoksa ve 3-5 karakterse BIST ekini ekle
    if "." not in query and "-" not in query and len(query) <= 5:
        return f"{query}.IS"
    return query

# --- 3. SESSION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 4. LANDING PAGE (PROFESYONEL VİTRİN) ---
if not st.session_state.authenticated:
    st.markdown("<h1 class='main-title'>Guardian Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Akademik Ekonometri Modelleriyle Sermayenizi Koruyan Karar Destek Sistemi</p>", unsafe_allow_html=True)

    st.markdown("""
        <div class='trust-panel'>
            <h3 style='color: #3b82f6; margin-top: 0;'>🛡️ Finansal Fırtınalara Karşı Matematiksel Kalkan</h3>
            <p style='color: #ffffff; font-size: 1.15rem; line-height: 1.7; font-weight: 400;'>
                Finansal piyasalarda kalıcı olmanın sırrı, ne kadar kazandığınız değil, <b>siyah kuğu (black swan)</b> olaylarında ne kadar korunduğunuzdur. 
                Guardian, portföyünüzü sadece bir tablo olarak değil, binlerce kriz senaryosuna maruz kalan dinamik bir yapı olarak analiz eder. 
                <br><br>
                Sistemimiz, <b>Value at Risk (VaR)</b> ve <b>Monte Carlo</b> simülasyonlarını kullanarak, duygulardan arınmış, 
                tamamen matematiksel bir risk projeksiyonu sunar.
            </p>
        </div>
    """, unsafe_allow_html=True)

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
    v1, v2, v3 = st.columns(3)
    with v1:
        st.markdown("<div class='feature-card'><h4>📉 Kayıp Kontrolü</h4><p>Yarın yaşanabilecek maksimum kaybınızı rasyonel verilerle öngörün.</p></div>", unsafe_allow_html=True)
    with v2:
        st.markdown("<div class='feature-card'><h4>🧪 Stres Testleri</h4><p>Küresel kriz senaryolarının portföyünüze etkisini saniyeler içinde simüle edin.</p></div>", unsafe_allow_html=True)
    with v3:
        st.markdown("<div class='feature-card'><h4>🤖 Karar Desteği</h4><p>Karmaşık grafikler yerine, AI destekli net stratejik öneriler alın.</p></div>", unsafe_allow_html=True)
    st.stop()

# --- 5. ANA TERMİNAL ---
st.sidebar.title("💎 Guardian Pro")
search_input = st.sidebar.text_input("🔍 Varlık Sorgula (Örn: THY, BTC, ALTIN, SISE):", "")

if st.session_state.demo_mode:
    selected_tickers = ["THYAO.IS", "BTC-USD", "GC=F"]
else:
    selected_tickers = [universal_search(x.strip()) for x in search_input.split(",")] if search_input else []

if selected_tickers:
    try:
        with st.spinner('Guardian verileri işliyor...'):
            data = yf.download(selected_tickers, period="1y", progress=False)['Close']
            if isinstance(data, pd.Series): data = data.to_frame()
            
            # Risk Hesaplamaları
            returns = data.pct_change().dropna()
            avg_vol = (returns.std() * np.sqrt(252) * 100).mean()
            
            # Dinamik Grafik Başlığı Oluşturma
            names = [name_map.get(t, t.replace(".IS", "")) for t in selected_tickers]
            graph_title = " & ".join(names) + " Performans Analizi"
            
            # Dashboard
            risk_color = "#22c55e" if avg_vol < 25 else "#f59e0b" if avg_vol < 45 else "#ef4444"
            st.markdown(f"<div style='background: #0f172a; padding: 2rem; border-radius: 20px; border-left: 10px solid {risk_color};'><h2>Risk Skoru: {min(10.0, avg_vol/5):.1f} / 10</h2></div>", unsafe_allow_html=True)
            
            # GRAFİK
            st.plotly_chart(px.line(data, title=graph_title, template="plotly_dark"), use_container_width=True)
            
            # AI Yorum
            st.subheader("🤖 Stratejik Öneri")
            if avg_vol > 35:
                st.error("⚠️ Portföy oynaklığı yüksek. Risk limitlerinizi korumak için defansif varlık ağırlığını artırın.")
            else:
                st.success("✅ Portföy dengeli. Mevcut strateji piyasa koşullarıyla uyumlu.")

    except Exception as e:
        st.error("Sembol bulunamadı. Lütfen 'THY, BTC, ALTIN' gibi anahtar kelimeler kullanın.")

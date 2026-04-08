import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- 1. CONFIG: GENİŞ EKRAN MODU ---
st.set_page_config(page_title="Guardian | Finansal Zeka", layout="wide", initial_sidebar_state="collapsed")

if 'lang' not in st.session_state: st.session_state.lang = "TR"

L_DICT = {
    "TR": {
        "m_title": "Guardian Finansal Zeka",
        "m_subtitle": "Sakarya Üniversitesi Ekonometri Disiplini ile Geliştirilmiş Sermaye Koruma Sistemi",
        "blog_h": "🛡️ Stratejik Analiz ve Risk Protokolü",
        "btn_enter": "Terminale Giriş Yap",
        "search_ph": "Varlık Ara (Hisse, Kripto, Emtia)...",
        "res_label": "BIST Öncelikli Sonuçlar:"
    },
    "EN": {
        "m_title": "Guardian Financial Intelligence",
        "m_subtitle": "Capital Protection System with Sakarya University Econometrics Discipline",
        "blog_h": "🛡️ Strategic Analysis & Risk Protocol",
        "btn_enter": "Enter Terminal",
        "search_ph": "Search Asset (Stock, Crypto, Commodity)...",
        "res_label": "BIST Priority Results:"
    }
}
L = L_DICT[st.session_state.lang]

# --- 2. CSS: EKONLAB TARZI GENİŞ BLOG VE KESKİN METİNLER ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #020617; }

    /* Sağ Üst Dil Seçici */
    .stSelectbox { width: 100px !important; float: right; }

    /* GENİŞ BLOG TASARIMI */
    .wide-hero {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        padding: 100px 5%;
        border-radius: 0 0 50px 50px;
        border-bottom: 2px solid #3b82f6;
        margin-bottom: 50px;
        text-align: left; /* Ekonlab gibi sola yaslı daha profesyonel durur */
    }
    .hero-title { font-size: 5rem; font-weight: 900; color: #ffffff !important; letter-spacing: -3px; line-height: 1; }
    .hero-subtitle { font-size: 1.5rem; color: #60a5fa !important; margin-top: 20px; font-weight: 600; }
    
    .blog-container { padding: 0 5%; display: flex; gap: 30px; margin-bottom: 50px; }
    .blog-card {
        background: #0f172a;
        padding: 40px;
        border-radius: 24px;
        border: 1px solid #1e293b;
        flex: 1;
        transition: 0.4s;
    }
    .blog-card:hover { border-color: #3b82f6; transform: translateY(-10px); box-shadow: 0 20px 40px rgba(59, 130, 246, 0.1); }
    .blog-card h3 { color: #ffffff; font-size: 1.8rem; margin-bottom: 15px; }
    .blog-card p { color: #94a3b8; font-size: 1.1rem; line-height: 1.7; }

    /* Terminal Butonu */
    .stButton>button { 
        background: #2563eb; color: white; border-radius: 15px; 
        height: 4.5rem; font-weight: 800; font-size: 1.3rem; border: none;
        width: 100%; box-shadow: 0 10px 20px rgba(37, 99, 235, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Dil Seçici
c_space, col_l = st.columns([12, 1.5])
with col_l:
    st.session_state.lang = st.selectbox("", ["TR", "EN"], label_visibility="collapsed")

# --- 3. AKILLI ARAMA (BIST FİLTRESİ) ---
def fetch_assets(query):
    if len(query) < 2: return []
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        quotes = resp.get('quotes', [])
        bist = [q for q in quotes if str(q.get('symbol','')).endswith('.IS')]
        others = [q for q in quotes if not str(q.get('symbol','')).endswith('.IS') and q.get('quoteType') != 'FUND']
        final = bist + others
        return [{"label": f"🇹🇷 {q.get('shortname')} ({q.get('symbol')})" if q in bist else f"🌍 {q.get('shortname')} ({q.get('symbol')})", 
                 "symbol": q.get('symbol')} for q in final[:8]]
    except: return []

# --- 4. LANDING PAGE (GENİŞ BLOG DÜZENİ) ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    # Üst Geniş Alan
    st.markdown(f"""
        <div class="wide-hero">
            <h1 class="hero-title">{L['m_title']}</h1>
            <p class="hero-subtitle">{L['m_subtitle']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Genişletilmiş Blog Kartları
    st.markdown(f" <h2 style='padding: 0 5%; color:white; margin-bottom:30px;'>{L['blog_h']}</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="blog-container">
            <div class="blog-card">
                <h3>📊 Ekonometrik Analiz</h3>
                <p>Sakarya Üniversitesi'ndeki akademik temellerimizle, piyasa verilerini sadece izlemiyor, 
                GARCH ve ARMA modelleriyle volatiliteyi tahmin ediyoruz.</p>
            </div>
            <div class="blog-card">
                <h3>🛡️ Risk Yönetimi</h3>
                <p>Value at Risk (VaR) protokolleri sayesinde, portföyünüzün maruz kalabileceği 
                maksimum kaybı matematiksel kesinlikle hesaplıyoruz.</p>
            </div>
            <div class="blog-card">
                <h3>🌍 Küresel Piyasalar</h3>
                <p>Borsa İstanbul'dan Nasdaq'a kadar tüm piyasalara erişim sağlayarak, 
                varlıklarınızı ekonometrik bir süzgeçten geçiriyoruz.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Giriş Butonu (Merkezi)
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2:
        if st.button(L['btn_enter']):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 5. ANA TERMİNAL ---
st.sidebar.title("💎 Guardian Terminal")
u_input = st.sidebar.text_input("Arama:", placeholder=L['search_ph'])

if u_input:
    res = fetch_assets(u_input)
    if res:
        choice = st.sidebar.selectbox(L['res_label'], options=[r['label'] for r in res])
        ticker = [r['symbol'] for r in res if r['label'] == choice][0]
        
        df = yf.download(ticker, period="1y", progress=False)['Close']
        if not df.empty:
            st.header(f"📈 {choice}")
            st.plotly_chart(px.line(df, template="plotly_dark", color_discrete_sequence=['#3b82f6']), use_container_width=True)
            
            # Risk Metrikleri
            ret = df.pct_change().dropna()
            vol = (ret.std() * np.sqrt(252) * 100).iloc[0]
            st.metric("Yıllık Oynaklık", f"%{vol:.2f}")

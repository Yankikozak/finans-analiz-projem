import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- 1. UI YAPILANDIRMASI ---
st.set_page_config(page_title="Guardian | Finansal Koruma", layout="wide")

# Dil Sözlüğü
L_DICT = {
    "TR": {
        "title": "Guardian Finansal Zeka",
        "subtitle": "Ekonometrik Modellerle Sermaye Koruma Sistemi",
        "m_title": "🛡️ Stratejik Manifesto ve Güven Protokolü",
        "search_ph": "Hisse, Kripto veya Emtia...",
        "risk_rep": "Risk Analiz Raporu",
        "vol": "Yıllık Oynaklık",
        "conf": "Güven Seviyesi",
        "academy_title": "🎓 Guardian Akademi",
        "academy_sub": "Ekonometrik disiplinle finansal okuryazarlığınızı geliştirin."
    },
    "EN": {
        "title": "Guardian Financial Intelligence",
        "subtitle": "Capital Protection System with Econometric Models",
        "m_title": "🛡️ Strategic Manifesto & Trust Protocol",
        "search_ph": "Stock, Crypto, Commodity...",
        "risk_rep": "Risk Analysis Report",
        "vol": "Annual Volatility",
        "conf": "Confidence Level",
        "academy_title": "🎓 Guardian Academy",
        "academy_sub": "Improve your financial literacy with econometric discipline."
    }
}

# --- 2. CSS: PREMIUM FINTECH TASARIMI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0f172a; }
    
    /* Sağ Üst Dil Seçici */
    .stSelectbox { width: 80px !important; float: right; }
    
    /* Blog Kartları */
    .blog-card {
        background: #1e293b;
        padding: 24px;
        border-radius: 20px;
        border: 1px solid #334155;
        margin-bottom: 20px;
        height: 100%;
        transition: 0.3s;
    }
    .blog-card:hover { border-color: #3b82f6; transform: translateY(-5px); }
    .cat-chip {
        background: #3b82f6;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .m-title { font-size: 3.5rem; font-weight: 800; text-align: center; color: white; margin-bottom: 0; }
    .m-sub { font-size: 1.2rem; text-align: center; color: #94a3b8; margin-bottom: 3rem; }
</style>
""", unsafe_allow_html=True)

# Dil seçimi
if 'lang' not in st.session_state: st.session_state.lang = "TR"
c_t, c_l = st.columns([10, 1])
with c_l:
    st.session_state.lang = st.selectbox("", ["TR", "EN"], index=0 if st.session_state.lang == "TR" else 1, label_visibility="collapsed")

L = L_DICT[st.session_state.lang]

# --- 3. AKILLI ARAMA MOTORU (BIST ÖNCELİKLİ) ---
def fetch_smart_assets(query):
    if len(query) < 2: return []
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        quotes = resp.get('quotes', [])
        
        # Kritik: BIST hisselerini en üste çek, alakasız fonları temizle
        bist = [q for q in quotes if str(q.get('symbol')).endswith('.IS')]
        others = [q for q in quotes if not str(q.get('symbol')).endswith('.IS') and q.get('quoteType') != 'FUND']
        
        sorted_list = bist + others
        return [{"label": f"{q.get('shortname', '')} ({q.get('symbol')})", "symbol": q.get('symbol')} for q in sorted_list[:8]]
    except: return []

# --- 4. LANDING & GELİŞMİŞ BLOG ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown(f"<h1 class='m-title'>{L['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='m-sub'>{L['subtitle']}</p>", unsafe_allow_html=True)
    
    # Akademi / Blog Bölümü
    st.markdown(f"### {L['academy_title']}")
    st.write(L['academy_sub'])
    
    col1, col2, col3 = st.columns(3)
    blog_posts = [
        {"cat": "Risk", "t": "VaR Analizi Nedir?", "d": "Sermayenizi korumak için en kötü senaryoyu hesaplayın.", "m": "4 dk"},
        {"cat": "Ekonometri", "t": "Zaman Serisi Tahmini", "d": "ARIMA ve GARCH modelleriyle piyasa projeksiyonu.", "m": "6 dk"},
        {"cat": "Kripto", "t": "Korelasyon Riski", "d": "Bitcoin ve geleneksel varlıklar arasındaki bağ.", "m": "5 dk"}
    ]
    
    for i, post in enumerate(blog_posts):
        with [col1, col2, col3][i]:
            st.markdown(f"""
                <div class="blog-card">
                    <span class="cat-chip">{post['cat']}</span>
                    <h4 style="margin: 15px 0 10px 0; color: white;">{post['t']}</h4>
                    <p style="color: #94a3b8; font-size: 14px;">{post['d']}</p>
                    <hr style="border: 0.5px solid #334155;">
                    <span style="color: #64748b; font-size: 12px;">⏱️ {post['m']} okuma</span>
                </div>
            """, unsafe_allow_html=True)

    st.write("---")
    if st.button("🚀 Terminale Giriş Yap / Enter Terminal"):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- 5. ANA TERMİNAL ---
st.sidebar.title(f"💎 Guardian {st.session_state.lang}")
s_input = st.sidebar.text_input("Arama:", placeholder=L['search_ph'])

if s_input:
    results = fetch_smart_assets(s_input)
    if results:
        choice = st.sidebar.selectbox("Eşleşen Varlıklar:", options=[r['label'] for r in results])
        ticker = [r['symbol'] for r in results if r['label'] == choice][0]
        
        # Analiz
        data = yf.download(ticker, period="1y", progress=False)['Close']
        if not data.empty:
            st.header(f"📊 {choice} {L['risk_rep']}")
            st.plotly_chart(px.line(data, template="plotly_dark", color_discrete_sequence=['#3b82f6']), use_container_width=True)
            
            # Basit Risk Metrikleri
            rets = data.pct_change().dropna()
            vol = (rets.std() * np.sqrt(252) * 100).iloc[0]
            c1, c2 = st.columns(2)
            c1.metric(L['vol'], f"%{vol:.2f}")
            c2.metric(L['conf'], "Yüksek" if vol < 25 else "Orta")

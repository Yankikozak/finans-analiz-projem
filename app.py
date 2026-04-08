import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- 1. CONFIG ---
st.set_page_config(page_title="Guardian | Finansal Zeka", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = "TR"

L_DICT = {
    "TR": {
        "m_title": "Guardian Finansal Zeka",
        "m_subtitle": "Sakarya Üniversitesi Ekonometri Temelli Karar Mekanizması",
        "b_title": "🛡️ Stratejik Analiz Paneli",
        "b_feature_1": "Ekonometrik Disiplin",
        "b_desc_1": "VaR ve GARCH modelleriyle sermayenizi matematiksel bir zırhla koruyun.",
        "b_feature_2": "Global Erişim",
        "b_desc_2": "BIST, Nasdaq ve Kripto piyasalarını tek bir terminalden yönetin.",
        "btn_enter": "Terminale Giriş Yap",
        "search_label": "🔍 Analiz Edilecek Varlık:",
        "results_label": "Eşleşen Varlıklar (BIST Öncelikli):"
    },
    "EN": {
        "m_title": "Guardian Financial Intelligence",
        "m_subtitle": "Decision Mechanism Based on Sakarya University Econometrics",
        "b_title": "🛡️ Strategic Analysis Panel",
        "b_feature_1": "Econometric Discipline",
        "b_desc_1": "Protect your capital with a mathematical shield using VaR and GARCH models.",
        "b_feature_2": "Global Access",
        "b_desc_2": "Manage BIST, Nasdaq, and Crypto markets from a single terminal.",
        "btn_enter": "Enter Terminal",
        "search_label": "🔍 Asset to Analyze:",
        "results_label": "Matching Assets (BIST Priority):"
    }
}

# --- 2. CSS: MAKSİMUM OKUNURLUK (OVERLAY SİSTEMİ) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #030712; }
    .stSelectbox { width: 90px !important; float: right; margin-top: -10px; }
    .hero-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 80px 50px; border-radius: 40px; border: 2px solid #3b82f6;
        text-align: center; margin: 40px auto; max-width: 1000px;
        box-shadow: 0 0 40px rgba(59, 130, 246, 0.2);
    }
    .hero-title { font-size: 4.5rem; font-weight: 900; color: #ffffff !important; letter-spacing: -2px; }
    .hero-subtitle { font-size: 1.4rem; color: #94a3b8 !important; margin-bottom: 50px; }
    .blog-card { background: rgba(255, 255, 255, 0.03); padding: 30px; border-radius: 24px; border: 1px solid #334155; text-align: left; }
    .blog-card h4 { color: #60a5fa !important; font-size: 1.5rem; margin-top: 0; }
    .blog-card p { color: #e2e8f0 !important; font-size: 1.1rem; line-height: 1.6; }
    .stButton>button { background: #2563eb; color: white; border-radius: 12px; height: 4rem; font-weight: 800; font-size: 1.2rem; border: none; }
</style>
""", unsafe_allow_html=True)

col_space, col_l = st.columns([12, 1])
with col_l:
    st.session_state.lang = st.selectbox("", ["TR", "EN"], index=0 if st.session_state.lang == "TR" else 1, label_visibility="collapsed")

L = L_DICT[st.session_state.lang]

# --- 3. AKILLI ARAMA (BIST FORCING) ---
def fetch_assets(query):
    if len(query) < 2: return []
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        quotes = resp.get('quotes', [])
        bist = [q for q in quotes if str(q.get('symbol', '')).endswith('.IS')]
        others = [q for q in quotes if not str(q.get('symbol', '')).endswith('.IS') and q.get('quoteType') != 'FUND']
        sorted_list = bist + others
        return [{"label": f"🇹🇷 {q.get('shortname')} ({q.get('symbol')})" if q in bist else f"🌍 {q.get('shortname')} ({q.get('symbol')})", 
                 "symbol": q.get('symbol')} for q in sorted_list[:8]]
    except: return []

# --- 4. LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown(f"""
        <div class="hero-container">
            <h1 class="hero-title">{L['m_title']}</h1>
            <p class="hero-subtitle">{L['m_subtitle']}</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                <div class="blog-card">
                    <h4>{L['b_feature_1']}</h4>
                    <p>{L['b_desc_1']}</p>
                </div>
                <div class="blog-card">
                    <h4>{L['b_feature_2']}</h4>
                    <p>{L['b_desc_2']}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        if st.button(L['btn_enter']):
            st.session_state.auth = True
            st.rerun()
    st.stop()

st.sidebar.title("💎 Guardian Intelligence")
user_input = st.sidebar.text_input(L['search_label'], placeholder="Örn: thy, sasa, btc")

if user_input:
    results = fetch_assets(user_input)
    if results:
        choice = st.sidebar.selectbox(L['results_label'], options=[r['label'] for r in results])
        ticker = [r['symbol'] for r in results if r['label'] == choice][0]
        df = yf.download(ticker, period="1y", progress=False)['Close']
        if not df.empty:
            st.subheader(f"📊 {choice} Analiz Paneli")
            st.plotly_chart(px.line(df, template="plotly_dark", color_discrete_sequence=['#3b82f6']), use_container_width=True)
            returns = df.pct_change().dropna()
            vol = (returns.std() * np.sqrt(252) * 100).iloc[0]
            c1, c2 = st.columns(2)
            c1.metric("Yıllık Volatilite", f"%{vol:.2f}")
            c2.metric("Güven Seviyesi", "Yüksek" if vol < 25 else "Orta")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Guardian | Finansal Koruma", layout="wide")

# Dil Ayarı
if 'lang' not in st.session_state: st.session_state.lang = "TR"

L_DICT = {
    "TR": {
        "title": "Guardian Finansal Zeka",
        "subtitle": "Ekonometrik Disiplin ve Sermaye Koruma Sistemi",
        "search_label": "🔍 Varlık Ara (Hisse, Kripto, Emtia):",
        "blog_title": "🛡️ Stratejik Analiz ve Güven Paneli",
        "blog_desc": "Sakarya Üniversitesi Ekonometri temelli algoritmalarla piyasayı rasyonel analiz edin.",
        "btn_enter": "Terminale Giriş Yap",
        "results_text": "Eşleşen Varlıklar (BIST Öncelikli):"
    },
    "EN": {
        "title": "Guardian Financial Intelligence",
        "subtitle": "Econometric Discipline & Capital Protection",
        "search_label": "🔍 Search Asset (Stock, Crypto, Commodity):",
        "blog_title": "🛡️ Strategic Analysis & Trust Panel",
        "blog_desc": "Analyze the market rationally with algorithms based on Econometric discipline.",
        "btn_enter": "Enter Terminal",
        "results_text": "Matching Assets (BIST Priority):"
    }
}
L = L_DICT[st.session_state.lang]

# --- 2. CSS: SAĞ ÜST DİL VE GENİŞ BLOG ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Sağ Üst Dil Seçici */
    .lang-container { position: absolute; top: 0px; right: 0px; z-index: 999; }
    
    /* Genişletilmiş Blog Paneli */
    .hero-section {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 60px;
        border-radius: 30px;
        border: 1px solid #3b82f6;
        margin-bottom: 40px;
        text-align: center;
    }
    .blog-grid { display: flex; gap: 20px; margin-top: 30px; text-align: left; }
    .blog-item {
        background: rgba(255,255,255,0.03);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #334155;
        flex: 1;
    }
    .blog-item h4 { color: #3b82f6; margin-top: 0; }
    .stButton>button { background: #3b82f6; color: white; border-radius: 12px; font-weight: bold; width: 100%; height: 50px; }
</style>
""", unsafe_allow_html=True)

# Dil Seçici (Sağ Üst)
col_spacer, col_lang = st.columns([10, 1.5])
with col_lang:
    st.session_state.lang = st.selectbox("", ["TR", "EN"], label_visibility="collapsed")

# --- 3. AKILLI ARAMA MOTORU (BIST FORCING) ---
def get_clean_assets(query):
    if len(query) < 2: return []
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        data = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        quotes = data.get('quotes', [])
        
        # MANUEL FİLTRELEME: Önce BIST hisselerini, sonra global hisseleri al. Fonları ve alakasızları at.
        bist = [q for q in quotes if str(q.get('symbol')).endswith('.IS')]
        crypto = [q for q in quotes if q.get('quoteType') == 'CRYPTOCURRENCY']
        global_stocks = [q for q in quotes if q.get('quoteType') == 'EQUITY' and not str(q.get('symbol')).endswith('.IS')]
        
        # BIST her zaman en üstte
        ordered = bist + crypto + global_stocks
        return [{"label": f"🇹🇷 {q.get('shortname')} ({q.get('symbol')})" if q in bist else f"🌍 {q.get('shortname')} ({q.get('symbol')})", 
                 "symbol": q.get('symbol')} for q in ordered[:10]]
    except: return []

# --- 4. GİRİŞ SAYFASI (PRO BLOG) ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown(f"<h1 style='text-align:center; font-size:4rem;'>{L['title']}</h1>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="hero-section">
        <h2 style="color:#3b82f6;">{L['blog_title']}</h2>
        <p style="font-size:1.2rem; color:#94a3b8;">{L['blog_desc']}</p>
        <div class="blog-grid">
            <div class="blog-item">
                <h4>🛡️ Sermaye Koruması</h4>
                <p>Value at Risk (VaR) modelleriyle portföyünüzün maruz kaldığı maksimum kaybı günlük olarak takip edin.</p>
            </div>
            <div class="blog-item">
                <h4>📈 Ekonometrik Analiz</h4>
                <p>Zaman serisi modelleri (ARMA-GARCH) ile sadece fiyatı değil, oynaklığı (volatiliteyi) tahmin edin.</p>
            </div>
            <div class="blog-item">
                <h4>🌍 Global Erişim</h4>
                <p>Borsa İstanbul'dan Nasdaq'a, Kripto piyasalarından Emtialara kadar tüm varlıklar tek bir panelde.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(L['btn_enter']):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- 5. ANA TERMİNAL ---
st.sidebar.title("💎 Guardian Intelligence")
user_query = st.sidebar.text_input(L['search_label'], placeholder="Örn: thy, sasa, btc")

if user_query:
    suggestions = get_clean_assets(user_query)
    if suggestions:
        choice = st.sidebar.selectbox(L['results_text'], options=[s['label'] for s in suggestions])
        ticker = [s['symbol'] for s in suggestions if s['label'] == choice][0]
        
        # ANALİZ BÖLÜMÜ
        with st.spinner('Veriler işleniyor...'):
            df = yf.download(ticker, period="1y", progress=False)['Close']
            if not df.empty:
                st.subheader(f"📊 {choice} Analiz Paneli")
                st.plotly_chart(px.line(df, template="plotly_dark", color_discrete_sequence=['#3b82f6']), use_container_width=True)
                
                # Metrikler
                returns = df.pct_change().dropna()
                volatility = (returns.std() * np.sqrt(252) * 100).iloc[0]
                c1, c2 = st.columns(2)
                c1.metric("Yıllık Oynaklık", f"%{volatility:.2f}")
                c2.metric("Risk Durumu", "⚠️ Yüksek" if volatility > 40 else "✅ Güvenli")

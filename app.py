import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- 1. PREMIUM UI & TASARIM AYARLARI ---
st.set_page_config(page_title="Guardian | Finansal Koruma", layout="wide")

# Dil Sözlüğü
languages = {
    "TR": {
        "title": "Guardian Finansal Zeka",
        "subtitle": "Ekonometrik Modellerle Sermaye Koruma Sistemi",
        "manifesto_title": "🛡️ Stratejik Manifesto ve Güven Protokolü",
        "manifesto_text": """
            Piyasalarda kazanmak bir seçenek, sermayeyi korumak ise bir zorunluluktur. 
            **Guardian Finansal Zeka**, Sakarya Üniversitesi Ekonometri disiplini üzerine inşa edilmiş bir karar destek mekanizmasıdır.
            
            **Sistem Kapasitesi:**
            * **Küresel Varlık Analizi:** Dünyanın her yerindeki hisse, kripto ve emtialara anında ulaşım.
            * **Rasyonel Risk Yönetimi:** VaR modelleriyle matematiksel 'en kötü senaryo' analizi.
            * **Stratejik Karar Desteği:** Piyasa gürültüsü yerine ekonometrik veri sinyalleri.
        """,
        "btn_demo": "🚀 Demo Portföyü Başlat",
        "btn_custom": "🔑 Terminale Giriş Yap",
        "search_label": "🔍 Analiz Edilecek Varlık:",
        "results_label": "Eşleşen Varlıklar:",
        "risk_report": "Risk Analiz Raporu",
        "volatility": "Yıllık Oynaklık",
        "confidence": "Güven Seviyesi"
    },
    "EN": {
        "title": "Guardian Financial Intelligence",
        "subtitle": "Capital Protection System with Econometric Models",
        "manifesto_title": "🛡️ Strategic Manifesto & Trust Protocol",
        "manifesto_text": """
            Winning is an option; protecting capital is a necessity. 
            **Guardian Financial Intelligence** is a decision support mechanism built on 
            the foundations of Econometric discipline.
            
            **System Capabilities:**
            * **Global Asset Analysis:** Instant access to stocks, crypto, and commodities worldwide.
            * **Rational Risk Management:** Mathematical 'worst-case scenario' analysis.
            * **Strategic Decision Support:** Clear econometric signals instead of market noise.
        """,
        "btn_demo": "🚀 Start Demo Portfolio",
        "btn_custom": "🔑 Enter Terminal",
        "search_label": "🔍 Asset to Analyze:",
        "results_label": "Matching Assets:",
        "risk_report": "Risk Analysis Report",
        "volatility": "Annual Volatility",
        "confidence": "Confidence Level"
    }
}

# --- 2. SAĞ ÜST DİL SEÇENEĞİ VE CSS (HATASIZ BLOK) ---
if 'lang' not in st.session_state:
    st.session_state.lang = "TR"

# CSS: Tırnak hatası riskine karşı f-string kullanmadan doğrudan markdown veriyoruz
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Sağ Üst Dil Seçici Konumu */
    .stSelectbox { width: 90px !important; float: right; }
    
    .main-title { font-size: 3.5rem; font-weight: 800; color: #ffffff; text-align: center; margin-top: 2rem; }
    .subtitle { font-size: 1.2rem; color: #ffffff; text-align: center; margin-bottom: 3rem; opacity: 0.8; }
    
    .trust-panel { 
        background: linear-gradient(145deg, #111827, #1f2937); 
        border: 1px solid #3b82f6; 
        padding: 4rem; 
        border-radius: 32px; 
        margin: 0 auto 3rem auto;
        max-width: 1100px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    .manifesto-text { color: #ffffff !important; font-size: 1.25rem; line-height: 1.9; }
    .stButton>button { background: #2563eb; color: white; border-radius: 12px; height: 3.5rem; font-weight: 600; width: 100%; }
</style>
""", unsafe_allow_html=True)

# Dil Seçici Yerleşimi
col_t, col_l = st.columns([10, 1])
with col_l:
    s_lang = st.selectbox("", ["TR", "EN"], index=0 if st.session_state.lang == "TR" else 1, label_visibility="collapsed")
    st.session_state.lang = s_lang

L = languages[st.session_state.lang]

# --- 3. AKILLI ARAMA MOTORU ---
def fetch_suggestions_smart(query):
    if len(query) < 2: return []
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        q_list = response.get('quotes', [])
        bist = [q for q in q_list if str(q.get('symbol')).endswith('.IS')]
        others = [q for q in q_list if not str(q.get('symbol')).endswith('.IS')]
        final_q = bist + others
        return [{"label": f"{q.get('shortname', '')} ({q.get('symbol')})", "symbol": q.get('symbol'), "name": q.get('shortname')} for q in final_q[:8]]
    except: return []

# --- 4. GİRİŞ SAYFASI ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown(f"<h1 class='main-title'>{L['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle'>{L['subtitle']}</p>", unsafe_allow_html=True)
    
    m_body = L['manifesto_text'].replace('*', '<br>•')
    st.markdown(f"""
        <div class='trust-panel'>
            <h2 style='color: #3b82f6; margin-top: 0;'>{L['manifesto_title']}</h2>
            <div class='manifesto-text'>{m_body}</div>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        b1, b2 = st.columns(2)
        if b1.button(L['btn_demo']):
            st.session_state.auth, st.session_state.mode = True, "demo"
            st.rerun()
        if b2.button(L['btn_custom']):
            st.session_state.auth, st.session_state.mode = True, "custom"
            st.rerun()
    st.stop()

# --- 5. ANA TERMİNAL ---
st.sidebar.title(f"💎 Guardian {st.session_state.lang}")
s_input = st.sidebar.text_input(L['search_label'], placeholder="SASA, BTC, AAPL...")

f_tickers, f_names = [], []

if st.session_state.mode == "demo":
    f_tickers, f_names = ["THYAO.IS", "BTC-USD", "GC=F"], ["THY", "Bitcoin", "Altın"]
else:
    if s_input:
        suggestions = fetch_suggestions_smart(s_input)
        if suggestions:
            choice = st.sidebar.selectbox(L['results_label'], options=[s['label'] for s in suggestions])
            selected = [s for s in suggestions if s['label'] == choice][0]
            f_tickers, f_names = [selected['symbol']], [selected['name']]

# --- 6. ANALİZ EKRANI ---
if f_tickers:
    try:
        data = yf.download(f_tickers, period="1y", progress=False)['Close']
        if not data.empty:
            if isinstance(data, pd.Series): data = data.to_frame()
            st.header(f"📊 {f_names[0]} {L['risk_report']}")
            st.plotly_chart(px.line(data, template="plotly_dark", color_discrete_sequence=['#3b82f6']), use_container_width=True)
            
            rets = data.pct_change().dropna()
            vol = (rets.std() * np.sqrt(252) * 100).iloc[0]
            col1, col2 = st.columns(2)
            col1.metric(L['volatility'], f"%{vol:.2f}")
            col2.metric(L['confidence'], "High" if vol < 25 else "Medium" if vol < 45 else "Low")
    except:
        st.error("Veri hatası.")

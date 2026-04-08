import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- 1. DİL SÖZLÜĞÜ (MULTILANGUAGE) ---
languages = {
    "TR": {
        "title": "Guardian Intelligence",
        "subtitle": "Global Risk Yönetimi ve Ekonometrik Projeksiyon",
        "manifesto_title": "🛡️ Stratejik Manifesto",
        "manifesto_text": "Guardian, sadece veri gösteren bir panel değil; Sakarya Üniversitesi Ekonometri temelinde yükselen bir karar mekanizmasıdır. Sistemimiz, dünyadaki varlıkları VaR ve Stokastik Modelleme süzgecinden geçirerek sermayenizi matematiksel bir zırhla korur.",
        "btn_demo": "🚀 Demo Portföyü Analiz Et",
        "btn_custom": "🔑 Kendi Portföyünü Oluştur",
        "search_label": "🔍 Varlık Adı veya Sembol Yazın:",
        "search_placeholder": "Örn: Apple, SASA, Bitcoin...",
        "results_label": "Sonuçlar bulundu, lütfen seçin:",
        "risk_score": "Risk Skoru",
        "volatility": "Yıllık Oynaklık",
        "confidence": "Piyasa Güveni"
    },
    "EN": {
        "title": "Guardian Intelligence",
        "subtitle": "Global Risk Management & Econometric Projection",
        "manifesto_title": "🛡️ Strategic Manifesto",
        "manifesto_text": "Guardian is not just a data panel; it is a decision mechanism built on the foundations of Econometrics. Our system protects your capital with a mathematical shield by filtering global assets through VaR and Stochastic Modeling.",
        "btn_demo": "🚀 Analyze Demo Portfolio",
        "btn_custom": "🔑 Create Custom Portfolio",
        "search_label": "🔍 Enter Asset Name or Symbol:",
        "search_placeholder": "e.g., Apple, SASA, Bitcoin...",
        "results_label": "Results found, please select:",
        "risk_score": "Risk Score",
        "volatility": "Annual Volatility",
        "confidence": "Market Confidence"
    }
}

# --- 2. PREMIUM UI CONFIG ---
st.set_page_config(page_title="Guardian | Terminal", layout="wide")

# Dil Seçimi (Sağ Üst Köşeye Yakın - Sidebar)
if 'lang' not in st.session_state: st.session_state.lang = "TR"
lang_choice = st.sidebar.selectbox("🌐 Language / Dil", ["TR", "EN"])
st.session_state.lang = lang_choice
L = languages[st.session_state.lang]

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .trust-panel {{ background: linear-gradient(145deg, #0f172a, #1e293b); border: 1px solid #3b82f6; padding: 3rem; border-radius: 24px; margin-bottom: 2.5rem; }}
    .main-title {{ font-size: 3.8rem; font-weight: 800; color: #ffffff; letter-spacing: -2px; }}
    .subtitle {{ font-size: 1.3rem; color: #ffffff; font-weight: 600; margin-bottom: 2rem; }}
    .manifesto-text {{ color: #ffffff !important; font-size: 1.15rem; line-height: 1.8; }}
    .stButton>button {{ background: #2563eb; color: white; border-radius: 12px; height: 3.5rem; font-weight: 600; width: 100%; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. AKILLI VE ÖNCELİKLİ ARAMA (BIST PRIORITY) ---
def fetch_suggestions_smart(query):
    if len(query) < 2: return []
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        quotes = response.get('quotes', [])
        
        # BIST hisselerini ( .IS ) en üste taşıyan mantık
        bist_results = [q for q in quotes if str(q.get('symbol')).endswith('.IS')]
        other_results = [q for q in quotes if not str(q.get('symbol')).endswith('.IS')]
        
        sorted_quotes = bist_results + other_results
        
        suggestions = []
        for quote in sorted_quotes[:8]:
            if quote.get('quoteType') in ['EQUITY', 'CRYPTO', 'ETF', 'INDEX']:
                label = f"{quote.get('shortname', '')} ({quote.get('symbol')}) - {quote.get('exchDisp', '')}"
                suggestions.append({"label": label, "symbol": quote.get('symbol'), "name": quote.get('shortname')})
        return suggestions
    except:
        return []

# --- 4. SESSION STATE & AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 5. LANDING PAGE ---
if not st.session_state.auth:
    st.markdown(f"<h1 class='main-title'>{L['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle'>{L['subtitle']}</p>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class='trust-panel'>
            <h3 style='color: #3b82f6; margin-top: 0;'>{L['manifesto_title']}</h3>
            <p class='manifesto-text'>{L['manifesto_text']}</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button(L['btn_demo']):
            st.session_state.auth, st.session_state.mode = True, "demo"
            st.rerun()
    with c2:
        if st.button(L['btn_custom']):
            st.session_state.auth, st.session_state.mode = True, "custom"
            st.rerun()
    st.stop()

# --- 6. ANA TERMİNAL ---
st.sidebar.title(f"💎 Guardian {st.session_state.lang}")

if st.session_state.mode == "demo":
    final_tickers = ["THYAO.IS", "BTC-USD", "GC=F"]
    final_names = ["Türk Hava Yolları", "Bitcoin", "Altın ONS"]
else:
    search_input = st.sidebar.text_input(L['search_label'], placeholder=L['search_placeholder'])
    if search_input:
        with st.sidebar:
            suggestions = fetch_suggestions_smart(search_input)
            if suggestions:
                choice = st.selectbox(L['results_label'], options=[s['label'] for s in suggestions])
                selected_data = [s for s in suggestions if s['label'] == choice][0]
                final_tickers, final_names = [selected_data['symbol']], [selected_data['name']]
            else:
                st.warning("Eşleşme yok / No match.")
                final_tickers = []
    else: final_tickers = []

# --- 7. ANALİZ EKRANI ---
if final_tickers:
    try:
        data = yf.download(final_tickers, period="1y", progress=False)['Close']
        if not data.empty:
            if isinstance(data, pd.Series): data = data.to_frame()
            st.header(f"📊 {final_names[0]} {L['risk_score']}")
            st.plotly_chart(px.line(data, template="plotly_dark", color_discrete_sequence=['#2563eb']), use_container_width=True)
            
            rets = data.pct_change().dropna()
            vol = (rets.std() * np.sqrt(252) * 100).iloc[0]
            col1, col2 = st.columns(2)
            col1.metric(L['volatility'], f"%{vol:.2f}")
            col2.metric(L['confidence'], "High" if vol < 25 else "Medium" if vol < 45 else "Low")
    except Exception as e:
        st.error(f"Error: {e}")

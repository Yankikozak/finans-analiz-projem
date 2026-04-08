import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- 1. PREMIUM UI & GENİŞLETİLMİŞ TASARIM ---
st.set_page_config(page_title="Guardian | Finansal Koruma", layout="wide")

# Dil Sözlüğü
languages = {
    "TR": {
        "title": "Guardian Finansal Zeka",
        "subtitle": "Ekonometrik Modellerle Sermaye Koruma Sistemi",
        "manifesto_title": "🛡️ Stratejik Manifesto ve Güven Protokolü",
        "manifesto_text": """
            Piyasalarda kazanmak bir seçenek, sermayeyi korumak ise bir zorunluluktur. 
            **Guardian Finansal Zeka**, Sakarya Üniversitesi Ekonometri disiplini üzerine inşa edilmiş, 
            duygulardan arındırılmış bir karar destek mekanizmasıdır.
            
            **Burada Neler Yapabilirsiniz?**
            * **Küresel Varlık Analizi:** Dünyanın her yerindeki hisse, kripto ve emtialara anında ulaşın.
            * **Rasyonel Risk Yönetimi:** Value at Risk (VaR) modelleriyle 'en kötü senaryoyu' matematiksel olarak görün.
            * **Stratejik Karar Desteği:** Karmaşık piyasa gürültüsünü değil, ekonometrik verinin net sinyallerini takip edin.
            
            Verilerimiz doğrudan küresel borsalardan akmakta olup, analizlerimiz akademik standartlarda stokastik süreçlerle hesaplanmaktadır. 
            Sermayeniz, matematiksel bir zırhla korunmayı hak ediyor.
        """,
        "btn_demo": "🚀 Demo Portföyü Başlat",
        "btn_custom": "🔑 Terminale Giriş Yap",
        "search_label": "🔍 Analiz Edilecek Varlık:",
        "results_label": "Eşleşen Varlıklar:"
    },
    "EN": {
        "title": "Guardian Financial Intelligence",
        "subtitle": "Capital Protection System with Econometric Models",
        "manifesto_title": "🛡️ Strategic Manifesto & Trust Protocol",
        "manifesto_text": """
            Winning is an option; protecting capital is a necessity. 
            **Guardian Financial Intelligence** is a decision support mechanism built on 
            Econometric discipline, entirely free from emotional bias.
            
            **What Can You Do Here?**
            * **Global Asset Analysis:** Instantly access stocks, crypto, and commodities worldwide.
            * **Rational Risk Management:** See the 'worst-case scenario' mathematically using VaR models.
            * **Strategic Decision Support:** Follow clear econometric signals, not complex market noise.
            
            Our data flows directly from global exchanges, and our analyses are calculated using 
            stochastic processes at academic standards. Your capital deserves a mathematical shield.
        """,
        "btn_demo": "🚀 Start Demo Portfolio",
        "btn_custom": "🔑 Enter Terminal",
        "search_label": "🔍 Asset to Analyze:",
        "results_label": "Matching Assets:"
    }
}

# --- 2. SAĞ ÜST DİL SEÇENEĞİ VE STİL ---
if 'lang' not in st.session_state: st.session_state.lang = "TR"

# CSS ile Dil Seçiciyi Sağ Üste Sabitleme ve Blogu Genişletme
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    
    /* Sağ Üst Dil Butonu Alanı */
    .stSelectbox {{ width: 80px !important; float: right; }}
    
    .main-title {{ font-size: 3.5rem; font-weight: 800; color: #ffffff; letter-spacing: -2px; text-align: center; }}
    .subtitle {{ font-size: 1.2rem; color: #ffffff; text-align: center; margin-bottom: 3rem; opacity: 0.8; }}
    
    /* Blog Panelini Ekranı Kaplayacak Şekilde Genişletme */
    .trust-panel {{ 
        background: linear-gradient(145deg, #111827, #1f2937); 
        border: 1px solid #3b82f6; 
        padding: 4rem; 
        border-radius: 32px; 
        margin: 0 auto 3rem auto;
        max-width: 1000px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }}
    .manifesto-text {{ color: #ffffff !important; font-size: 1.25rem; line-height: 1.9; }}
    
    /* Gereksiz Sidebar Boşluğunu Kaldırma (Giriş Sayfası İçin) */
    [data-testid="stSidebar"] {{ display: {'none' if not st.get_option("client.showSidebarNavigation") else 'block'}}}
    </style>
    """, unsafe_allow_html=True)

# Dil seçimi için sağ üstte küçük bir alan (Sidebar yerine ana ekranın üstü)
col_title, col_lang = st.columns([10, 1])
with col_lang:
    lang_choice = st.selectbox("", ["TR", "EN"], index=0 if st.session_state.lang == "TR" else 1, label_visibility="collapsed")
    st.session_state.lang = lang_choice

L = languages[st.session_state.lang]

# --- 3. AKILLI ARAMA MOTORU (BIST ÖNCELİKLİ) ---
def fetch_suggestions_smart(query):
    if len(query) < 2: return []
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        quotes = response.get('quotes', [])
        bist = [q for q in quotes if str(q.get('symbol')).endswith('.IS')]
        others = [q for q in quotes if not str(q.get('symbol')).endswith('.IS')]
        sorted_q = bist + others
        return [{"label": f"{q.get('shortname', '')} ({q.get('symbol')})", "symbol": q.get('symbol'), "name": q.get('shortname')} for q in sorted_q[:8]]
    except: return []

# --- 4. GİRİŞ SAYFASI (GENİŞLETİLMİŞ BLOG) ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown(f"<h1 class='main-title'>{L['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle'>{L['subtitle']}</p>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class='trust-panel'>
            <h2 style='color: #3b82f6; margin-top: 0; border-bottom: 1px solid #374151; padding-bottom: 1rem;'>{L['manifesto_title']}</h2>
            <div class='manifesto-text'>{L['manifesto_text'].replace('*', '<br>•')}</div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        col_b1, col_b2 = st.columns(2)
        if col_b1.button(L['btn_demo']):
            st.session_state.auth, st.session_state.mode = True, "demo"
            st.rerun()
        if col_b2.button(L['btn_custom']):
            st.session_state.auth, st.session_state.mode = True, "custom"
            st.rerun()
    st.stop()

# --- 5. ANA TERMİNAL ---
# Giriş yapıldıktan sonra sidebar'ı gösteriyoruz
st.sidebar.title(f"💎 Guardian {st.session_state.lang}")
search_input = st.sidebar.text_input(L['search_label'], placeholder="Hisse, Kripto...")

if st.session_state.mode == "demo":
    final_tickers, final_names = ["THYAO.IS", "BTC-USD", "GC=F"], ["THY", "Bitcoin", "Altın"]
else:
    if search_input:
        suggestions = fetch_suggestions_smart(search_input)
        if suggestions:
            choice = st.sidebar.selectbox(L['results_label'], options=[s['label'] for s in suggestions])
            sel = [s for s in suggestions if s['label'] == choice][0]
            final_tickers, final_names = [sel['symbol']], [sel['name']]
        else: final_tickers = []
    else: final_tickers = []

# --- 6. ANALİZ ANALİZ ---
if final_tickers:
    try:
        data = yf.download(final_tickers, period="1y", progress=False)['Close']
        if not data.empty:
            if isinstance(data, pd.Series): data = data.to_frame()
            st.header(f"📊 {final_names[0]} Analiz Raporu")
            st.plotly_chart(px.line(data, template="plotly_dark", color_discrete_sequence=['#3b82f6']), use_container_width=True)
            
            rets = data.pct_change().dropna()
            vol = (rets.std() * np.sqrt(252) * 100).iloc[0]
            c1, c2 = st.columns(2)
            c1.metric("Volatilite", f"%{vol:.2f}")
            c2.metric("Güven Seviyesi", "Yüksek" if vol < 25 else "Orta")
    except: st.error("Veri alınamadı.")

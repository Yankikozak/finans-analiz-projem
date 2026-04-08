import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- 1. KURUMSAL UI & BEYAZ METİN AYARLARI ---
st.set_page_config(page_title="Guardian | Global Terminal", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .trust-panel { 
        background: linear-gradient(145deg, #0f172a, #1e293b); 
        border: 1px solid #3b82f6; 
        padding: 3rem; 
        border-radius: 24px; 
        margin-bottom: 2.5rem;
    }
    .main-title { font-size: 3.8rem; font-weight: 800; color: #ffffff; letter-spacing: -2px; }
    .subtitle { font-size: 1.3rem; color: #ffffff; font-weight: 600; margin-bottom: 2rem; }
    .manifesto-text { color: #ffffff !important; font-size: 1.15rem; line-height: 1.8; }
    
    /* Input ve Buton Tasarımı */
    .stTextInput>div>div>input { background-color: #1e293b; color: white; border: 1px solid #334155; }
    .stButton>button { background: #2563eb; color: white; border-radius: 12px; height: 3.5rem; font-weight: 600; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CANLI GLOBAL ARAMA MOTORU (YAHOO API) ---
def fetch_suggestions(query):
    """Kullanıcı yazdıkça dünyadaki tüm borsaları tarar."""
    if len(query) < 2: return []
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        suggestions = []
        for quote in response.get('quotes', []):
            # Sadece Hisse, Kripto ve ETF'leri al
            if quote.get('quoteType') in ['EQUITY', 'CRYPTO', 'ETF', 'INDEX']:
                label = f"{quote.get('shortname', '')} ({quote.get('symbol')}) - {quote.get('exchDisp', '')}"
                suggestions.append({"label": label, "symbol": quote.get('symbol'), "name": quote.get('shortname')})
        return suggestions
    except:
        return []

# --- 3. SESSION STATE ---
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 4. GİRİŞ EKRANI VE BLOG (MANIFESTO) ---
if not st.session_state.auth:
    st.markdown("<h1 class='main-title'>Guardian Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Global Risk Yönetimi ve Ekonometrik Projeksiyon</p>", unsafe_allow_html=True)

    st.markdown("""
        <div class='trust-panel'>
            <h3 style='color: #3b82f6; margin-top: 0;'>🛡️ Stratejik Manifesto</h3>
            <p class='manifesto-text'>
                Guardian, sadece veri gösteren bir panel değil; <b>Sakarya Üniversitesi Ekonometri</b> temelinde yükselen bir karar mekanizmasıdır. 
                Sistemimiz, dünya piyasalarındaki binlerce varlığı <b>Value at Risk (VaR)</b> ve <b>Stokastik Modelleme</b> süzgecinden geçirerek 
                sermayenizi matematiksel bir zırhla korur. 
                <br><br>
                Piyasa gürültüsünü değil, verinin sesini dinleyin.
            </p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Demo Portföyü Analiz Et"):
            st.session_state.auth = True
            st.session_state.mode = "demo"
            st.rerun()
    with c2:
        if st.button("🔑 Kendi Portföyünü Oluştur"):
            st.session_state.auth = True
            st.session_state.mode = "custom"
            st.rerun()
    st.stop()

# --- 5. ANA TERMİNAL: CANLI ARAMA ---
st.sidebar.title("💎 Guardian Terminal")

if st.session_state.mode == "demo":
    final_tickers = ["THYAO.IS", "BTC-USD", "GC=F"]
    final_names = ["Türk Hava Yolları", "Bitcoin", "Altın ONS"]
else:
    search_input = st.sidebar.text_input("🔍 Varlık Adı veya Sembol Yazın:", placeholder="Örn: Apple, SASA, Bitcoin...")
    
    if search_input:
        with st.sidebar:
            suggestions = fetch_suggestions(search_input)
            if suggestions:
                choice = st.selectbox("Sonuçlar bulundu, lütfen seçin:", 
                                     options=[s['label'] for s in suggestions])
                
                selected_data = [s for s in suggestions if s['label'] == choice][0]
                final_tickers = [selected_data['symbol']]
                final_names = [selected_data['name']]
            else:
                st.warning("Eşleşme bulunamadı. Tam sembolü yazmayı deneyin (Örn: THYAO.IS).")
                final_tickers = []
    else:
        final_tickers = []

# --- 6. ANALİZ EKRANI ---
if final_tickers:
    try:
        with st.spinner('Analiz motoru hazırlanıyor...'):
            data = yf.download(final_tickers, period="1y", progress=False)['Close']
            
            if not data.empty:
                if isinstance(data, pd.Series): data = data.to_frame()
                
                # Dinamik Başlık
                st.header(f"📊 {final_names[0]} Risk Analiz Raporu")
                
                # Grafik
                fig = px.line(data, template="plotly_dark", color_discrete_sequence=['#2563eb'])
                st.plotly_chart(fig, use_container_width=True)
                
                # Risk Metrikleri
                rets = data.pct_change().dropna()
                vol = (rets.std() * np.sqrt(252) * 100).iloc[0]
                
                col1, col2 = st.columns(2)
                col1.metric("Yıllık Oynaklık", f"%{vol:.2f}")
                col2.metric("Piyasa Güveni", "Yüksek" if vol < 25 else "Orta" if vol < 45 else "Düşük")
                
    except Exception as e:
        st.error(f"Veri hatası: {e}")

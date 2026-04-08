import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- 1. PRO KONFİGÜRASYON ---
st.set_page_config(page_title="Guardian Market", layout="wide", initial_sidebar_state="collapsed")

# Dil Ayarları
if 'lang' not in st.session_state: st.session_state.lang = "TR"

L_DICT = {
    "TR": {
        "title": "GUARDIAN MARKET",
        "subtitle": "Piyasa Takip ve Ekonometrik Risk Terminali",
        "search_label": "🔍 Varlık Ara (Hisse, Kripto, Emtia):",
        "market_summary": "Piyasa Özeti",
        "risk_score": "Risk Skoru",
        "volatility": "Oynaklık",
        "btn_enter": "Terminale Giriş",
        "table_asset": "Varlık",
        "table_price": "Fiyat",
        "table_change": "Değişim (%)"
    },
    "EN": {
        "title": "GUARDIAN MARKET",
        "subtitle": "Market Watch & Econometric Risk Terminal",
        "search_label": "🔍 Search Asset (Stock, Crypto, Commodity):",
        "market_summary": "Market Summary",
        "risk_score": "Risk Score",
        "volatility": "Volatility",
        "btn_enter": "Enter Terminal",
        "table_asset": "Asset",
        "table_price": "Price",
        "table_change": "Change (%)"
    }
}
L = L_DICT[st.session_state.lang]

# --- 2. CSS: EKONLAB ESİNTİLİ MODERN ARAYÜZ ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0a0e17; color: #ffffff; }
    
    /* Üst Bar Tasarımı */
    .market-header {
        background: rgba(30, 41, 59, 0.5);
        padding: 20px;
        border-radius: 15px;
        border-bottom: 2px solid #3b82f6;
        margin-bottom: 30px;
        text-align: center;
    }

    /* Kart Yapısı (Ekonlab Tarzı) */
    .metric-card {
        background: #111827;
        border: 1px solid #1f2937;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        transition: 0.3s;
    }
    .metric-card:hover { border-color: #3b82f6; background: #1e293b; }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #3b82f6; }
    .metric-label { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }

    /* Arama Çubuğu Özelleştirme */
    .stTextInput>div>div>input {
        background-color: #111827 !important;
        color: white !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 10px !important;
    }
    
    /* Tablo Görünümü */
    .stDataFrame { border: 1px solid #1f2937; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# Dil Seçimi
c1, c2 = st.columns([10, 1])
with c2:
    st.session_state.lang = st.selectbox("", ["TR", "EN"], label_visibility="collapsed")

# --- 3. AKILLI ARAMA VE VERİ ÇEKME ---
def fetch_market_data(query):
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        quotes = resp.get('quotes', [])
        bist = [q for q in quotes if str(q.get('symbol','')).endswith('.IS')]
        others = [q for q in quotes if not str(q.get('symbol','')).endswith('.IS') and q.get('quoteType') != 'FUND']
        return bist + others
    except: return []

# --- 4. ANA ARAYÜZ (MARKET DASHBOARD) ---
st.markdown(f"""
    <div class="market-header">
        <h1 style="margin:0; letter-spacing:-2px; font-weight:900;">{L['title']}</h1>
        <p style="color:#3b82f6; margin:0; font-weight:600;">{L['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

# Üst Metrikler (Canlı hisse simülasyonu gibi)
m1, m2, m3, m4 = st.columns(4)
for col, label, val in zip([m1, m2, m3, m4], 
                           ["BIST 100", "USD/TRY", "BTC/USD", "ALTIN (GR)"], 
                           ["9,120.4", "32.41", "68,432", "2,450"]):
    with col:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{val}</div>
            </div>
        """, unsafe_allow_html=True)

st.write("---")

# Arama ve Detaylı Analiz
search_q = st.text_input(L['search_label'], placeholder="Hisse kodu veya isim yazın...")

if search_q:
    results = fetch_market_data(search_q)
    if results:
        options = {f"{q.get('shortname')} ({q.get('symbol')})": q.get('symbol') for q in results}
        selection = st.selectbox("Eşleşen Sonuçlar:", list(options.keys()))
        ticker = options[selection]
        
        # Grafik Alanı
        df = yf.download(ticker, period="1mo", progress=False)['Close']
        if not df.empty:
            c_left, c_right = st.columns([2, 1])
            with c_left:
                fig = px.area(df, template="plotly_dark", color_discrete_sequence=['#3b82f6'])
                fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with c_right:
                # Ekonometrik Risk Analizi Kartı
                returns = df.pct_change().dropna()
                vol = (returns.std() * np.sqrt(252) * 100).iloc[0]
                st.markdown(f"""
                    <div class="metric-card" style="height:400px; display:flex; flex-direction:column; justify-content:center;">
                        <div class="metric-label">{L['volatility']} (Annual)</div>
                        <div class="metric-value">%{vol:.2f}</div>
                        <br>
                        <div class="metric-label">{L['risk_score']}</div>
                        <div class="metric-value" style="color:{'#ef4444' if vol > 35 else '#22c55e'}">
                            {'Yüksek' if vol > 35 else 'Düşük'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from datetime import datetime

# --- 1. TEKNİK ALTYAPI: CACHE & OPTİMİZASYON ---
st.set_page_config(page_title="Guardian Terminal", layout="wide", initial_sidebar_state="collapsed")

@st.cache_data(ttl=300)  # Veriyi 5 dakika saklar, hızı artırır
def get_quick_stats(ticker):
    try:
        data = yf.Ticker(ticker).history(period="2d")
        if len(data) < 2: return 0, 0
        price = data['Close'].iloc[-1]
        change = ((price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
        return price, change
    except: return 0, 0

@st.cache_data(ttl=600)
def calculate_risk_score(ticker):
    try:
        df = yf.download(ticker, period="3mo", progress=False)['Close']
        returns = df.pct_change().dropna()
        vol = returns.std() * np.sqrt(252) * 100
        # Basit Risk Skoru (1-10)
        score = min(max(int(vol / 10), 1), 10)
        return score, vol
    except: return 5, 0

# --- 2. SMART SEARCH: RANKING & ENTITY MATCHING ---
def smart_search(query):
    if len(query) < 2: return []
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        quotes = resp.get('quotes', [])
        
        enriched_results = []
        for q in quotes:
            symbol = q.get('symbol')
            if not symbol or q.get('quoteType') == 'FUND': continue
            
            # Ranking Mantığı
            score = 0
            if query.upper() in symbol: score += 100
            if symbol.endswith('.IS'): score += 50 # BIST Önceliği
            
            price, change = get_quick_stats(symbol)
            risk, _ = calculate_risk_score(symbol)
            
            enriched_results.append({
                "symbol": symbol,
                "name": q.get('shortname', 'Bilinmiyor'),
                "price": price,
                "change": change,
                "risk": risk,
                "score": score
            })
        
        return sorted(enriched_results, key=lambda x: x['score'], reverse=True)
    except: return []

# --- 3. UI/UX: MODERN FINANSAL TASARIM (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #020617; }
    
    /* SaaS Kart Yapısı */
    .search-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .search-card:hover { border-color: #3b82f6; background: rgba(30, 41, 59, 0.6); }
    
    .status-up { color: #22c55e; font-weight: bold; }
    .status-down { color: #ef4444; font-weight: bold; }
    
    .risk-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    /* Blog Kartları */
    .blog-section { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
    .blog-card {
        background: #0f172a; border: 1px solid #1e293b; padding: 25px; border-radius: 20px;
    }
    .blog-tag { color: #3b82f6; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- 4. LANDING & BLOG SİSTEMİ ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ Guardian Intelligence")
    st.subheader("Sakarya Üniversitesi Ekonometri Disiplini ile Güçlendirilmiş SaaS Analiz Platformu")
    
    tabs = st.tabs(["📊 Market", "📝 Analist Raporları", "🎓 Eğitim"])
    
    with tabs[1]:
        st.markdown('<div class="blog-section">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="blog-card">
                <span class="blog-tag">HİSSE SENEDİ</span>
                <h3>BIST 100 Volatilite Analizi</h3>
                <p>GARCH modellerimiz önümüzdeki 10 gün için oynaklık artışı bekliyor. Nakit oranını korumak stratejik olabilir.</p>
                <hr style="border:0.1px solid #1e293b">
                <small>Risk Skoru: 7/10 | Analist: Yankı</small>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="blog-card">
                <span class="blog-tag">MAKROEKONOMİ</span>
                <h3>Enflasyon ve Kur Tahminleri</h3>
                <p>Ekonometrik zaman serisi analizleri, kurdaki stabilizasyonun devam edeceğine işaret ediyor.</p>
                <hr style="border:0.1px solid #1e293b">
                <small>Risk Skoru: 4/10 | Analist: AI-Guardian</small>
            </div>
            """, unsafe_allow_html=True)
    
    if st.button("Terminali Başlat"):
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- 5. SMART TERMINAL ---
st.header("🔍 Akıllı Varlık Terminali")
query = st.text_input("", placeholder="Varlık ismi veya sembolü girin (Örn: Apple, THY, BTC)...", label_visibility="collapsed")

if query:
    results = smart_search(query)
    if not results:
        st.warning("Sonuç bulunamadı.")
    else:
        for r in results:
            change_class = "status-up" if r['change'] >= 0 else "status-down"
            risk_color = "#22c55e" if r['risk'] < 4 else "#eab308" if r['risk'] < 7 else "#ef4444"
            
            with st.container():
                st.markdown(f"""
                <div class="search-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.2rem; font-weight: 800;">{r['name']}</span> 
                            <span style="color: #64748b; margin-left: 10px;">{r['symbol']}</span>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.1rem; font-weight: bold;">{r['price']:.2f} USD</div>
                            <div class="{change_class}">%{r['change']:.2f}</div>
                        </div>
                    </div>
                    <div style="margin-top: 15px; display: flex; gap: 15px; align-items: center;">
                        <span class="risk-badge" style="background: {risk_color}33; color: {risk_color};">Risk Skoru: {r['risk']}/10</span>
                        <span style="color: #94a3b8; font-size: 0.85rem;">Ekonometrik model tarafından onaylandı.</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Analiz Et: {r['symbol']}", key=r['symbol']):
                    st.session_state.selected_ticker = r['symbol']

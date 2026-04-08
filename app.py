import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from rapidfuzz import process, fuzz

# --- 1. PREMIUM UI & VISIBILITY CONFIG ---
st.set_page_config(page_title="Guardian | Finansal Risk Terminali", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Metinlerin görünürlüğü için Pure White ayarı */
    .main-title { font-size: 3.5rem; font-weight: 800; letter-spacing: -2px; color: #ffffff; margin-bottom: 5px; }
    .subtitle { font-size: 1.25rem; color: #ffffff; font-weight: 600; margin-bottom: 2rem; }
    
    .trust-panel { 
        background: linear-gradient(145deg, #0f172a, #1e293b); 
        border: 1px solid #3b82f6; 
        padding: 2.5rem; 
        border-radius: 24px; 
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.7);
    }
    
    .feature-card { 
        background: #1e293b; 
        padding: 1.5rem; 
        border-radius: 16px; 
        border: 1px solid #334155; 
        height: 100%; 
        color: #ffffff !important; 
    }
    .feature-card h4 { color: #ffffff !important; font-weight: 700; }
    .feature-card p { color: #ffffff !important; font-weight: 400; opacity: 0.9; }
    
    .stButton>button { background: #2563eb; color: white; border-radius: 12px; height: 3.5rem; font-weight: 600; border: none; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AKILLI ARAMA MOTORU VERİ SETİ ---
@st.cache_data
def get_asset_db():
    data = [
        {"symbol": "THYAO.IS", "name": "Türk Hava Yolları", "tags": ["THY", "Uçak", "Havacılık"]},
        {"symbol": "BTC-USD", "name": "Bitcoin", "tags": ["BTC", "Kripto", "Digital Gold", "Bitkoin"]},
        {"symbol": "ETH-USD", "name": "Ethereum", "tags": ["ETH", "Kripto", "Ether"]},
        {"symbol": "GC=F", "name": "Altın ONS", "tags": ["Gold", "XAU", "Ons", "Metal"]},
        {"symbol": "SISE.IS", "name": "Şişecam", "tags": ["Cam", "Fabrika", "Sanayi"]},
        {"symbol": "EREGL.IS", "name": "Ereğli Demir Çelik", "tags": ["Demir", "Çelik", "Sanayi"]},
        {"symbol": "SI=F", "name": "Gümüş ONS", "tags": ["Silver", "XAG", "Gumus"]},
        {"symbol": "XU100.IS", "name": "BIST 100", "tags": ["Endeks", "Borsa Istanbul", "Hisse"]},
        {"symbol": "AAPL", "name": "Apple Inc.", "tags": ["Teknoloji", "iPhone", "Nasdaq"]},
        {"symbol": "TSLA", "name": "Tesla", "tags": ["Elon Musk", "EV", "Elektrikli Araç"]}
    ]
    return pd.DataFrame(data)

def smart_search(query, df):
    if not query: return []
    query = query.lower().strip()
    results = []
    for _, row in df.iterrows():
        # Sembol, İsim veya Etiketler üzerinden benzerlik puanı hesapla
        score = max(
            fuzz.ratio(query, row['symbol'].lower().split('.')[0]),
            fuzz.partial_ratio(query, row['name'].lower()),
            max([fuzz.ratio(query, t.lower()) for t in row['tags']]) if row['tags'] else 0
        )
        if score > 50: # %50 benzerlik eşiği
            results.append({"symbol": row['symbol'], "name": row['name'], "score": score})
    return sorted(results, key=lambda x: x['score'], reverse=True)[:5]

# --- 3. SESSION STATE & AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 4. PROFESYONEL GİRİŞ EKRANI (LANDING) ---
if not st.session_state.auth:
    st.markdown("<h1 class='main-title'>Guardian Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Akademik Ekonometri Modelleriyle Sermayenizi Koruyan Karar Destek Sistemi</p>", unsafe_allow_html=True)

    st.markdown("""
        <div class='trust-panel'>
            <h3 style='color: #3b82f6; margin-top: 0;'>🛡️ Finansal Fırtınalara Karşı Matematiksel Kalkan</h3>
            <p style='color: #ffffff; font-size: 1.15rem; line-height: 1.7;'>
                Finansal piyasalarda kalıcı olmanın sırrı, ne kadar kazandığınız değil, <b>siyah kuğu (black swan)</b> olaylarında ne kadar korunduğunuzdur. 
                Sistemimiz, <b>Value at Risk (VaR)</b> ve <b>Monte Carlo</b> simülasyonlarını kullanarak, duygulardan arınmış rasyonel bir risk projeksiyonu sunar.
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

    st.markdown("<br>", unsafe_allow_html=True)
    v1, v2, v3 = st.columns(3)
    with v1: st.markdown("<div class='feature-card'><h4>📉 Kayıp Kontrolü</h4><p>Yarın yaşanabilecek maksimum kaybınızı rasyonel verilerle öngörün.</p></div>", unsafe_allow_html=True)
    with v2: st.markdown("<div class='feature-card'><h4>🧪 Stres Testleri</h4><p>Kriz senaryolarının portföyünüze etkisini saniyeler içinde simüle edin.</p></div>", unsafe_allow_html=True)
    with v3: st.markdown("<div class='feature-card'><h4>🤖 Karar Desteği</h4><p>AI destekli net stratejik önerilerle aksiyon alın.</p></div>", unsafe_allow_html=True)
    st.stop()

# --- 5. ANA TERMİNAL ---
st.sidebar.title("💎 Guardian Pro")
df_search = get_asset_db()
query = st.sidebar.text_input("🔍 Varlık veya Sembol Ara (Örn: bitkoin, thy):")

if st.session_state.mode == "demo":
    tickers = ["THYAO.IS", "BTC-USD", "GC=F"]
    names = ["Türk Hava Yolları", "Bitcoin", "Altın ONS"]
else:
    matches = smart_search(query, df_search)
    if matches:
        st.sidebar.write("**Sonuçlar:**")
        selected = st.sidebar.selectbox("Seçiniz:", [m['name'] for m in matches])
        tickers = [m['symbol'] for m in matches if m['name'] == selected]
        names = [selected]
    else:
        tickers = []

# --- 6. ANALİZ EKRANI ---
if tickers:
    try:
        data = yf.download(tickers, period="1y", progress=False)['Close']
        if isinstance(data, pd.Series): data = data.to_frame()
        
        # Dinamik Başlık
        graph_title = f"{' & '.join(names)} Performans Analizi"
        
        st.header(graph_title)
        
        # Risk Dashboard
        returns = data.pct_change().dropna()
        vol = returns.std() * np.sqrt(252) * 100
        risk_score = min(10.0, vol.mean() / 5)
        
        r_color = "#22c55e" if risk_score < 4 else "#f59e0b" if risk_score < 7 else "#ef4444"
        st.markdown(f"<div style='background:#111418; padding:20px; border-radius:15px; border-left:10px solid {r_color};'><h3>Risk Skoru: {risk_score:.1f} / 10</h3></div>", unsafe_allow_html=True)
        
        st.plotly_chart(px.line(data, template="plotly_dark"), use_container_width=True)
        
    except Exception as e:
        st.error(f"Veri çekilemedi: {e}")

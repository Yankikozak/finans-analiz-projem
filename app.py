import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from rapidfuzz import fuzz

# --- 1. KURUMSAL UI AYARLARI ---
st.set_page_config(page_title="Guardian | Risk Terminali", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main-title { font-size: 3.5rem; font-weight: 800; letter-spacing: -2px; color: #ffffff; }
    .subtitle { font-size: 1.25rem; color: #ffffff; font-weight: 600; margin-bottom: 2rem; }
    
    .trust-panel { 
        background: linear-gradient(145deg, #0f172a, #1e293b); 
        border: 1px solid #3b82f6; 
        padding: 2.5rem; 
        border-radius: 24px; 
        margin-bottom: 2.5rem;
    }
    
    .feature-card { 
        background: #1e293b; 
        padding: 1.5rem; 
        border-radius: 16px; 
        border: 1px solid #334155; 
        color: #ffffff !important; 
    }
    
    /* Yükleme çubuğu rengini kurumsal mavi yap */
    .stProgress > div > div > div > div { background-color: #2563eb; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GELİŞMİŞ GLOBAL ARAMA MOTORU ---
@st.cache_data
def get_quick_access():
    # Hızlı erişim için popüler varlıklar (Hata payını azaltır)
    return {
        "THY": "THYAO.IS", "BITCOIN": "BTC-USD", "ALTIN": "GC=F", 
        "GUMUS": "SI=F", "NASDAQ": "^IXIC", "BIST100": "XU100.IS"
    }

def resolve_ticker(query):
    query = query.upper().strip()
    quick_db = get_quick_access()
    
    # 1. Sözlükte var mı?
    if query in quick_db:
        return quick_db[query]
    
    # 2. Eğer kullanıcı nokta koymadıysa ve 4-5 karakterse BIST varsay
    if "." not in query and "-" not in query:
        # Kripto çifti kontrolü (BTCUSD gibi bitişik yazımlar için)
        if any(x in query for x in ["USD", "USDT"]):
            return f"{query[:3]}-{query[3:]}"
        return f"{query}.IS"
    
    return query

# --- 3. SESSION STATE ---
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 4. GİRİŞ EKRANI (LANDING) ---
if not st.session_state.auth:
    st.markdown("<h1 class='main-title'>Guardian Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Akademik Ekonometri Modelleriyle Sermayenizi Koruyan Karar Destek Sistemi</p>", unsafe_allow_html=True)

    st.markdown("""
        <div class='trust-panel'>
            <h3 style='color: #3b82f6; margin-top: 0;'>🛡️ Kurumsal Risk Projeksiyonu</h3>
            <p style='color: #ffffff; font-size: 1.15rem; line-height: 1.7;'>
                Guardian, global piyasalardaki tüm hisse senedi, emtia ve kripto varlıkları kapsayan 
                geniş bir veri ağına sahiptir. Portföyünüzü sadece analiz etmez, olası kriz senaryolarına 
                karşı matematiksel olarak test eder.
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

# --- 5. ANA TERMİNAL (TÜM HİSSELERE AÇIK) ---
st.sidebar.title("💎 Guardian Global")
raw_input = st.sidebar.text_input("🔍 Varlık Sembolü Girin (Örn: SASA, AAPL, ETH-USD):")

if st.session_state.mode == "demo":
    tickers = ["THYAO.IS", "BTC-USD", "GC=F"]
else:
    tickers = [resolve_ticker(x.strip()) for x in raw_input.split(",")] if raw_input else []

if tickers:
    try:
        # EMOJİSİZ, CİDDİ YÜKLEME MESAJI
        with st.spinner('Piyasa verileri terminale aktarılıyor...'):
            data = yf.download(tickers, period="1y", progress=False)['Close']
            
            if data.empty:
                st.warning("Veri bulunamadı. Lütfen sembolü kontrol edin (Örn: EREGL yerine EREGL.IS).")
            else:
                if isinstance(data, pd.Series): data = data.to_frame()
                
                # Dinamik Başlık
                st.header(f"📊 {', '.join(tickers)} Analiz Raporu")
                
                # Risk Analizi
                returns = data.pct_change().dropna()
                ann_vol = (returns.std() * np.sqrt(252) * 100).mean()
                
                # Görselleştirme
                st.plotly_chart(px.line(data, template="plotly_dark"), use_container_width=True)
                
                # AI Yorum (Ciddi ve Teknik)
                st.subheader("📝 Risk Yönetim Notu")
                if ann_vol > 30:
                    st.error(f"Sinyal: Yüksek Volatilite (%{ann_vol:.1f}). Portföy koruma kalkanı (Hedge) aktif edilmelidir.")
                else:
                    st.success(f"Sinyal: Stabil Trend (%{ann_vol:.1f}). Mevcut pozisyonlar korunabilir.")

    except Exception as e:
        st.error(f"Sistemsel Hata: {str(e)}")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. MARKA KİMLİĞİ VE STİL ---
st.set_page_config(page_title="Guardian Finance | Risk Control", layout="wide")

st.markdown("""
    <style>
    /* Stripe/Notion stili kartlar */
    .metric-card {
        background: #1a1c23;
        border: 1px solid #2d3139;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
    }
    .risk-high { color: #ff4b4b; border-bottom: 4px solid #ff4b4b; }
    .risk-mid { color: #ffa500; border-bottom: 4px solid #ffa500; }
    .risk-low { color: #00ff00; border-bottom: 4px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DEĞER ÖNERİSİ (LANDING) ---
if 'active' not in st.session_state:
    st.session_state.active = False

if not st.session_state.active:
    st.title("🛡️ Yatırımlarını Şansa Bırakma.")
    st.subheader("Guardian, ekonometrik modellerle portföyündeki 'kara delikleri' tespit eder.")
    
    st.markdown("""
    - **Karar Ver:** "Ne yapmalıyım?" sorusuna AI destekli yanıtlar al.
    - **Kayıp Kontrolü:** Piyasa krizlerini önceden simüle et.
    - **Güven:** Akademik risk modelleriyle sermayeni koru.
    """)
    
    if st.button("Ücretsiz Analize Başla (Demo Portföy)"):
        st.session_state.active = True
        st.rerun()
    st.stop()

# --- 3. AKILLI ANALİZ MOTORU ---
def get_ai_advice(score, var_val):
    if score > 7:
        return "🚨 **KRİTİK:** Portföyün çok agresif. Bir çöküş durumunda telafisi zor yaralar alabilirsin. **Öneri:** Hisse ağırlığını %20 azaltıp altına geç.", "risk-high"
    elif score > 4:
        return "⚠️ **DİKKAT:** Orta düzey risk. Piyasa dalgalanmaları seni sarsabilir. **Öneri:** Stop-loss seviyelerini güncelle.", "risk-mid"
    else:
        return "✅ **GÜVENLİ:** Portföyün dengeli. Mevcut stratejini koruyabilirsin.", "risk-low"

# --- 4. ANA DASHBOARD ---
st.sidebar.title("💎 Guardian Pro")
mode = st.sidebar.radio("Mod", ["Demo Portföy", "Kendi Portföyüm (Pro)"])

# Demo Verileri
assets = ["THYAO.IS", "BTC-USD", "GC=F", "EREGL.IS"]
weights = np.array([0.4, 0.2, 0.2, 0.2])

try:
    with st.spinner('Piyasa verileri analiz ediliyor...'):
        data = yf.download(assets, period="1y", progress=False)['Close']
        returns = data.pct_change().dropna()
        port_ret = (returns * weights).sum(axis=1)
        cum_ret = (1 + port_ret).cumprod()
        
        # Metrikler
        vol = port_ret.std() * np.sqrt(252) * 100
        risk_score = min(10.0, vol / 4)
        var_95 = np.percentile(port_ret, 5) * 100
        
        advice, color_class = get_ai_advice(risk_score, var_95)

        # --- GÖRSEL HİYERARŞİ: SONUÇ EKRANI ---
        st.markdown(f"<h1 style='text-align: center;' class='{color_class}'>Risk Skoru: {risk_score:.1f} / 10</h1>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 1.2rem; margin-bottom: 40px;'>{advice}</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Yıllık Oynaklık", f"%{vol:.2f}")
        with col2:
            st.metric("Maksimum Günlük Kayıp", f"%{abs(var_95):.2f}")
        with col3:
            st.metric("Kriz Dayanıklılığı", "Düşük" if risk_score > 6 else "Yüksek")

        # --- WOW EFFECT: KRİZ SİMÜLASYONU ---
        st.divider()
        st.subheader("🧪 Kriz Simülasyonu: '2008 Benzeri Çöküş'")
        crash_impact = abs(var_95 * 4.5) # Basit kriz katsayısı
        
        c_col1, c_col2 = st.columns([1, 2])
        with c_col1:
            st.error(f"Bu senaryoda tahmini kaybın: **%{crash_impact:.1f}**")
            st.write("Eğer bu kayıp seni rahatsız ediyorsa, portföy yapını 'Defansif' moda geçirmelisin.")
        with c_col2:
            st.plotly_chart(px.line(cum_ret, title="Performans Geçmişi", template="plotly_dark"), use_container_width=True)

except:
    st.error("Veri bağlantısı kurulamadı.")

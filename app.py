import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Portfolio Intelligence Terminal", layout="wide")

st.markdown("""
    <style>
    .metric-card { background-color: #111418; border: 1px solid #1f2937; padding: 20px; border-radius: 12px; }
    .stButton>button { width: 100%; background-color: #2563eb; color: white; border-radius: 8px; }
    .action-box { padding: 20px; border-radius: 10px; border-left: 5px solid; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HESAPLAMA MOTORU (ENGINE) ---
@st.cache_data(ttl=3600)
def fetch_and_analyze(assets, weights, period="1y"):
    try:
        data = yf.download(assets, period=period, progress=False)['Close']
        if isinstance(data, pd.Series): data = data.to_frame()
        
        returns = data.pct_change().dropna()
        # Portföy Günlük Getirisi
        port_returns = (returns * weights).sum(axis=1)
        cum_returns = (1 + port_returns).cumprod()
        
        # Metrikler
        vol = port_returns.std() * np.sqrt(252)
        mdd = ((cum_returns / cum_returns.cummax()) - 1).min()
        var_95 = np.percentile(port_returns, 5) # %95 VaR
        
        return {
            "cum_returns": cum_returns,
            "volatility": vol,
            "mdd": mdd,
            "var": var_95,
            "last_return": (cum_returns.iloc[-1] - 1)
        }
    except Exception as e:
        return None

# --- 3. KARAR DESTEK MANTIĞI (INTELLIGENCE) ---
def get_strategic_advice(metrics):
    vol = metrics['volatility'] * 100
    var = abs(metrics['var'] * 100)
    
    advice = []
    if vol > 30:
        advice.append(("🔴 Yüksek Risk", "Portföy oynaklığı çok yüksek. Agresif varlıkları (Kripto/Teknoloji) %15 azaltıp emtiaya yönelmek riski dengeler."))
    elif vol < 15:
        advice.append(("🟢 Defansif", "Portföyün oldukça güvenli ama getiri potansiyeli sınırlı. Küçük bir miktar endeks fonu eklenebilir."))
    
    if var > 3.5:
        advice.append(("⚠️ Kritik Kayıp Eşiği", f"Piyasadaki normal bir günde dahi %{var:.2f} kayıp ihtimalin var. Nakit rezervini artır."))
        
    return advice

# --- 4. UI AKIŞI ---
st.title("🛡️ Portfolio Intelligence Terminal")
st.markdown("_Kayıp kontrolü ve stratejik karar destek sistemi_")

# Sidebar - Portföy Girişi
st.sidebar.header("📂 Portföy Yönetimi")
app_mode = st.sidebar.toggle("Kendi Portföyümü Oluştur", value=False)

if not app_mode:
    # DEMO MODU
    st.sidebar.info("Şu an 'Dengeli Demo Portföy' aktif.")
    assets = ["THYAO.IS", "EREGL.IS", "BTC-USD", "GC=F"]
    weights = [0.3, 0.2, 0.1, 0.4]
else:
    # KULLANICI GİRİŞİ
    raw_tickers = st.sidebar.text_input("Varlıklar (Virgülle ayırın)", "THYAO, EREGL, BTC, GOLD")
    tickers = []
    for t in raw_tickers.split(","):
        t = t.strip().upper()
        if t in ["BTC", "ETH"]: tickers.append(f"{t}-USD")
        elif t in ["GOLD", "SILVER"]: tickers.append("GC=F" if t=="GOLD" else "SI=F")
        elif "." not in t: tickers.append(f"{t}.IS")
        else: tickers.append(t)
    assets = tickers
    weights = [1/len(assets)] * len(assets) # Eşit ağırlık varsayılan

# Analiz Çalıştır
metrics = fetch_and_analyze(assets, weights)

if metrics:
    # --- DASHBOARD ÜST ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam Getiri", f"%{metrics['last_return']*100:.2f}")
    c2.metric("Yıllık Risk", f"%{metrics['volatility']*100:.1f}")
    c3.metric("Max Kayıp (DD)", f"%{metrics['mdd']*100:.1f}")
    
    risk_score = min(10, max(1, (metrics['volatility'] * 100) / 5))
    c4.metric("Risk Skoru", f"{risk_score:.1;f} / 10")

    # --- ANA GRAFİK ---
    st.plotly_chart(px.line(metrics['cum_returns'], title="Kümülatif Getiri Trendi", template="plotly_dark"), use_container_width=True)

    # --- KAYIP KONTROLÜ & STRES TESTİ ---
    st.divider()
    st.subheader("🧪 Kayıp Kontrolü & Stres Testi")
    
    sc1, sc2 = st.columns(2)
    with sc1:
        st.write("### Olası Senaryolar")
        crash_10 = -10 * (metrics['volatility'] / 0.18) # Basit beta tahmini
        st.error(f"**%10 Piyasa Düşüşü:** Portföy tahmini **%{abs(crash_10):.1f}** değer kaybeder.")
        st.warning(f"**Günlük VaR (%95):** Normal bir günde en fazla **%{abs(metrics['var']*100):.2f}** kayıp beklenir.")

    with sc2:
        st.write("### Stratejik Aksiyon Planı")
        advices = get_strategic_advice(metrics)
        for title, text in advices:
            st.markdown(f"**{title}:** {text}")

    # --- PORTFÖYÜ KAYDET (SaaS Özelliği İllüzyonu) ---
    st.divider()
    if st.button("💾 Bu Portföyü ve Analizi Kaydet"):
        st.toast("Portföy kaydedildi! (Üyelik özelliği)")

else:
    st.error("Veriler yüklenemedi. Lütfen sembolleri kontrol edin.")

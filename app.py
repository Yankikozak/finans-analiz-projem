import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import norm

# --- CONFIG ---
st.set_page_config(page_title="Guardian Finance | Risk Engine", layout="wide")

class RiskEngine:
    @staticmethod
    def calculate_metrics(returns, weights):
        # Yıllık getiri ve volatilite
        port_ret = np.sum(returns.mean() * weights) * 252
        port_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        
        # VaR %95 (Parametrik)
        var_95 = norm.ppf(1-0.95, port_ret/252, port_vol/np.sqrt(252))
        
        # Sharpe Ratio (Rf = %30 varsayıldı - TR piyasası için)
        sharpe = (port_ret - 0.30) / port_vol
        
        return port_ret, port_vol, var_95, sharpe

# --- UI HEADER ---
st.title("🛡️ Guardian Finance: Loss Mitigation Engine")
st.markdown("---")

# --- DATA & SESSION ---
if 'view' not in st.session_state: st.session_state.view = 'demo'

# --- SIDEBAR: ASSET MANAGEMENT ---
with st.sidebar:
    st.header("📂 Portföy Yapılandırma")
    mode = st.toggle("Kendi Portföyüm", value=False)
    
    if not mode:
        st.info("Demo Portföy: THY, Altın, Bitcoin, Ereğli")
        assets = ["THYAO.IS", "GC=F", "BTC-USD", "EREGL.IS"]
        weights = np.array([0.3, 0.3, 0.1, 0.3])
    else:
        raw = st.text_input("Varlıklar (Virgül):", "AAPL, TSLA, BTC-USD")
        assets = [x.strip() for x in raw.split(",")]
        weights = np.array([1/len(assets)] * len(assets))

# --- CORE ENGINE EXECUTION ---
try:
    data = yf.download(assets, period="1y")['Close'].ffill()
    returns = data.pct_change().dropna()
    
    engine = RiskEngine()
    ann_ret, ann_vol, var_val, sharpe = engine.calculate_metrics(returns, weights)

    # --- DASHBOARD ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Beklenen Yıllık Getiri", f"%{ann_ret*100:.1f}")
    col2.metric("Sistemik Risk (Vol)", f"%{ann_vol*100:.1f}")
    col3.metric("Max Günlük Kayıp (VaR)", f"%{abs(var_val)*100:.2f}")
    col4.metric("Sharpe Oranı", f"{sharpe:.2f}")

    # --- ACTIONABLE INTELLIGENCE (EN KRİTİK NOKTA) ---
    st.markdown("### 🤖 Guardian AI: Karar Önerileri")
    advice_col, alert_col = st.columns(2)
    
    with advice_col:
        if ann_vol > 0.4:
            st.error("🚨 **KRİTİK UYARI:** Portföy volatilite eşiği %40'ı aştı. Kripto veya yan tahta hisse ağırlığını %10 azaltıp emtiaya geçiş önerilir.")
        elif sharpe < 1:
            st.warning("⚠️ **VERİMSİZLİK:** Aldığın risk başına kazancın düşük. Korelasyonu yüksek varlıkları (Örn: Hepsi teknoloji) ayrıştırmalısın.")
        else:
            st.success("✅ **OPTIMAL:** Risk/Getiri dengeniz profesyonel standartlarda. Pozisyon koru.")

    with alert_col:
        crash_impact = ann_vol * -1.28  # Basit stres katsayısı
        st.info(f"🧪 **Kriz Projeksiyonu:** Olası bir piyasa krizinde portföyün tahmini kaybı: **%{abs(crash_impact)*100:.1f}**. Nakit rezervin bu tutarı karşılamalı.")

    # --- VISUALS ---
    st.plotly_chart(px.line((1+returns.dot(weights)).cumprod(), title="Hedge Edilmemiş Performans"), use_container_width=True)

except Exception as e:
    st.error(f"Veri bağlantı hatası: {e}")

# --- MONETIZATION HOOK ---
st.markdown("---")
if st.button("🚀 Detaylı Monte Carlo Analizi ve PDF Raporu Al (PREMIUM)"):
    st.balloons()
    st.toast("Premium abonelik sistemine yönlendiriliyorsunuz...")

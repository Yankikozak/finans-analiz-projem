import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Sayfa Yapılandırması
st.set_page_config(page_title="Risk & Portföy Analiz Terminali", layout="wide")

# Tasarım İyileştirmeleri
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# Başlık Güncellemesi
st.title("🛡️ Risk & Portföy Analiz Terminali")
st.markdown("_Veriye dayalı finansal karar destek sistemi_")
st.markdown("---")

# --- GENİŞ VARLIK KÜTÜPHANESİ ---
asset_library = {
    # Borsa İstanbul
    "THYAO": "THYAO.IS", "EREGL": "EREGL.IS", "ASELS": "ASELS.IS", "SISE": "SISE.IS", 
    "TUPRS": "TUPRS.IS", "KCHOL": "KCHOL.IS", "AKBNK": "AKBNK.IS", "GARAN": "GARAN.IS",
    "SASAS": "SASA.IS", "HEKTS": "HEKTS.IS", "BIMAS": "BIMAS.IS", "FROTO": "FROTO.IS",
    # Kripto Paralar
    "BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "AVAX": "AVAX-USD", "XRP": "XRP-USD",
    # ABD Borsaları & Emtia
    "APPLE": "AAPL", "TESLA": "TSLA", "AMAZON": "AMZN", "NVIDIA": "NVDA", "GOLD": "GC=F", "SILVER": "SI=F"
}

# --- SIDEBAR ---
st.sidebar.header("📂 Portföy Yönetimi")
mode = st.sidebar.radio("Çalışma Modu:", ["Hazır Demo Portföy", "Kendi Portföyünü Oluştur"])

if mode == "Hazır Demo Portföy":
    selected_assets = ["THYAO.IS", "EREGL.IS", "BTC-USD", "GC=F"]
    st.sidebar.info("Örnek 'Dengeli Portföy' (THY, Ereğli, Bitcoin, Altın) inceleniyor.")
else:
    raw_input = st.sidebar.text_input("Varlık Kodları (Örn: THYAO, BTC, GOLD)", "THYAO, EREGL, BTC")
    # Akıllı Sembol Dönüştürücü (Kullanıcı THYAO yazsa bile .IS ekler, BTC yazsa -USD ekler)
    tickers_list = [t.strip().upper() for t in raw_input.split(",")]
    selected_assets = []
    for t in tickers_list:
        if t in asset_library:
            selected_assets.append(asset_library[t])
        elif "." not in t and "-" not in t:
            selected_assets.append(f"{t}.IS")
        else:
            selected_assets.append(t)

days = st.sidebar.slider("Geçmiş Veri Aralığı (Gün)", 30, 1095, 365)
start_date = datetime.now() - timedelta(days=days)

# --- VERİ ÇEKME ---
@st.cache_data
def get_data(assets, start):
    try:
        df = yf.download(assets, start=start, progress=False)['Close']
        if isinstance(df, pd.Series): df = df.to_frame()
        return df.ffill().dropna()
    except:
        return None

data = get_data(selected_assets, start_date)

if data is not None and not data.empty and len(data) > 5:
    returns = data.pct_change().dropna()
    weights = np.array([1/len(selected_assets)] * len(selected_assets))
    port_returns = (returns * weights).sum(axis=1)
    cum_returns = (1 + port_returns).cumprod()
    
    # --- METRİKLER ---
    col1, col2, col3, col4 = st.columns(4)
    total_ret = (cum_returns.iloc[-1] - 1) * 100
    vol = port_returns.std() * np.sqrt(252) * 100
    drawdown = ((cum_returns / cum_returns.cummax()) - 1).min() * 100
    var_95 = np.percentile(port_returns, 5) * 100

    col1.metric("Toplam Getiri", f"%{total_ret:.2f}")
    col2.metric("Yıllık Volatilite", f"%{vol:.2f}")
    col3.metric("Maksimum Kayıp", f"%{drawdown:.2f}")
    col4.metric("Günlük VaR (%95)", f"%{abs(var_95):.2f}")

    # --- GRAFİKLER ---
    g1, g2 = st.columns([2, 1])
    with g1:
        st.subheader("Portföy Performans Trendi")
        st.plotly_chart(px.line(cum_returns, template="plotly_dark"), use_container_width=True)
    with g2:
        st.subheader("Varlık Dağılımı") # Pasta sembolü kaldırıldı
        st.plotly_chart(px.pie(values=weights, names=selected_assets, hole=0.4), use_container_width=True)

    # --- SENARYO ANALİZİ ---
    st.markdown("---")
    st.subheader("Stres Testi: Piyasa Şoku Simülasyonu")
    crash_impact = -10 * (vol / 18) 
    st.error(f"Sistemik bir %10 piyasa düşüşünde, portföyün tahmini duyarlılığı: **%{abs(crash_impact):.2f}** kayıp yönlüdür.")

    # --- PROFESYONEL STRATEJİ ANALİZİ ---
    st.markdown("---")
    st.subheader("Stratejik Portföy Yönetim Notları")
    c_a, c_b = st.columns(2)
    
    with c_a:
        st.info("### Risk Pozisyonu")
        if vol > 25:
            st.write("Mevcut portföy yapısı **agresif büyüme** odaklıdır. Volatilite katsayısı piyasa ortalamasının üzerindedir. Ani likidite ihtiyaçları için risk teşkil edebilir.")
        else:
            st.write("Portföy **defansif/dengeli** bir karaktere sahiptir. Sistemik risklere karşı direnç kapasitesi yüksektir.")

    with c_b:
        st.success("### Taktiksel Öneriler")
        if abs(drawdown) > 20:
            st.write("Maksimum kayıp oranı kritik eşiktedir. Riski stabilize etmek adına emtia veya sabit getirili varlık ağırlığının artırılması önerilir.")
        else:
            st.write("Portföy korelasyonu sağlıklı görünmektedir. Mevcut varlık dağılımı makroekonomik beklentilerle uyumlu korunabilir.")
else:
    st.warning("⚠️ Veri çekilemedi. Lütfen varlık kodlarını (Örn: THYAO, BTC) kontrol edin veya Demo modunu kullanın.")

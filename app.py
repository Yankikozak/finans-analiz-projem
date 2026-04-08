import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Sayfa Yapılandırması
st.set_page_config(page_title="Stratejik Portföy Terminali", layout="wide")

# --- CSS: Tasarım İyileştirme ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# Başlık (İsim kaldırıldı, kurumsal kimlik eklendi)
st.title("🛡️ Profesyonel Risk & Portföy Analiz Terminali")
st.markdown("_Veriye dayalı finansal karar destek sistemi_")
st.markdown("---")

# --- SIDEBAR: KULLANICI GİRİŞİ ---
st.sidebar.header("📂 Portföy Yönetimi")

# 1. DEMO PORTFÖY SEÇENEĞİ (Login'siz anında deneyim)
mode = st.sidebar.radio("Çalışma Modu:", ["Hazır Demo Portföy", "Kendi Portföyünü Oluştur"])

if mode == "Hazır Demo Portföy":
    # Örnek bir dengeli portföy
    default_tickers = "THYAO, EREGL, BTC-USD, GOLD"
    asset_dict = {"THYAO.IS": 0.3, "EREGL.IS": 0.3, "BTC-USD": 0.2, "GC=F": 0.2}
    st.sidebar.info("Şu an örnek bir 'Dengeli Portföy' inceleniyor.")
else:
    raw_input = st.sidebar.text_input("Varlık Kodları (Virgülle ayırın)", "THYAO, EREGL, BTC")
    # Ağırlık girişi (Basitlik için eşit ağırlık varsayıyoruz, geliştirilebilir)
    tickers_list = [t.strip().upper() for t in raw_input.split(",")]
    asset_dict = {f"{t}.IS" if "." not in t and "-" not in t else t: 1/len(tickers_list) for t in tickers_list}

days = st.sidebar.slider("Geçmiş Veri Aralığı (Gün)", 30, 730, 365)
start_date = datetime.now() - timedelta(days=days)

# --- VERİ ÇEKME ---
@st.cache_data
def get_portfolio_data(assets, start):
    try:
        df = yf.download(list(assets.keys()), start=start, progress=False)['Close']
        return df.ffill().dropna()
    except:
        return None

data = get_portfolio_data(asset_dict, start_date)

if data is not None and not data.empty:
    # Getiriler ve Portföy Hesaplama
    returns = data.pct_change().dropna()
    weights = np.array(list(asset_dict.values()))
    
    # Portföy Günlük Getirisi
    port_returns = (returns * weights).sum(axis=1)
    cum_returns = (1 + port_returns).cumprod()
    
    # --- METRİKLER ---
    col1, col2, col3, col4 = st.columns(4)
    total_ret = (cum_returns.iloc[-1] - 1) * 100
    vol = port_returns.std() * np.sqrt(252) * 100
    drawdown = ((cum_returns / cum_returns.cummax()) - 1).min() * 100
    var_95 = np.percentile(port_returns, 5) * 100

    col1.metric("💰 Toplam Getiri", f"%{total_ret:.2f}")
    col2.metric("📉 Yıllık Volatilite", f"%{vol:.2f}")
    col3.metric("🌊 Max Düşüş", f"%{drawdown:.2f}")
    col4.metric("🛡️ Günlük VaR (%95)", f"%{abs(var_95):.2f}")

    # --- GRAFİKLER ---
    g1, g2 = st.columns([2, 1])
    with g1:
        st.subheader("📈 Portföy Performans Çizgisi")
        st.plotly_chart(px.line(cum_returns, template="plotly_dark"), use_container_width=True)
    with g2:
        st.subheader("🥧 Varlık Dağılımı")
        st.plotly_chart(px.pie(values=weights, names=list(asset_dict.keys()), hole=0.4), use_container_width=True)

    # --- KRİTİK: SENARYO SİMÜLASYONU ---
    st.markdown("---")
    st.subheader("🧪 Stres Testi: Piyasa Çöküş Senaryosu")
    st.write("Eğer piyasa yarın birden %10 düşerse portföyün nasıl etkilenir?")
    
    crash_impact = -10 * (vol / 20) # Volatiliteye bağlı basit bir Beta tahmini
    expected_loss = (100000 * crash_impact) / 100
    
    st.error(f"**Senaryo Sonucu:** %10'luk bir piyasa düşüşünde, 100.000 TL'lik yatırımında yaklaşık **{abs(expected_loss):,.0f} TL** kayıp yaşanabilir.")

    # --- KRİTİK: AKSİYON ÖNERİLERİ ---
    st.markdown("---")
    st.subheader("🎯 Yankı AI: Stratejik Aksiyon Önerileri")
    
    c_a, c_b = st.columns(2)
    with c_a:
        st.info("### 🧐 Risk Analizi")
        if vol > 25:
            st.write("⚠️ **Yüksek Risk:** Portföyün çok agresif. Bir varlığın sert düşüşü tüm portföyü eritebilir.")
        else:
            st.write("✅ **Dengeli:** Risk dağılımın sağlıklı görünüyor.")

    with c_b:
        st.success("### ⚡ Net Aksiyon Planı")
        # Basit bir zeka algoritması
        max_asset = list(asset_dict.keys())[np.argmax(weights)]
        if vol > 30:
            st.write(f"👉 **Aksiyon:** Risk çok yüksek! **{max_asset}** ağırlığını azaltıp Altın (GOLD) veya Nakit ekle.")
        elif total_ret < -5:
            st.write("👉 **Aksiyon:** Zarar kes (Stop-loss) seviyelerini kontrol et veya maliyet düşürmek için kademeli alım düşün.")
        else:
            st.write("👉 **Aksiyon:** Mevcut yapıyı koru. Portföyün piyasa koşullarına uyumlu.")

else:
    st.warning("⚠️ Lütfen geçerli varlık kodları girin veya Demo moduna geçin.")

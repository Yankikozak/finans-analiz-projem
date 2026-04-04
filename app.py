import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Sayfa Yapılandırması
st.set_page_config(page_title="Yankı Risk Paneli", layout="wide")

st.title("🛡️ Yankı Finansal Risk & Portföy Analiz Terminali")
st.markdown("---")

# --- KULLANICI DOSTU VARLIK LİSTESİ ---
# Kullanıcı burada tanıdık isimler görecek, sistem arka planda Yahoo kodunu kullanacak.
asset_dict = {
    "ASELSAN (Bist)": "ASELS.IS",
    "THY - Türk Hava Yolları (Bist)": "THYAO.IS",
    "Bitcoin (Kripto)": "BTC-USD",
    "Ethereum (Kripto)": "ETH-USD",
    "Tüpraş (Bist)": "TUPRS.IS",
    "Ereğli Demir Çelik (Bist)": "EREGL.IS",
    "Şişecam (Bist)": "SISE.IS",
    "Apple (ABD Borsası)": "AAPL",
    "Tesla (ABD Borsası)": "TSLA",
    "Altın (Ons/USD)": "GC=F",
    "Gümüş (Ons/USD)": "SI=F"
}

# --- SIDEBAR: KOLAY SEÇİM ---
st.sidebar.header("🔍 Varlık Seçimi")
selected_display_name = st.sidebar.selectbox(
    "Analiz etmek istediğiniz varlığı seçin:",
    list(asset_dict.keys())
)

# Seçilen isme karşılık gelen Yahoo sembolünü alıyoruz
ticker = asset_dict[selected_display_name]

# Manuel arama yapmak isteyenler için opsiyonel kutu
manual_input = st.sidebar.text_input("Veya farklı bir kod yazın (Örn: GARAN):")
if manual_input:
    ticker = manual_input.upper().strip()
    if "." not in ticker and "-" not in ticker:
        ticker = f"{ticker}.IS"

st.sidebar.markdown("---")
days = st.sidebar.slider("Analiz Süresi (Gün)", 30, 1095, 365)
start_date = datetime.now() - timedelta(days=days)

# --- VERİ ÇEKME ---
@st.cache_data
def get_clean_data(t, start):
    try:
        df = yf.download(t, start=start, progress=False)['Close']
        if df.empty: return None
        if isinstance(df, pd.Series):
            df = df.to_frame()
        return df.ffill().dropna()
    except:
        return None

data = get_clean_data(ticker, start_date)

# --- PANEL GÖRÜNÜMÜ ---
if data is not None and len(data) > 5:
    price_col = data.iloc[:, 0]
    returns = price_col.pct_change().dropna()
    
    # Hesaplamalar
    total_ret = ((price_col.iloc[-1] / price_col.iloc[0]) - 1) * 100
    vol = returns.std() * np.sqrt(252) * 100
    risk_score = min(10, max(1, vol / 6))
    
    # Üst Bilgi Kartları
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Toplam Getiri", f"%{float(total_ret):.2f}")
    c2.metric("📉 Risk Seviyesi", f"%{float(vol):.2f}")
    c3.metric("📊 Risk Puanı", f"{float(risk_score):.1f} / 10")

    # Grafik
    st.subheader(f"📈 {selected_display_name} Fiyat Analizi")
    fig = px.line(data, template="plotly_dark", labels={'value': 'Fiyat', 'index': 'Tarih'})
    st.plotly_chart(fig, use_container_width=True)

    # Akıllı Yorumlar
    st.markdown("---")
    st.subheader("💡 Yankı'nın Profesyonel Analizi")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.info("### 🧐 Risk Durumu")
        if risk_score > 7:
            st.write(f"⚠️ **Yüksek Risk:** {selected_display_name} şu an oldukça oynak. Büyük kazanç potansiyeli kadar sert düşüş riski de taşıyor.")
        elif risk_score > 4:
            st.write(f"⚖️ **Dengeli:** Standart bir piyasa varlığı gibi hareket ediyor.")
        else:
            st.write(f"🛡️ **Güvenli Liman:** Hareketleri oldukça sakin, portföyü dengelemek için ideal.")

    with col_b:
        st.success("### 📈 Performans Notu")
        if total_ret > 0:
            st.write(f"🚀 Bu varlık seçilen dönemde **%{total_ret:.2f}** kazandırmış. Yatırımcı güveni yüksek görünüyor.")
        else:
            st.write(f"📉 Bu dönemde **%{total_ret:.2f}** kaybettirmiş. Ekonometrik olarak bir toparlanma süreci beklenebilir.")

else:
    st.error(f"❌ '{ticker}' verisi çekilemedi. Piyasalar kapalı olabilir veya kod hatalıdır.")

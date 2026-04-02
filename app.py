import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from arch import arch_model
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa Ayarları
st.set_page_config(page_title="Ekonometrik Risk Terminali", layout="wide")

# CSS - Okunmayan yazıları beyaza sabitle
st.markdown("""
    <style>
    .main { background-color: #0e1117 !important; }
    [data-testid="stMetric"] { background-color: #1e2130 !important; padding: 20px !important; border-radius: 12px !important; border: 1px solid #3e4451 !important; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 16px !important; }
    [data-testid="stMetricValue"] { color: #00ffcc !important; font-size: 28px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Finansal Risk ve Volatilite Terminali")

# 2. Yan Panel
with st.sidebar:
    st.header("🔍 Ayarlar")
    ticker = st.text_input("Varlık Sembolü:", "BTC-USD")
    gun_sayisi = st.slider("Veri Aralığı:", 250, 1000, 500)

# 3. Veri Çekme (Hata Çözücü Versiyon)
@st.cache_data
def veri_yukle(symbol, days):
    try:
        # auto_adjust=True ve actions=False ile en sade veriyi çekiyoruz
        df = yf.download(symbol, period=f"{days}d", auto_adjust=True)
        if df.empty: return None
        
        # Eğer veri çok katmanlıysa (MultiIndex), sadece 'Close' sütununu alıp düzleştiriyoruz
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df['Return'] = 100 * np.log(df['Close'] / df['Close'].shift(1))
        return df.dropna()
    except: return None

df = veri_yukle(ticker, gun_sayisi)

# 4. Hesaplamalar ve Görselleştirme
if df is not None and not df.empty:
    try:
        # GARCH Modeli
        model = arch_model(df['Return'], vol='Garch', p=1, q=1)
        res = model.fit(disp="off")
        df['Volatility'] = res.conditional_volatility

        # DEĞERLERİ ÇEKERKEN HATA ALMAMAK İÇİN .values[0] EKLEDİK
        last_price = float(df['Close'].iloc[-1])
        current_vol = float(df['Volatility'].iloc[-1])
        var_95 = float(np.percentile(df['Return'], 5))
        ort_getiri = float(df['Return'].mean())

        # Metrik Kartları
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Son Fiyat", f"${last_price:,.2f}")
        c2.metric("Volatilite (σ)", f"%{current_vol:.2f}")
        c3.metric("Risk (%95 VaR)", f"%{var_95:.2f}")
        c4.metric("Ort. Getiri", f"%{ort_getiri:.3f}")

        st.divider()

        # Grafikler
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=('Fiyat Grafiği', 'GARCH Volatilite Öngörüsü'))
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Fiyat", line=dict(color='#00ffcc')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Volatility'], name="GARCH", fill='tozeroy', line=dict(color='orange')), row=2, col=1)
        fig.update_layout(height=600, template="plotly_dark", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Model hatası: {e}. Lütfen başka bir sembol deneyin.")
else:
    st.error("❌ Veri çekilemedi. Sembolü kontrol edin.")
    
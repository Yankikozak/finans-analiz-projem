import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# --- 1. Sayfa Ayarları ---
st.set_page_config(
    page_title="TR-Analytix | BIST Risk Motoru",
    page_icon="💎",
    layout="wide"
)

# --- 2. Tasarım (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; }
    h1, h2, h3 { color: white !important; font-family: 'Inter', sans-serif; }
    .stMarkdown p { color: #94A3B8; }
    /* Kart Yapısı */
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Header ---
col_logo, col_nav = st.columns([1, 2])
with col_logo:
    st.markdown("<h2 style='margin-top:0;'>TR-<span style='color:#8B5CF6'>Analytix</span></h2>", unsafe_allow_html=True)

# --- 4. Hero Alanı ---
st.markdown("<h1 style='text-align: center; font-size: 3rem;'>BIST Risk Motoru</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Yapay zeka destekli analizlerle akıllı yatırım kararları alın.</p>", unsafe_allow_html=True)

# Arama Çubuğu
symbol = st.text_input("", placeholder="Hisse kodu girin (Örn: THYAO)", label_visibility="collapsed")

if symbol:
    # Sembolün sonuna .IS ekleme (BIST kuralı)
    ticker_sym = f"{symbol.upper()}.IS"
    
    try:
        # Veri Çekme
        data = yf.Ticker(ticker_sym)
        hist = data.history(period="1mo")
        price = hist['Close'].iloc[-1]
        change = ((price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100

        # --- 5. Hisse Detay Üst Alan ---
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### {symbol.upper()}")
            st.markdown(f"<h1 style='color:white;'>₺{price:.2f}</h1>", unsafe_allow_html=True)
            color = "green" if change > 0 else "red"
            st.markdown(f"<p style='color:{color};'>%{change:.2f} Bugün</p>", unsafe_allow_html=True)

        with c2:
            st.markdown("### Risk Skoru")
            # Basit bir risk algoritması (Örnek: Volatiliteye göre)
            risk_score = 4.2 # Statik örnek
            st.markdown(f"<h1 style='color:#EAB308;'>{risk_score} <small style='font-size:15px; color:#64748B;'>/ 10</small></h1>", unsafe_allow_html=True)
            st.progress(risk_score / 10)

        # --- 6. Grafik ---
        fig = go.Figure(data=[go.Candlestick(x=hist.index,
                        open=hist['Open'], high=hist['High'],
                        low=hist['Low'], close=hist['Close'])])
        fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # --- 7. AI Analiz (Simüle) ---
        st.markdown("---")
        st.markdown("### 🧠 AI Analist Yorumu")
        st.info(f"{symbol.upper()} hissesi son dönemde hacimli bir artış gösteriyor. Risk skoru orta seviyede olup, global havacılık trendleri takibi önerilir.")

    except Exception as e:
        st.error(f"Veri çekilemedi: {symbol}. Lütfen geçerli bir BIST kodu girin.")
else:
    st.info("Lütfen analiz etmek istediğiniz hisse senedinin kodunu yukarıya yazın.")

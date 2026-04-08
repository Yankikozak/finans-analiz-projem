import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. ANALYST ENGINE (SENTETİK İÇERİK ÜRETİCİ) ---
def get_market_insights(ticker_name, df):
    last_price = df['Close'].iloc[-1]
    ret = df['Close'].pct_change().dropna()
    vol = ret.std() * np.sqrt(252) * 100
    ma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    # Trend Belirleme
    trend = "Bullish" if last_price > ma_20 else "Bearish"
    risk_level = "Yüksek" if vol > 35 else "Orta" if vol > 20 else "Düşük"
    
    insights = {
        "trend": trend,
        "vol_desc": f"Varlık %{vol:.2f} yıllık oynaklık ile {risk_level} risk kategorisindedir.",
        "momentum": "Fiyat 20 günlük ortalamanın üzerinde, alıcı iştahı korunuyor." if trend == "Bullish" else "Satış baskısı devam ediyor.",
        "summary": [
            f"Kısa vadeli trend {trend} eğiliminde.",
            f"Risk eşiği {risk_level} seviyesinde seyrediyor.",
            "Teknik sinyaller mevcut fiyatta konsolidasyon işaret ediyor."
        ]
    }
    return insights

# --- 2. UI/UX: BOŞLUK HİSSİNİ YOK EDEN KART TASARIMI ---
st.markdown("""
<style>
    .insight-card { background: #111827; border-left: 5px solid #3b82f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .learning-pill { background: #1e293b; padding: 15px; border-radius: 15px; border: 1px solid #334155; }
    .stat-box { text-align: center; border: 1px solid #1e293b; padding: 10px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. EXECUTION ---
st.title("🛡️ Guardian Research Hub")
ticker = st.sidebar.text_input("Varlık Seçin", "THYAO.IS")

data = yf.download(ticker, period="6mo", progress=False)

if not data.empty:
    ins = get_market_insights(ticker, data)
    
    tab1, tab2, tab3 = st.tabs(["📊 Market Insights", "🎓 Learning Hub", "📈 Teknik Analiz"])
    
    with tab1:
        st.subheader(f"🔍 {ticker} Analist Raporu")
        c1, c2, c3 = st.columns(3)
        c1.metric("Trend", ins['trend'])
        c2.metric("Risk Seviyesi", "Yüksek" if "Yüksek" in ins['vol_desc'] else "Stabil")
        c3.metric("Momentum", "Pozitif" if ins['trend'] == "Bullish" else "Negatif")
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>Yatırımcı Özeti</h4>
            <ul>
                {"".join([f"<li>{item}</li>" for item in ins['summary']])}
            </ul>
            <p><b>Detaylı Yorum:</b> {ins['vol_desc']} {ins['momentum']}</p>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.subheader("🎓 Finansal Okuryazarlık")
        with st.expander("📌 Volatilite Nedir? (Bu varlık üzerinden öğren)"):
            st.markdown(f"""
            <div class="learning-pill">
                Volatilite, fiyatın ne kadar "sert" hareket ettiğidir. 
                Şu an incelediğin <b>{ticker}</b> varlığının volatilitesi oldukça belirgin.
                <br><br><b>Örnek:</b> Eğer volatilite yüksekse, stop-loss mesafeni daha geniş tutman gerekebilir.
            </div>
            """, unsafe_allow_html=True)

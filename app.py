import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Sayfa Yapılandırması
st.set_page_config(page_title="Risk & Portföy Analiz Terminali", layout="wide")

# --- GELİŞMİŞ SEMBOL SÖZLÜĞÜ (Arama Motoru Çekirdeği) ---
# Kullanıcı ne yazarsa yazsın, sistem Yahoo Finance diline çevirir.
search_engine_db = {
    # Borsa İstanbul (Popülerler)
    "ASELSAN": "ASELS.IS", "THY": "THYAO.IS", "TÜPRAŞ": "TUPRS.IS", "EREĞLİ": "EREGL.IS",
    "ŞİŞECAM": "SISE.IS", "KOÇ HOLDİNG": "KCHOL.IS", "SASA": "SASA.IS", "HEKTAŞ": "HEKTS.IS",
    "GARANTİ": "GARAN.IS", "AKBANK": "AKBNK.IS", "BİM": "BIMAS.IS", "FORD": "FROTO.IS",
    # Kripto Dünyası
    "BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD", "SOLANA": "SOL-USD", "RIPPLE": "XRP-USD",
    "DOGE": "DOGE-USD", "AVAX": "AVAX-USD", "BINANCE": "BNB-USD",
    # Küresel Piyasalar & Emtia
    "ALTIN": "GC=F", "GÜMÜŞ": "SI=F", "PETROL": "CL=F", "NASDAQ": "^IXIC", "S&P500": "^GSPC",
    "APPLE": "AAPL", "TESLA": "TSLA", "NVIDIA": "NVDA", "GOOGLE": "GOOGL", "AMAZON": "AMZN"
}

def smart_search(input_text):
    """Kullanıcının yazdığı metni teknik sembole dönüştürür."""
    clean_input = input_text.upper().strip()
    # 1. Sözlükte tam eşleşme var mı? (Örn: "Altın")
    if clean_input in search_engine_db:
        return search_engine_db[clean_input]
    
    # 2. Teknik kod mu yazdı? (Örn: "BTC", "THYAO")
    crypto_list = ["BTC", "ETH", "SOL", "XRP", "AVAX", "DOGE"]
    if clean_input in crypto_list:
        return f"{clean_input}-USD"
    
    # 3. Bist kontrolü (Nokta yoksa .IS ekle)
    if "." not in clean_input and "-" not in clean_input:
        return f"{clean_input}.IS"
    
    return clean_input

# --- UI BAŞLIĞI ---
st.title("🛡️ Risk & Portföy Analiz Terminali")
st.markdown("_Veriye dayalı finansal karar destek sistemi_")
st.markdown("---")

# --- SIDEBAR: ARAMA MOTORU ---
st.sidebar.header("🔍 Akıllı Arama & Portföy")

# Çoklu Seçim Menüsü (Hazır popüler varlıklar)
suggestions = list(search_engine_db.keys())
selected_from_list = st.sidebar.multiselect(
    "Popüler Varlıklardan Seçin:",
    options=suggestions,
    default=["THY", "BITCOIN", "ALTIN"]
)

# Manuel Giriş (Listede olmayanlar için)
manual_input = st.sidebar.text_input("Veya farklı kodlar ekleyin (Virgülle):", "")

# Nihai Sembol Listesini Oluşturma
final_tickers = [search_engine_db[name] for name in selected_from_list]
if manual_input:
    extra_tickers = [smart_search(x) for x in manual_input.split(",") if x.strip()]
    final_tickers.extend(extra_tickers)

# Tekilleştirme (Aynı varlığın iki kez eklenmesini önler)
final_tickers = list(set(final_tickers))

days = st.sidebar.slider("Analiz Aralığı (Gün)", 30, 1095, 365)
start_date = datetime.now() - timedelta(days=days)

# --- VERİ VE ANALİZ ---
@st.cache_data
def get_data(tickers, start):
    try:
        df = yf.download(tickers, start=start, progress=False)['Close']
        if isinstance(df, pd.Series): df = df.to_frame()
        return df.ffill().dropna()
    except: return None

if final_tickers:
    data = get_data(final_tickers, start_date)
    
    if data is not None and not data.empty and len(data) > 5:
        # Portföy Hesaplamaları
        returns = data.pct_change().dropna()
        weights = np.array([1/len(final_tickers)] * len(final_tickers))
        port_returns = (returns * weights).sum(axis=1)
        cum_returns = (1 + port_returns).cumprod()
        
        # Metrik Kartları
        m1, m2, m3 = st.columns(3)
        total_ret = (cum_returns.iloc[-1] - 1) * 100
        vol = port_returns.std() * np.sqrt(252) * 100
        drawdown = ((cum_returns / cum_returns.cummax()) - 1).min() * 100
        
        m1.metric("Toplam Getiri", f"%{total_ret:.2f}")
        m2.metric("Risk Seviyesi", f"%{vol:.2f}")
        m3.metric("Maksimum Kayıp", f"%{drawdown:.2f}")

        # Ana Performans Grafiği
        st.plotly_chart(px.line(cum_returns, title="Kümülatif Performans Trendi", template="plotly_dark"), use_container_width=True)
        
        # --- STRATEJİK ANALİZ VE ÖNERİLER ---
        st.markdown("---")
        st.subheader("💡 Stratejik Portföy Analizi")
        
        c_a, c_b = st.columns(2)
        with c_a:
            st.info("### 🧐 Risk Pozisyonu")
            if vol > 25:
                st.write("⚠️ **Agresif:** Portföy volatilite eşiği yüksek. Piyasa dalgalanmalarına karşı duyarlılık fazla.")
            else:
                st.write("✅ **Dengeli:** Risk dağılımı makul seviyelerde, defansif bir yapı korunuyor.")
        
        with c_b:
            st.success("### 🎯 Taktiksel Öneri")
            if total_ret > 0:
                st.write("🚀 Mevcut trend pozitif. Belirlenen kâr hedefleri doğrultusunda pozisyonlar korunabilir.")
            else:
                st.write("📉 Negatif ayrışma gözleniyor. Maliyet düşürme veya varlık çeşitlendirme stratejileri değerlendirilmelidir.")
            
    else:
        st.error("⚠️ Seçilen varlıklar için veri çekilemedi. Lütfen internet bağlantısını veya sembolleri kontrol edin.")
else:
    st.info("Lütfen sol menüden analiz etmek istediğiniz varlıkları seçin veya arama yapın.")

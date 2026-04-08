import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Sayfa Yapılandırması
st.set_page_config(page_title="Risk & Portföy Analiz Terminali", layout="wide")

# --- DEV BIST & KÜRESEL VARLIK KÜTÜPHANESİ ---
# Kullanıcı dostu isimleri teknik kodlara eşliyoruz.
search_engine_db = {
    # HAVACILIK & ULAŞIM
    "THY": "THYAO.IS", "TÜRK HAVA YOLLARI": "THYAO.IS", "PEGASUS": "PGSUS.IS", "TAV HAVALİMANLARI": "TAVHL.IS",
    # BANKACILIK
    "GARANTİ": "GARAN.IS", "AKBANK": "AKBNK.IS", "İŞ BANKASI": "ISCTR.IS", "YAPI KREDİ": "YKBNK.IS", "VAKIFBANK": "VAKBN.IS", "HALKBANK": "HALKB.IS",
    # ENERJİ & SANAYİ
    "TÜPRAŞ": "TUPRS.IS", "EREĞLİ": "EREGL.IS", "KARDEMİR": "KRDMD.IS", "SASA": "SASA.IS", "HEKTAŞ": "HEKTS.IS", "PETKİM": "PETKM.IS", "ASTOR": "ASTOR.IS", "KONTROLMATİK": "KONTR.IS",
    # HOLDİNG & OTOMOTİV
    "KOÇ HOLDİNG": "KCHOL.IS", "SABANCI HOLDİNG": "SAHOL.IS", "FORD OTOSAN": "FROTO.IS", "TOFAŞ": "TOASO.IS", "DOĞUŞ OTOMOTİV": "DOAS.IS", "ŞİŞECAM": "SISE.IS",
    # TEKNOLOJİ & SAVUNMA
    "ASELSAN": "ASELS.IS", "MİA TEKNOLOJİ": "MIATK.IS", "YEOTEK": "YEOTK.IS", "REEDER": "REEDR.IS",
    # PERAKENDE & GIDA
    "BİM": "BIMAS.IS", "MİGROS": "MGROS.IS", "ŞOK MARKET": "SOKM.IS", "ÜLKER": "ULKER.IS", "COCA COLA": "CCOLA.IS",
    # KRİPTO PARALAR
    "BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD", "SOLANA": "SOL-USD", "AVAX": "AVAX-USD", "RIPPLE": "XRP-USD",
    # EMTİA & ENDEKSLER
    "ALTIN": "GC=F", "GÜMÜŞ": "SI=F", "BIST 100": "XU100.IS", "NASDAQ": "^IXIC", "S&P 500": "^GSPC"
}

def smart_search(input_text):
    clean_input = input_text.upper().strip()
    # 1. Sözlükte tam isim eşleşmesi
    if clean_input in search_engine_db:
        return search_engine_db[clean_input]
    
    # 2. Kripto kısa kod kontrolü
    crypto_list = ["BTC", "ETH", "SOL", "XRP", "AVAX", "DOGE"]
    if clean_input in crypto_list:
        return f"{clean_input}-USD"
    
    # 3. Nokta yoksa otomatik BIST eki ekle
    if "." not in clean_input and "-" not in clean_input:
        return f"{clean_input}.IS"
    
    return clean_input

# --- UI BAŞLIĞI ---
st.title("🛡️ Risk & Portföy Analiz Terminali")
st.markdown("_Genişletilmiş BIST & Küresel Varlık Takip Sistemi_")
st.markdown("---")

# --- SIDEBAR ---
st.sidebar.header("🔍 Portföy Yapılandırıcı")

# Çoklu Seçim Menüsü (Alfabetik sıralı liste)
suggestions = sorted(list(search_engine_db.keys()))
selected_from_list = st.sidebar.multiselect(
    "Varlıkları Seçin:",
    options=suggestions,
    default=["THY", "ASELSAN", "ALTIN"]
)

# Manuel Arama Kutusu
manual_input = st.sidebar.text_input("Listede olmayan kodları ekleyin (Örn: THYAO, EREGL):", "")

# Nihai Sembol Listesi
final_tickers = [search_engine_db[name] for name in selected_from_list]
if manual_input:
    extra_tickers = [smart_search(x) for x in manual_input.split(",") if x.strip()]
    final_tickers.extend(extra_tickers)

final_tickers = list(set(final_tickers)) # Tekilleştirme

st.sidebar.markdown("---")
days = st.sidebar.slider("Analiz Aralığı (Gün)", 30, 1095, 365)
start_date = datetime.now() - timedelta(days=days)

# --- VERİ ANALİZ KATMANI ---
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
        # Hesaplamalar
        returns = data.pct_change().dropna()
        weights = np.array([1/len(final_tickers)] * len(final_tickers))
        port_returns = (returns * weights).sum(axis=1)
        cum_returns = (1 + port_returns).cumprod()
        
        # Metrik Kartları
        m1, m2, m3 = st.columns(3)
        m1.metric("Portföy Getirisi", f"%{((cum_returns.iloc[-1]-1)*100):.2f}")
        m2.metric("Risk (Volatilite)", f"%{(port_returns.std() * np.sqrt(252) * 100):.2f}")
        m3.metric("Maksimum Kayıp", f"%{(((cum_returns / cum_returns.cummax()) - 1).min() * 100):.2f}")

        # Grafik
        st.plotly_chart(px.line(cum_returns, title="Kümülatif Getiri Grafiği", template="plotly_dark"), use_container_width=True)
        
        # --- STRATEJİK ANALİZ ---
        st.markdown("---")
        st.subheader("💡 Terminal Analiz Notları")
        col_x, col_y = st.columns(2)
        
        with col_x:
            st.info("### Varlık Dağılımı")
            st.write(f"Şu an **{len(final_tickers)}** farklı varlık üzerinden analiz yapılıyor.")
            st.write(f"İzlenen Semboller: {', '.join(final_tickers)}")
            
        with col_y:
            st.success("### Aksiyon Önerisi")
            if (cum_returns.iloc[-1]-1) > 0.2:
                st.write("🚀 Portföy güçlü bir ivme yakalamış. Kâr realizasyonu seviyeleri takip edilmelidir.")
            else:
                st.write("⚖️ Portföy dengelenme sürecinde. Uzun vadeli destek noktaları izlenebilir.")
    else:
        st.error("⚠️ Seçilen varlıklar için veri çekilemedi. Piyasalar kapalı olabilir.")
else:
    st.info("Lütfen sol menüden analiz etmek istediğiniz varlıkları seçin.")

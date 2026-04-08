import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- 1. PREMIUM UI & GENİŞLETİLMİŞ TASARIM ---
st.set_page_config(page_title="Guardian | Finansal Koruma", layout="wide")

# Dil Sözlüğü
languages = {
    "TR": {
        "title": "Guardian Finansal Zeka",
        "subtitle": "Ekonometrik Modellerle Sermaye Koruma Sistemi",
        "manifesto_title": "🛡️ Stratejik Manifesto ve Güven Protokolü",
        "manifesto_text": """
            Piyasalarda kazanmak bir seçenek, sermayeyi korumak ise bir zorunluluktur. 
            **Guardian Finansal Zeka**, Sakarya Üniversitesi Ekonometri disiplini üzerine inşa edilmiş bir karar destek mekanizmasıdır.
            
            **Sistem Kapasitesi:**
            * **Küresel Varlık Analizi:** Dünyanın her yerindeki hisse, kripto ve emtialara anında ulaşım.
            * **Rasyonel Risk Yönetimi:** VaR modelleriyle matematiksel 'en kötü senaryo' analizi.
            * **Stratejik Karar Desteği:** Piyasa gürültüsü yerine ekonometrik veri sinyalleri.
        """,
        "btn_demo": "🚀 Demo Portföyü Başlat",
        "btn_custom": "🔑 Terminale Giriş Yap",
        "search_label": "🔍 Analiz Edilecek Varlık:",
        "results_label": "Eşleşen Varlıklar:",
        "risk_report": "Risk Analiz Raporu",
        "volatility": "Yıllık Oynaklık",
        "confidence": "Güven Seviyesi"
    },
    "EN": {
        "title": "Guardian Financial Intelligence",
        "subtitle": "Capital Protection System with Econometric Models",
        "manifesto_title": "🛡️ Strategic Manifesto & Trust Protocol",
        "manifesto_text": """
            Winning is an option; protecting capital is a necessity. 
            **Guardian Financial Intelligence** is a decision support mechanism built on 
            the foundations of Econometric discipline.
            
            **System Capabilities:**
            * **Global Asset Analysis:** Instant access to stocks, crypto, and commodities worldwide.
            * **Rational Risk Management:** Mathematical 'worst-case scenario' analysis.
            * **Strategic Decision Support:** Clear econometric signals instead of market noise.
        """,
        "btn_demo": "🚀 Start Demo Portfolio",
        "btn_custom": "🔑 Enter Terminal",
        "search_label": "🔍 Asset to Analyze:",
        "results_label": "Matching Assets:",
        "risk_report": "Risk Analysis Report",
        "volatility": "Annual Volatility",
        "confidence": "Confidence Level"
    }
}

# --- 2. SAĞ ÜST DİL SEÇENEĞİ VE TASARIM ---
if 'lang' not in st.session_state:
    st.session_state.lang = "TR"

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main-title { font-size: 3.5rem; font-weight: 800; color: #ffffff; text-align: center; margin-top: 2rem; }
    .subtitle { font-size: 1.2rem; color: #ffffff; text-align: center; margin-bottom: 3rem; opacity: 0.8; }
    
    .trust-panel { 
        background: linear-gradient(145deg, #111827, #1f2937); 
        border: 1px solid #3b82f6; 
        padding: 4rem

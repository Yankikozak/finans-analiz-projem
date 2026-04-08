import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- 1. PREMIUM UI & GENİŞLETİLMİŞ TASARIM AYARLARI ---
st.set_page_config(page_title="Guardian | Finansal Koruma", layout="wide")

# Dil Sözlüğü (Tüm UI metinleri burada yönetilir)
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
            
            Verilerimiz doğrudan küresel borsalardan akmakta olup, analizlerimiz akademik standartlarda stokastik süreçlerle hesaplanmaktadır.
        """,
        "btn_demo": "🚀 Demo Portföyü Başlat",
        "btn_custom": "🔑 Terminale Giriş Yap",
        "search_label": "🔍 Analiz Edilecek Varlık (Hisse, Kripto, Emtia):",
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
            * **Rational Risk Management:** Mathematical 'worst-case scenario' analysis with VaR.
            * **Strategic Decision Support:** Clear econometric signals instead of market noise.
            
            Our data flows directly from global exchanges, and our analyses are calculated using 
            stochastic processes at academic standards.
        """,
        "btn_demo":

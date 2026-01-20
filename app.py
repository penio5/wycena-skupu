import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import time
import pandas as pd

st.set_page_config(page_title="Monitor Skupów", layout="wide")

# --- FUNKCJE SCRAPERA ---
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

def scrapuj_skup_telefonow(driver, url):
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        form = soup.find('form', class_='variations_form')
        if not form: return None
        
        variants = json.loads(form.get('data-product_variations'))
        results = {}
        for v in variants:
            attr = v['attributes']
            # Filtr: Inna + Brak rat
            raty = str(attr.get('attribute_pa_system-ratalny', '')).lower()
            sklep = str(attr.get('attribute_pa_kupiony-w', '')).lower()
            if raty == 'nie' and sklep == 'inna':
                stan = str(attr.get('attribute_pa_wybierz-stan', attr.get('attribute_pa_stan-produktu', ''))).upper()
                results[stan] = float(v['display_price'])
        return results
    except: return None

# --- INTERFEJS ---
st.title("📈 Twój Monitor Cen Skupu")

# Prosta baza danych w pamięci sesji (można rozbudować o plik)
if 'baza_linkow' not in st.session_state:
    st.session_state.baza_linkow = []

with st.expander("➕ Dodaj nowy model do porównania"):
    nazwa = st.text_input("Nazwa urządzenia (np. iPhone 16 Pro)")
    link1 = st.text_input("Link SkupTelefonow.pl")
    link2 = st.text_input("Link ElektroSkup.pl (lub inny)")
    if st.button("Zapisz w bazie"):
        st.session_state.baza_linkow.append({"nazwa": nazwa, "skup_tel": link1, "elektro": link2})
        st.success("Dodano!")

if st.session_state.baza_linkow:
    st.subheader("Twoja Lista Monitorowania")
    for i, item in enumerate(st.session_state.baza_linkow):
        st.write(f"{i+1}. **{item['nazwa']}**")
    
    if st.button("🚀 ODPAL MONITORING WSZYSTKICH CEN"):
        all_results = []
        driver = get_driver()
        progress = st.progress(0)
        
        for idx, item in enumerate(st.session_state.baza_linkow):
            st.write(f"Sprawdzam: {item['nazwa']}...")
            
            # Pobieramy dane ze SkupTelefonow
            ceny_skup = scrapuj_skup_telefonow(driver, item['skup_tel'])
            
            if ceny_skup:
                for stan, cena in ceny_skup.items():
                    all_

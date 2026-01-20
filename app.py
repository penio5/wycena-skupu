import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import time
import pandas as pd

st.set_page_config(page_title="Monitor Skupów PRO", layout="wide")

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

# --- SCRAPER SKUPTELEFONOW ---
def scrapuj_skup_telefonow(driver, url):
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        form = soup.find('form', class_='variations_form')
        if not form: return {}
        
        variants = json.loads(form.get('data-product_variations'))
        results = {}
        for v in variants:
            attr = v['attributes']
            # Filtrujemy tylko brak rat i pochodzenie "inna"
            raty = str(attr.get('attribute_pa_system-ratalny', '')).lower()
            sklep = str(attr.get('attribute_pa_kupiony-w', '')).lower()
            if raty == 'nie' and sklep == 'inna':
                stan = str(attr.get('attribute_pa_wybierz-stan', attr.get('attribute_pa_stan-produktu', ''))).upper()
                results[stan] = int(v['display_price'])
        return results
    except: return {}

# --- SCRAPER ELEKTROSKUP ---
def scrapuj_elektroskup(driver, url):
    try:
        driver.get(url)
        time.sleep(3)
        results = {}
        # Mapowanie nazw przycisków na standardowe stany
        stany_do_klikniecia = {
            "IDEALNY": "Idealny",
            "BARDZO DOBRY": "Bardzo dobry",
            "DOBRY": "Dobry",
            "DOSTATECZNY": "Dostateczny"
        }
        
        for klucz, tekst in stany_do_klikniecia.items():
            try:
                # Szukamy przycisku stanu i klikamy go
                buttons = driver.find_elements(By.CLASS_NAME, "variant-name")
                for btn in buttons:
                    if tekst in btn.text:
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(1)
                        # Pobieramy nową cenę po kliknięciu
                        cena_txt = driver.find_element(By.ID, "price_amount").text
                        cena = int(''.join(filter(str.isdigit, cena_txt)))
                        results[klucz] = cena
                        break
            except: continue
        return results
    except: return {}

# --- INTERFEJS ---
st.title("🚀 Twój Panel Porównawczy")

if 'baza' not in st.session_state:
    st.session_state.baza = []

with st.expander("➕ Dodaj nową parę do monitorowania"):
    c1, c2, c3 = st.columns(3)
    nazwa = c1.text_input("Nazwa modelu")
    l1 = c2.text_input("Link SkupTelefonow")
    l2 = c3.text_input("Link ElektroSkup")
    if st.button("Zapisz w mojej bazie"):
        st.session_state.baza.append({"nazwa": nazwa, "l1": l1, "l2": l2})
        st.success("Zapisano!")

if st.session_state.baza:
    if st.button("🔄 ODŚWIEŻ WSZYSTKIE CENY"):
        driver = get_driver()
        final_data = []
        
        for item in st.session_state.baza:
            with st.status(f"Analizuję: {item['nazwa']}...", expanded=False):
                dane_skup = scrapuj_skup_telefonow(driver, item['l1'])
                dane_elektro = scrapuj_elektroskup(driver, item['l2'])
                
                # Łączymy wyniki w jeden wiersz dla każdego stanu
                wszystkie_stany = set(list(dane_skup.keys()) + list(dane_elektro.keys()))
                for s in wszystkie_stany:
                    # Czyścimy nazwy stanów dla porównania
                    s_clean = s.replace("UŻYWANY ", "").strip()
                    final_data.append({
                        "Urządzenie": item['nazwa'],
                        "Stan": s_clean,
                        "SkupTelefonow (Inna/Nie)": f"{dane_skup.get(s, '---')} zł",
                        "ElektroSkup": f"{dane_elektro.get(s_clean, '---')} zł"
                    })
        
        driver.quit()
        if final_data:
            st.subheader("Zestawienie Cenowe")
            df = pd.DataFrame(final_data)
            st.dataframe(df, use_container_width=True)
else:
    st.info("Dodaj pierwsze linki, aby rozpocząć monitoring.")

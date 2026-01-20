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

# --- SCRAPER SKUPTELEFONOW (Poprawiony pod nowe atrybuty) ---
def scrapuj_skup_telefonow(driver, url):
    try:
        driver.get(url)
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        form = soup.find('form', class_='variations_form')
        if not form: return {}
        
        variants = json.loads(form.get('data-product_variations'))
        results = {}
        for v in variants:
            attr = v['attributes']
            # Filtry: nie-raty i inna (ignorujemy wielkość liter)
            raty = str(attr.get('attribute_pa_system-ratalny', '')).lower()
            sklep = str(attr.get('attribute_pa_kupiony-w', '')).lower()
            
            if (raty == 'nie' or raty == '') and (sklep == 'inna' or sklep == ''):
                # Próbujemy różnych nazw atrybutu stanu, które widzieliśmy w logach
                stan = (attr.get('attribute_pa_stan-produktu') or 
                        attr.get('attribute_pa_wybierz-stan') or 
                        "NIEZNANY").upper()
                results[stan] = int(v['display_price'])
        return results
    except Exception as e:
        st.error(f"Błąd SkupTelefonow: {e}")
        return {}

# --- SCRAPER ELEKTROSKUP (Ulepszone klikanie) ---
def scrapuj_elektroskup(driver, url):
    try:
        driver.get(url)
        time.sleep(5)
        results = {}
        stany = ["Idealny", "Bardzo dobry", "Dobry", "Dostateczny"]
        
        for s_name in stany:
            try:
                # Szukamy etykiety stanu i klikamy
                label = driver.find_element(By.XPATH, f"//label[contains(text(), '{s_name}')]")
                driver.execute_script("arguments[0].click();", label)
                time.sleep(2) # Czekamy na przeliczenie ceny
                
                cena_elem = driver.find_element(By.ID, "price_amount")
                cena_val = ''.join(filter(str.isdigit, cena_elem.text))
                if cena_val:
                    results[s_name.upper()] = int(cena_val)
            except:
                continue
        return results
    except Exception as e:
        st.error(f"Błąd ElektroSkup: {e}")
        return {}

# --- INTERFEJS ---
st.title("📊 Twój Panel Porównawczy")

if 'baza' not in st.session_state:
    st.session_state.baza = []

with st.expander("➕ Dodaj urządzenia do bazy"):
    c1, c2, c3 = st.columns(3)
    n = c1.text_input("Nazwa (np. iPhone 16 Pro)")
    l1 = c2.text_input("Link SkupTelefonow")
    l2 = c3.text_input("Link ElektroSkup")
    if st.button("Zapisz"):
        st.session_state.baza.append({"nazwa": n, "l1": l1, "l2": l2})

if st.session_state.baza:
    if st.button("🔄 POBIERZ AKTUALNE CENY"):
        driver = get_driver()
        all_rows = []
        
        for item in st.session_state.baza:
            st.info(f"Pobieram: {item['nazwa']}...")
            res1 = scrapuj_skup_telefonow(driver, item['l1'])
            res2 = scrapuj_elektroskup(driver, item['l2'])
            
            # Łączymy wyniki w tabelę
            klucze = set(list(res1.keys()) + list(res2.keys()))
            for k in klucze:
                # Normalizacja nazw stanów do porównania
                clean_k = k.replace("UŻYWANY ", "").strip()
                all_rows.append({
                    "Urządzenie": item['nazwa'],
                    "Stan": clean_k,
                    "SkupTelefonow": f"{res1.get(k, '---')} zł",
                    "ElektroSkup": f"{res2.get(clean_k, '---')} zł"
                })
        
        driver.quit()
        if all_rows:
            st.table(pd.DataFrame(all_rows))

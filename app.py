import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import time

st.set_page_config(page_title="Wyceniarka", layout="wide")

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # Ścieżka do Chromium w systemie Debian (z packages.txt)
    options.binary_location = "/usr/bin/chromium"
    
    # Używamy systemowego sterownika zainstalowanego przez packages.txt
    service = Service("/usr/bin/chromedriver")
    
    return webdriver.Chrome(service=service, options=options)

st.title("Skup Urządzeń - Wyceń model 📱")

url = st.text_input("Wklej link z skuptelefonow.pl:", "https://skuptelefonow.pl/telefon/iphone-16-pro-256gb/")

if st.button("Sprawdź cenę konkurencji"):
    with st.spinner("Bot sprawdza ceny..."):
        driver = None
        try:
            driver = get_driver()
            driver.get(url)
            time.sleep(5)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            form = soup.find('form', class_='variations_form')
            
            if form:
                variants = json.loads(form.get('data-product_variations'))
                st.success(f"Pobrano pomyślnie {len(variants)} wariantów")
                
                for v in variants:
                    stan = v['attributes'].get('attribute_pa_stan-produktu', 'Inny')
                    cena = v['display_price']
                    
                    with st.expander(f"STAN: {stan.replace('-', ' ').upper()}"):
                        c1, c2 = st.columns(2)
                        c1.metric("Cena konkurencji", f"{cena} zł")
                        c2.metric("Twoja propozycja", f"{round(float(cena) * 0.88)} zł")
            else:
                st.error("Nie znaleziono tabeli cen. Upewnij się, że link prowadzi do konkretnego modelu.")
                
        except Exception as e:
            st.error(f"Błąd: {e}")
        finally:
            if driver:
                driver.quit()

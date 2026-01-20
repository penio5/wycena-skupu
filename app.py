import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
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
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    # Próba uruchomienia z automatycznym pobraniem sterownika
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    return webdriver.Chrome(service=service, options=options)

st.title("Skup Urządzeń - Wyceń model 📱")

url = st.text_input("Wklej link z kuptelefonow.pl:", "https://skuptelefonow.pl/telefon/iphone-16-pro-256gb/")

if st.button("Sprawdź cenę konkurencji"):
    with st.spinner("Bot pracuje..."):
        try:
            driver = get_driver()
            driver.get(url)
            time.sleep(4)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            form = soup.find('form', class_='variations_form')
            
            if form:
                variants = json.loads(form.get('data-product_variations'))
                for v in variants:
                    stan = v['attributes'].get('attribute_pa_stan-produktu', 'Inny')
                    cena = v['display_price']
                    
                    with st.expander(f"STAN: {stan.upper()}"):
                        c1, c2 = st.columns(2)
                        c1.metric("Cena konkurencji", f"{cena} zł")
                        c2.metric("Twoja cena (-200 zł)", f"{cena - 200} zł")
            else:
                st.error("Nie znaleziono wariantów. Sprawdź, czy na stronie są przyciski wyboru stanu.")
            
            driver.quit()
        except Exception as e:
            st.error(f"Szczegóły błędu dla programisty: {e}")

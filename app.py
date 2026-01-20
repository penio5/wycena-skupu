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
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

st.title("Szybka Wycena Odkupu 📱")

url = st.text_input("Wklej link do modelu:", "https://skuptelefonow.pl/telefon/iphone-16-pro-256gb/")

if st.button("Pobierz wszystkie ceny"):
    with st.spinner("Pobieram dane..."):
        driver = None
        try:
            driver = get_driver()
            driver.get(url)
            time.sleep(5)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            form = soup.find('form', class_='variations_form')
            
            if form:
                all_variants = json.loads(form.get('data-product_variations'))
                
                st.subheader("Wszystkie znalezione warianty cenowe:")
                
                for v in all_variants:
                    attr = v['attributes']
                    cena = v['display_price']
                    
                    # Tworzymy opis wariantu z dostępnych atrybutów
                    opis_czesci = [str(val).replace('-', ' ').upper() for val in attr.values() if val]
                    opis = " | ".join(opis_czesci) if opis_czesci else "WARIANT PODSTAWOWY"
                    
                    with st.container():
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.write(f"**{opis}**")
                        c2.metric("Skup", f"{cena} zł")
                        # Twoja cena z marżą 12%
                        twoja = round(float(cena) * 0.88)
                        c3.metric("Twoja Oferta", f"{twoja} zł", delta=f"-{int(cena-twoja)} zł")
                        st.divider()
            else:
                st.error("Brak danych o wariantach. Sprawdź link.")
                
        except Exception as e:
            st.error(f"Błąd: {e}")
        finally:
            if driver:
                driver.quit()

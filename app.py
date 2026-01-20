import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import time

# Ustawienia strony
st.set_page_config(page_title="Wyceniarka", layout="centered")

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

if st.button("Pobierz konkrety"):
    with st.spinner("Filtruję dane..."):
        driver = None
        try:
            driver = get_driver()
            driver.get(url)
            time.sleep(4)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            form = soup.find('form', class_='variations_form')
            
            if form:
                all_variants = json.loads(form.get('data-product_variations'))
                
                st.subheader("Wyniki dla: Kupiony w Inna / System ratalny: NIE")
                
                found = False
                for v in all_variants:
                    attr = v['attributes']
                    
                    # FILTRY: Interesują nas tylko te warianty
                    is_inna = attr.get('attribute_pa_kupiony-w') == 'inna'
                    is_not_raty = attr.get('attribute_pa_system-ratalny') == 'nie'
                    
                    if is_inna and is_not_raty:
                        found = True
                        stan = attr.get('attribute_pa_stan-produktu', 'Nieznany').replace('-', ' ').upper()
                        cena = float(v['display_price'])
                        
                        # Wyświetlanie w czytelny sposób
                        with st.container():
                            c1, c2, c3 = st.columns([2, 1, 1])
                            c1.info(f"**STAN: {stan}**")
                            c2.metric("Skup", f"{cena} zł")
                            # Automatyczne liczenie Twojej ceny (np. 10% marży)
                            c3.metric("Twoja oferta", f"{round(cena * 0.90)} zł")
                
                if not found:
                    st.warning("Nie znaleziono wariantów pasujących do filtrów (Inna/Brak rat).")
            else:
                st.error("Nie udało się pobrać danych. Upewnij się, że link jest poprawny.")
                
        except Exception as e:
            st.error(f"Błąd: {e}")
        finally:
            if driver:
                driver.quit()

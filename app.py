import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from bs4 import BeautifulSoup
import json
import time

st.set_page_config(page_title="Asystent Wyceny", page_icon="📱")
st.title("Asystent Wyceny Skupu 📱")

url = st.text_input("Wklej link do produktu:", "https://skuptelefonow.pl/telefon/iphone-16-pro-256gb/")

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Ta linia automatycznie znajdzie Chromium na serwerze Streamlit
    return webdriver.Chrome(
        service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
        options=options
    )

if st.button("Pobierz aktualne ceny"):
    with st.spinner('Uruchamiam silnik wyceny...'):
        try:
            driver = get_driver()
            driver.get(url)
            time.sleep(5) # Dajemy stronie czas na załadowanie cen
            
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Szukanie danych wariacji
            form = soup.find('form', class_='variations_form')
            
            if form and form.get('data-product_variations'):
                variants = json.loads(form.get('data-product_variations'))
                st.success(f"Znaleziono {len(variants)} wariantów stanu")
                
                for v in variants:
                    stan = v['attributes'].get('attribute_pa_stan-produktu', 'Nieznany')
                    cena = v['display_price']
                    
                    with st.container():
                        c1, c2, c3 = st.columns([2,1,1])
                        c1.subheader(stan.replace('-', ' ').upper())
                        c2.metric("Cena skupu", f"{cena} zł")
                        # Twoja propozycja (np. marża 15%)
                        c3.metric("Twoja oferta", f"{round(cena * 0.85)} zł", delta="-15%")
                        st.divider()
            else:
                st.warning("Nie znaleziono wariantów cenowych. Sprawdź czy link jest poprawny.")
                
            driver.quit()
        except Exception as e:
            st.error(f"Błąd krytyczny: {str(e)}")

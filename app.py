import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

st.title("Asystent Wyceny Skupu 📱")

url = st.text_input("Wklej link do produktu:", "https://skuptelefonow.pl/telefon/iphone-16-pro-256gb/")

if st.button("Pobierz aktualne ceny"):
    with st.spinner('Trwa pobieranie danych...'):
        # Konfiguracja przeglądarki (Headless - bez okna)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Udajemy prawdziwego użytkownika
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Czekamy chwilę, aż JavaScript załaduje ceny
        time.sleep(3) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Próbujemy znaleźć ukryte dane wariacji (ceny dla stanów)
        try:
            import json
            variations_element = soup.find('form', {'class': 'variations_form'})
            data = variations_element['data-product_variations']
            variants = json.loads(data)
            
            st.success("Znaleziono ceny!")
            
            for v in variants:
                stan = v['attributes']['attribute_pa_stan-produktu']
                cena = v['display_price']
                
                # Wyświetlamy wynik w aplikacji
                col1, col2, col3 = st.columns(3)
                col1.write(f"**Stan:** {stan.replace('-', ' ').upper()}")
                col2.write(f"**Cena skupu:** {cena} zł")
                col3.write(f"**Twoja oferta (-15%):** {round(cena * 0.85)} zł")
        
        except Exception as e:
            st.error(f"Nie udało się wyciągnąć cen. Strona mogła zmienić format. Błąd: {e}")
        
        driver.quit()

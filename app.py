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

if st.button("Pobierz konkrety"):
    with st.spinner("Przeszukuję bazę danych produktu..."):
        driver = None
        try:
            driver = get_driver()
            driver.get(url)
            time.sleep(5)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            form = soup.find('form', class_='variations_form')
            
            if form:
                all_variants = json.loads(form.get('data-product_variations'))
                
                st.subheader("Filtry: Kupiony w 'inna' | System ratalny: 'Nie'")
                
                found_any = False
                for v in all_variants:
                    attr = v['attributes']
                    
                    # Pobieramy wartości filtrów (małe litery dla pewności porównania)
                    sklep = str(attr.get('attribute_pa_kupiony-w', '')).lower()
                    raty = str(attr.get('attribute_pa_system-ratalny', '')).lower()
                    stan_surowy = attr.get('attribute_pa_stan-produktu', 'Nieznany')
                    
                    # Sprawdzamy czy wariant pasuje (inna i nie-raty)
                    if sklep == 'inna' and raty == 'nie':
                        found_any = True
                        cena = float(v['display_price'])
                        
                        # Ładny podgląd wyników
                        with st.container():
                            c1, c2, c3 = st.columns([2, 1, 1])
                            nazwa_stanu = stan_surowy.replace('-', ' ').upper()
                            c1.success(f"📍 {nazwa_stanu}")
                            c2.metric("Skup Konkurencji", f"{cena} zł")
                            # Przykładowa marża: Twoja oferta to cena skupu - 10%
                            twoja_cena = round(cena * 0.90)
                            c3.metric("Twoja Oferta", f"{twoja_cena} zł", delta=f"-{int(cena-twoja_cena)} zł")
                            st.divider()
                
                if not found_any:
                    st.warning("Znalazłem produkt, ale żadna z opcji nie pasuje do filtrów 'Inna' + 'Nie'.")
                    with st.expander("Zobacz co widzi robot (debug)"):
                        st.write(all_variants[0]['attributes'] if all_variants else "Brak wariantów")
            else:
                st.error("Nie znaleziono danych technicznych na stronie. Upewnij się, że to link do produktu z opcjami wyboru.")
                
        except Exception as e:
            st.error(f"Wystąpił błąd: {e}")
        finally:
            if driver:
                driver.quit()

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import time
import pandas as pd

st.set_page_config(page_title="Multi-Skup PRO", layout="wide")

# CSS dla lepszego wyglądu na mobile (mniejsze czcionki)
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

st.title("📊 Porównywarka Skupów")

# Panel boczny na Twoje ustawienia
with st.sidebar:
    st.header("Ustawienia Marży")
    marza_procent = st.slider("Twoja marża (%)", 5, 30, 12)
    st.info("Aplikacja odejmie ten % od najwyższej ceny skupu.")

# Lista linków do sprawdzenia (możesz tu dodać więcej pol w przyszłości)
link_skup = st.text_input("Link SkupTelefonow.pl:", "https://skuptelefonow.pl/telefon/iphone-16-pro-256gb/")

if st.button("🚀 Porównaj Ceny"):
    with st.spinner("Pobieram dane z wielu źródeł..."):
        driver = None
        try:
            driver = get_driver()
            driver.get(link_skup)
            time.sleep(4)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            form = soup.find('form', class_='variations_form')
            
            if form:
                all_variants = json.loads(form.get('data-product_variations'))
                data_rows = []

                for v in all_variants:
                    attr = v['attributes']
                    
                    # FILTR: Pomijaj jeśli system ratalny to "tak"
                    raty = str(attr.get('attribute_pa_system-ratalny', '')).lower()
                    if raty == 'tak':
                        continue
                    
                    # Wyciągamy stan i sklep (kupiony w)
                    stan = str(attr.get('attribute_pa_wybierz-stan', attr.get('attribute_pa_stan-produktu', ''))).replace('-', ' ').upper()
                    sklep = str(attr.get('attribute_pa_kupiony-w', 'INNA')).upper()
                    cena = float(v['display_price'])
                    
                    # Liczymy Twoją cenę
                    twoja_oferta = round(cena * (1 - marza_procent/100))
                    
                    data_rows.append({
                        "STAN": stan,
                        "SKLEP / POCHODZENIE": sklep,
                        "CENA SKUPU (PLN)": int(cena),
                        "TWOJA OFERTA (PLN)": twoja_oferta
                    })

                # Tworzymy czytelną tabelę (DataFrame)
                df = pd.DataFrame(data_rows)
                
                # Sortowanie, żeby najlepsze stany były na górze
                if not df.empty:
                    st.success("✅ Dane pobrane i przefiltrowane")
                    
                    # Wyświetlanie tabeli zamiast wielkich kafelków
                    st.table(df)
                    
                    # Podsumowanie pod tabelą w formie kolumn
                    st.subheader("Szybki podgląd (Najwyższe ceny)")
                    cols = st.columns(len(df['STAN'].unique()[:3])) # Max 3 stany
                    for i, row in df.head(len(cols)).iterrows():
                        cols[i].metric(row['STAN'], f"{row['CENA SKUPU (PLN)']} zł", f"Twoja: {row['TWOJA OFERTA (PLN)']} zł")
                
            else:
                st.error("Błąd pobierania wariantów.")
                
        except Exception as e:
            st.error(f"Błąd: {e}")
        finally:
            if driver:
                driver.quit()

st.markdown("---")
st.caption("Tip: Używaj suwaka w menu bocznym, aby szybko zmieniać swoje ceny dla klienta.")

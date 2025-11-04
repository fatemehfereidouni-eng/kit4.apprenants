import time
import pandas as pd
import re
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Lancer le navigateur ---
driver = webdriver.Chrome()
driver.maximize_window()

url = "https://annuaire-entreprises.data.gouv.fr"
driver.get(url)

# --- Rechercher un mot-clé
mot_cle = "entreprise"
try:
    search_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "terme"))
    )
    search_box.send_keys(mot_cle)

    button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Rechercher']"))
    )
    button.click()

except TimeoutException:
    print("⚠️ Timeout : la page ou les éléments n’ont pas chargé.")
    driver.quit()
    exit()

# --- Fonction pour extraire le dirigeant ---
def get_leader(driver):
    try:
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )
        rows = table.find_elements(By.TAG_NAME, "tr")
        names = []
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) > 1:
                dirigeant = tds[1].text.strip()
                if dirigeant:
                    names.append(dirigeant)
        return " | ".join(names)
    except Exception:
        return ""

# --- Extraction principale ---
rows = []
page = 1
page_limit = 30  # 🔹 Limiter à 30 pages

while True:
    print(f"🔎 Lecture de la page {page}...")

    try:
        cards = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.results-list > div"))
        )
        print("✅ Nombre de cartes trouvées :", len(cards))
    except TimeoutException:
        print("⚠️ Aucun résultat trouvé sur cette page.")
        break

    # --- Prendre uniquement la première carte de la page ---
    if cards:
        card = cards[0]
        try:
            name_text = card.find_element(By.CSS_SELECTOR, "a").text.strip()
            link_el = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        except Exception:
            continue

        siren = ""
        if link_el:
            m = re.search(r"/entreprise/.*-(\d{9})$", link_el)
            if m:
                siren = m.group(1)

        try:
            address = " | ".join([li.text.strip() for li in card.find_elements(By.CSS_SELECTOR, "ul li")])
        except Exception:
            address = ""

        code_postal = ""
        ville = ""
        for ad in address.split("|"):
            m2 = re.search(r'(\d{5})\s+([A-Za-zÀ-ÖØ-öø-ÿ\s\'-]+)', ad)
            if m2:
                code_postal = m2.group(1).strip()
                ville = m2.group(2).strip()
                break

        # --- Valeurs initiales ---
        dirigeant_text = ""
        sector_text = ""
        capital_text = ""
        salaries_text = ""

        # --- Ouvrir la page détaillée ---
        driver.execute_script("window.open(arguments[0]);", link_el)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)

        # --- Récupérer les infos détaillées ---
        try:
            sector_text = driver.find_element(
                By.CSS_SELECTOR, "#entreprise > div > div:nth-child(2) > table > tbody > tr:nth-child(8) > td:nth-child(2) > button"
            ).text.strip()
        except:
            sector_text = ""

        try:
            capital_text = driver.find_element(
                By.XPATH, "//span[contains(text(), 'Capital')]/ancestor::tr/td[2]"
            ).text.strip()
        except:
            capital_text = ""

        try:
            salaries_text = driver.find_element(By.CSS_SELECTOR, "#entreprise > div > div:nth-child(2) > table > tbody > tr:nth-child(12) > td:nth-child(2)").text.strip()
        except:
            salaries_text = ""

        try:
            dirigeants_link = driver.find_element(
                By.XPATH, "//a[contains(@href, '/dirigeants/')]"
            ).get_attribute("href")
            driver.get(dirigeants_link)
            time.sleep(2)
            dirigeant_text = get_leader(driver)
        except:
            dirigeant_text = ""

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # --- Enregistrer les infos ---
        rows.append({
            "page": page,
            "nom": name_text,
            "siren": siren,
            "adresse": address,
            "code_postal": code_postal,
            "ville": ville,
            "dirigeant": dirigeant_text,
            "secteur": sector_text,
            "capital": capital_text,
            "salaries": salaries_text
        })

    # --- Aller à la page suivante ---
    if page >= page_limit:
        print("⛔ Limite de 30 pages atteinte.")
        break

    try:
        next_button = driver.find_element(
            By.CSS_SELECTOR,
            "body > div:nth-child(6) > main > div > div:nth-child(2) > div.layout-center > nav > ul > li:nth-child(9) > a"
        )
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(3)
        page += 1
    except NoSuchElementException:
        print("📘 Fin des pages.")
        break

# --- Sauvegarde CSV ---
output_file = "premiere_entreprise_par_page.csv"
with open(output_file, "w", newline='', encoding='utf-8') as csvfile:
    fieldnames = ["page", "nom", "siren", "adresse", "code_postal", "ville", "dirigeant", "secteur", "capital", "salaries"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in rows:
        writer.writerow(data)

print(f"💾 {len(rows)} sociétés enregistrées (1 par page, jusqu’à 30 pages).")
driver.quit()

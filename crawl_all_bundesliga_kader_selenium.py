import time
import json
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from scrape_bundesliga_team_urls_robust import lade_team_urls
from speichere_transfermarkt_html import speichere_html

MAX_RETRIES = 5
RETRY_DELAY_RANGE = (5, 15)  # Sekunden

def extrahiere_kader(driver, url):
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Versuch {attempt+1}: Lade {url}")
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".responsive-table"))
            )

            if "503 Service Unavailable" in driver.page_source:
                raise Exception("503-Fehlerseite erkannt")

            return driver.page_source  # Erfolg
        except Exception as e:
            print(f"⚠️ Fehler: {e}")
            if attempt < MAX_RETRIES - 1:
                sleep_time = random.randint(*RETRY_DELAY_RANGE)
                print(f"🔁 Warte {sleep_time} Sekunden und versuche es erneut...")
                time.sleep(sleep_time)
            else:
                print("❌ Maximale Wiederholungen erreicht. Überspringe.")
                return None

def crawl_alle_teams():
    teams = lade_team_urls()
    all_teams_data = {}

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    for teamname, url in teams.items():
        if "kader" not in url:
            print(f"⚠️ Überspringe {teamname} wegen ungültiger URL: {url}")
            continue

        print(f"🟦 Crawle {teamname} – {url}")
        html = extrahiere_kader(driver, url)
        if html:
            all_teams_data[teamname] = html
            speichere_html(teamname, html)
        else:
            print(f"❌ Konnte {teamname} nicht laden.")

    driver.quit()

    with open("teams_full.py", "w", encoding="utf-8") as f:
        f.write("Teams = ")
        json.dump(all_teams_data, f, indent=4, ensure_ascii=False)

    print("✅ Alle Teams gespeichert in teams_full.py")

if __name__ == "__main__":
    crawl_alle_teams()

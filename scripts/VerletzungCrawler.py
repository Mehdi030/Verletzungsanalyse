import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

class VerletzungCrawler:
    def __init__(self, url):
        self.url = url
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def scrape(self) -> pd.DataFrame:
        try:
            res = requests.get(self.url, headers=self.headers, timeout=20)
        except requests.exceptions.Timeout:
            print(f"⏳ Timeout bei URL: {self.url} – versuche erneut...")
            time.sleep(2)
            try:
                res = requests.get(self.url, headers=self.headers, timeout=20)
            except Exception as e:
                print(f"❌ Wieder fehlgeschlagen: {self.url}")
                print(f"🔴 Ausnahme: {e}")
                return pd.DataFrame()
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der URL: {self.url}")
            print(f"🔴 Ausnahme: {e}")
            return pd.DataFrame()

        if res.status_code != 200:
            print(f"❌ Fehler: Statuscode {res.status_code} für URL: {self.url}")
            return pd.DataFrame()

        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table", class_="items")

        if not table:
            return pd.DataFrame()

        rows = table.find_all("tr")[1:]
        daten = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                daten.append({
                    "Saison": cols[0].get_text(strip=True),
                    "Verletzung": cols[1].get_text(strip=True),
                    "von": cols[2].get_text(strip=True),
                    "bis": cols[3].get_text(strip=True),
                    "Spiele_verpasst": cols[4].get_text(strip=True)
                })

        return pd.DataFrame(daten)

import requests
from bs4 import BeautifulSoup
import pandas as pd

class VerletzungCrawler:
    def __init__(self, url):
        self.url = url
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def scrape(self):
        try:
            res = requests.get(self.url, headers=self.headers, timeout=10)
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der URL: {self.url}")
            print(f"🔴 Ausnahme: {e}")
            return pd.DataFrame()

        if res.status_code != 200:
            print(f"❌ Fehler: Statuscode {res.status_code} für URL: {self.url}")
            return pd.DataFrame()

        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table", {"class": "items"})

        if not table:
            print(f"⚠️ Keine Verletzungstabelle gefunden für URL: {self.url}")
            return pd.DataFrame()

        rows = table.find_all("tr")[1:]

        daten = []
        for row in rows:
            cols = row.find_all("td")
            if cols and len(cols) >= 5:
                daten.append({
                    "Saison": cols[0].text.strip(),
                    "Verletzung": cols[1].text.strip(),
                    "von": cols[2].text.strip(),
                    "bis": cols[3].text.strip(),
                    "Spiele_verpasst": cols[4].text.strip()
                })

        return pd.DataFrame(daten)

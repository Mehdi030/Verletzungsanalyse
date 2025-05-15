import requests
from bs4 import BeautifulSoup
import pandas as pd

class FBrefCrawler:
    def __init__(self, team_url: str):
        self.team_url = team_url
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def scrape(self) -> pd.DataFrame:
        res = requests.get(self.team_url, headers=self.headers)
        if res.status_code != 200:
            print(f"❌ Fehler beim Abrufen: {self.team_url}")
            return pd.DataFrame()

        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table", {"id": "appearances"})
        if not table:
            print(f"⚠️ Keine Einsatz-Tabelle gefunden bei {self.team_url}")
            return pd.DataFrame()

        rows = table.find_all("tr")
        daten = []
        for row in rows:
            if row.get("class") and "thead" in row["class"]:
                continue
            cols = row.find_all("td")
            if cols:
                status = cols[-1].text.strip().lower()
                if "injury" in status or "not in squad" in status:
                    daten.append({
                        "Spieler": cols[0].text.strip(),
                        "Status": status,
                        "Quelle": "FBref"
                    })

        return pd.DataFrame(daten)

import requests
from bs4 import BeautifulSoup
import pandas as pd

class VerletzungCrawler:
    def __init__(self, url):
        self.url = url
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def scrape(self):
        res = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table", {"class": "items"})
        rows = table.find_all("tr")[1:]

        daten = []
        for row in rows:
            cols = row.find_all("td")
            if cols:
                daten.append({
                    "Saison": cols[0].text.strip(),
                    "Verletzung": cols[1].text.strip(),
                    "von": cols[2].text.strip(),
                    "bis": cols[3].text.strip(),
                    "Spiele_verpasst": cols[4].text.strip()
                })
        return pd.DataFrame(daten)

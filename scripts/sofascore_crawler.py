import requests
import pandas as pd

class SofaScoreCrawler:
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.api_url = f"https://api.sofascore.com/api/v1/team/{team_id}/injuries"

    def scrape(self) -> pd.DataFrame:
        try:
            res = requests.get(self.api_url)
            if res.status_code != 200:
                print(f"❌ Fehler beim Abrufen: {self.api_url}")
                return pd.DataFrame()

            data = res.json()
            eintraege = data.get("injuries", [])
            daten = []
            for eintrag in eintraege:
                daten.append({
                    "Spieler": eintrag.get("player", {}).get("name"),
                    "Verletzung": eintrag.get("injury", {}).get("type"),
                    "von": eintrag.get("injury", {}).get("startDate", "unbekannt"),
                    "Team": eintrag.get("team", {}).get("name", "unbekannt"),
                    "Quelle": "SofaScore"
                })

            return pd.DataFrame(daten)
        except Exception as e:
            print(f"❌ Fehler beim Parsen der SofaScore-Daten: {e}")
            return pd.DataFrame()

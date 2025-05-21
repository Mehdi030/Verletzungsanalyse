# scripts/understat_loader.py
import requests
import pandas as pd

class UnderstatLoader:
    def __init__(self, player_name: str, season: int = 2023):
        self.player_name = player_name
        self.season = season

    def load(self) -> pd.DataFrame:
        url = f"https://understat.com/player/{self.player_name}"
        try:
            print(f"🔍 Versuche Daten von Understat für {self.player_name} zu laden... (Fake-Link zur Demo)")
            # Hier wäre normalerweise echter Code für Understat
            # Wir simulieren für das Projekt dummy-Daten
            data = [
                {"xG": 0.34, "xA": 0.12, "Saison": str(self.season)},
                {"xG": 0.22, "xA": 0.05, "Saison": str(self.season)}
            ]
            return pd.DataFrame(data)
        except Exception as e:
            print(f"❌ Fehler bei Understat für {self.player_name}: {e}")
            return pd.DataFrame()

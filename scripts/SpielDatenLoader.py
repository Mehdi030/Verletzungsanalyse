import pandas as pd

class SpielDatenLoader:
    def __init__(self, pfad: str):
        self.pfad = pfad

    def lade_spiele(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.pfad)
            df = df[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]]
            df.columns = ["Datum", "Heim", "Auswaerts", "Tore_Heim", "Tore_Auswaerts", "Ergebnis"]
            return df
        except Exception as e:
            print(f"❌ Fehler beim Laden der Spieldaten: {e}")
            return pd.DataFrame()

import pandas as pd

class Analyse:
    def __init__(self, spiele_df: pd.DataFrame, verletzungen_df: pd.DataFrame):
        self.spiele_df = spiele_df
        self.verletzungen_df = verletzungen_df

    def einfache_analyse(self):
        print("🔍 Vorschau auf Spieldaten:")
        print(self.spiele_df.head())

        print("\n🩹 Vorschau auf Verletzungsdaten:")
        print(self.verletzungen_df.head())

        print(f"\n🧮 Anzahl Spiele: {len(self.spiele_df)}")
        print(f"🧮 Anzahl Verletzungen: {len(self.verletzungen_df)}")

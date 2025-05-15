import pandas as pd

class VerletzungManager:
    def __init__(self, crawlers: list):
        self.crawlers = crawlers

    def lade_alle_verletzungen(self) -> pd.DataFrame:
        frames = []

        for crawler in self.crawlers:
            try:
                df = crawler.scrape()
                if not df.empty:
                    df["Quelle"] = crawler.__class__.__name__  # Herkunft markieren
                    frames.append(df)
            except Exception as e:
                print(f"❌ Fehler bei {crawler.__class__.__name__}: {e}")

        if not frames:
            print("⚠️ Keine Daten aus den Quellen erhalten.")
            return pd.DataFrame()

        # Zusammenführen und Duplikate vermeiden
        kombiniert = pd.concat(frames, ignore_index=True)

        # Optional: Duplikate filtern
        kombiniert = kombiniert.drop_duplicates(subset=["Spieler", "von", "bis", "Verletzung"])

        return kombiniert

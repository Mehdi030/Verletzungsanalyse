import pandas as pd
import unicodedata
from scripts.MultiSourceCrawler import MultiSourceCrawler

class TeamManager:
    def __init__(self, teamname: str, spieler_info: dict):
        self.teamname = teamname
        self.spieler_info = spieler_info

    def normalize_name_for_url(self, name: str) -> str:
        name = name.lower().replace(" ", "-")
        name = name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8")
        return name

    def crawl_team_verletzungen(self) -> pd.DataFrame:
        gesamt_df = pd.DataFrame()

        for name, info in self.spieler_info.items():
            print(f"🔍 Crawle {name}...")

            crawler = MultiSourceCrawler(
                name=name,
                transfermarkt_id=info.get("transfermarkt_id"),
                fbref_url=info.get("fbref_url")
            )

            # 🎯 NEU: beide Quellen als Tuple entgegennehmen
            df_tm, df_fbref = crawler.scrape_all()

            # 🎯 NEU: Kombiniere die beiden DataFrames
            df = pd.concat([df_tm, df_fbref], ignore_index=True)

            if df.empty:
                print(f"⚠️ Keine Daten für {name}")
                continue

            df["Spieler"] = name
            df["Team"] = self.teamname
            gesamt_df = pd.concat([gesamt_df, df], ignore_index=True)

        return gesamt_df

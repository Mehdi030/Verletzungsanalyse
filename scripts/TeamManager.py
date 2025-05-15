import pandas as pd
import unicodedata
from scripts.MultiSourceCrawler import MultiSourceCrawler

class TeamManager:
    def __init__(self, teamname: str, spieler_info: dict):
        """
        spieler_info: dict mit Format:
        {
            "Spielername": {
                "transfermarkt_id": ...,
                "fbref_url": ...,
                "sofascore_id": ...
            }
        }
        """
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

            tm_url = None
            if info.get("transfermarkt_id"):
                urlname = self.normalize_name_for_url(name)
                tm_url = f"https://www.transfermarkt.de/{urlname}/verletzungen/spieler/{info['transfermarkt_id']}"
                print(f"🔗 Transfermarkt URL: {tm_url}")

            crawler = MultiSourceCrawler(
                name=name,
                transfermarkt_url=tm_url,
                fbref_url=info.get("fbref_url"),
                sofascore_id=info.get("sofascore_id")
            )

            df = crawler.scrape_all()
            if df.empty:
                print(f"⚠️ Keine Daten für {name}")
                continue

            df["Spieler"] = name
            df["Team"] = self.teamname
            gesamt_df = pd.concat([gesamt_df, df], ignore_index=True)

        return gesamt_df

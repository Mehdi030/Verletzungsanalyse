import pandas as pd
from scripts.VerletzungCrawler import VerletzungCrawler

class TeamManager:
    def __init__(self, teamname: str, spieler_ids: dict):
        """
        spieler_ids: dict mit Format { "Spielername": spielerID }
        """
        self.teamname = teamname
        self.spieler_ids = spieler_ids

    def crawl_team_verletzungen(self) -> pd.DataFrame:
        gesamt_df = pd.DataFrame()

        for name, spieler_id in self.spieler_ids.items():
            url = f"https://www.transfermarkt.de/spieler/verletzungen/spieler/{spieler_id}"
            print(f"🔍 Crawle {name} ({spieler_id})...")
            crawler = VerletzungCrawler(url)
            df = crawler.scrape()

            if not df.empty:
                df["Spieler"] = name
                df["Team"] = self.teamname
                gesamt_df = pd.concat([gesamt_df, df], ignore_index=True)

        return gesamt_df

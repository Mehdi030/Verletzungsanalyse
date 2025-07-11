
import pandas as pd
from scripts.Teams import Teams
from scripts.TeamManager import TeamManager

class BundesligaVerletzungsCrawler:
    def __init__(self):
        self.teams = Teams

    def crawl_alle_verletzungen(self) -> pd.DataFrame:
        gesamt_df = pd.DataFrame()

        for teamname, spieler_info in self.teams.items():
            print(f"⚽️ Team: {teamname}")
            manager = TeamManager(teamname=teamname, spieler_info=spieler_info)
            team_df = manager.crawl_team_verletzungen()
            team_df["Team"] = teamname  # Team-Spalte hinzufügen
            gesamt_df = pd.concat([gesamt_df, team_df], ignore_index=True)

        return gesamt_df

    def speichere_als_csv(self, df: pd.DataFrame, pfad: str = "alle_verletzungen.csv"):
        df.to_csv(pfad, index=False)
        print(f"✅ CSV gespeichert unter: {pfad}")

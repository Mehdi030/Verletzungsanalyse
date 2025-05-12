import os
from scripts.TeamManager import TeamManager
from scripts.SpielDatenLoader import SpielDatenLoader
from scripts.Analyse import Analyse
from scripts.Daten import speichere_csv, lade_csv, VERLETZUNGEN_CSV, SPIELE_CSV
from scripts.Teams import Teams




def main():
    # Ordner anlegen
    os.makedirs("daten", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Team-Auswahl
    print("\n🔎 Verfügbare Teams:")
    for idx, teamname in enumerate(Teams.keys()):
        print(f"{idx + 1}. {teamname}")

    try:
        auswahl = int(input("Wähle dein Team (Nummer): "))
        teamname = list(Teams.keys())[auswahl - 1]
    except (ValueError, IndexError):
        print("❌ Ungültige Auswahl. Abbruch.")
        return

    print(f"\n➡️ Team gewählt: {teamname}")
    spieler_ids = Teams[teamname]

    # Verletzungsdaten crawlen
    manager = TeamManager(teamname, spieler_ids)
    verletzungen_df = manager.crawl_team_verletzungen()
    speichere_csv(verletzungen_df, VERLETZUNGEN_CSV)

    # Spieldaten laden
    loader = SpielDatenLoader(SPIELE_CSV)
    spiele_df = loader.lade_spiele()

    # Analyse starten
    analyse = Analyse(spiele_df, verletzungen_df)
    analyse.einfache_analyse()

if __name__ == "__main__":
    main()

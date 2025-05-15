import os
import pandas as pd
import matplotlib.pyplot as plt

from scripts.TeamManager import TeamManager
from scripts.SpielDatenLoader import SpielDatenLoader
from scripts.Analyse import Analyse
from scripts.Daten import speichere_csv, SPIELE_CSV
from scripts.Teams import Teams

from scripts.VerletzungCrawler import VerletzungCrawler
from scripts.VerletzungManager import VerletzungManager

def main():
    os.makedirs("daten", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # TEAM 1 auswählen
    print("\n🔎 Verfügbare Teams:")
    for idx, teamname in enumerate(Teams.keys()):
        print(f"{idx + 1}. {teamname}")

    try:
        auswahl = int(input("Wähle dein Team (Nummer): "))
        teamname_1 = list(Teams.keys())[auswahl - 1]
    except (ValueError, IndexError):
        print("❌ Ungültige Auswahl. Abbruch.")
        return

    print(f"\n➡️ Team gewählt: {teamname_1}")
    spieler_ids_1 = Teams[teamname_1]
    manager1 = TeamManager(teamname_1, spieler_ids_1)
    df1 = manager1.crawl_team_verletzungen()
    df1["Team"] = teamname_1
    speichere_csv(df1, os.path.join("daten", f"verletzungen_{teamname_1.lower().replace(' ', '_')}.csv"))

    # VERGLEICHSMODUS
    vergleich = input("🔁 Möchtest du dieses Team mit einem weiteren vergleichen? (j/n): ").strip().lower()

    if vergleich == "j":
        print("\n🔎 Wähle Vergleichsteam:")
        andere_teams = [t for t in Teams.keys() if t != teamname_1]
        for idx, teamname in enumerate(andere_teams):
            print(f"{idx + 1}. {teamname}")

        try:
            auswahl_2 = int(input("Wähle zweites Team (Nummer): "))
            teamname_2 = andere_teams[auswahl_2 - 1]
        except (ValueError, IndexError):
            print("❌ Ungültige Auswahl. Abbruch.")
            return

        print(f"\n➡️ Vergleich: {teamname_1} vs. {teamname_2}")
        spieler_ids_2 = Teams[teamname_2]
        manager2 = TeamManager(teamname_2, spieler_ids_2)
        df2 = manager2.crawl_team_verletzungen()
        df2["Team"] = teamname_2

        combined_df = pd.concat([df1, df2], ignore_index=True)
        combined_df = combined_df[combined_df["Saison"].notna()]
        combined_df["Saison"] = combined_df["Saison"].astype(str).str.strip()
        saisonen = combined_df.groupby(["Saison", "Team"]).size().unstack(fill_value=0)

        if not saisonen.empty:
            ax = saisonen.plot(kind="bar", figsize=(12, 6), edgecolor="black")
            ax.set_title("Vergleich: Verletzungen pro Saison")
            ax.set_xlabel("Saison")
            ax.set_ylabel("Anzahl Verletzungen")
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', linestyle='--', alpha=0.6)
            ax.legend(title="Team")

            plt.tight_layout()
            plt.savefig("output/verletzungsvergleich.png")
            print("📸 Vergleichsdiagramm gespeichert: output/verletzungsvergleich.png")
            plt.show()
        else:
            print("⚠️ Kein Vergleich möglich, da keine gültigen Saisondaten vorhanden sind.")
        return

    # EINZELTEAM ANALYSE
    loader = SpielDatenLoader(SPIELE_CSV)
    spiele_df = loader.lade_spiele()
    analyse = Analyse(spiele_df, df1)
    analyse.einfache_analyse()

    # Nur Transfermarkt als Quelle für zusätzlichen Crawl
    tm = VerletzungCrawler("https://www.transfermarkt.de/thomas-mueller/verletzungen/spieler/58358")
    manager = VerletzungManager([tm])
    df = manager.lade_alle_verletzungen()

    if not df.empty:
        speichere_csv(df, "daten/alle_quellen_verletzungen.csv")
        print("\n📥 Daten aus mehreren Quellen (nur Transfermarkt):")
        print(df.head())

if __name__ == "__main__":
    main()

import os
import pandas as pd
import matplotlib.pyplot as plt

from scripts.TeamManager import TeamManager
from scripts.SpielDatenLoader import SpielDatenLoader
from scripts.Analyse import Analyse
from scripts.Daten import speichere_csv, SPIELE_CSV
from scripts.Teams import Teams
from scripts.AnalyseErweiterung import erweitere_mit_understat
from scripts.BundesligaVerletzungsCrawler import BundesligaVerletzungsCrawler

# Konfiguration: wie viele Jahre rückwirkend
ANALYSE_JAHRE = 5

def filter_letzte_saisons(df: pd.DataFrame, jahre=5) -> pd.DataFrame:
    aktuelle_saison = pd.Timestamp.now().year

    def extrahiere_jahr(s):
        if "/" in s:
            teil = s.split("/")[0]
            return int("20" + teil) if len(teil) == 2 else int(teil)
        try:
            return int(s[:4])
        except:
            return None

    df["Jahr_start"] = df["Saison"].apply(extrahiere_jahr)
    df = df[df["Jahr_start"].notna()]
    df = df[df["Jahr_start"] >= aktuelle_saison - jahre]
    return df.drop(columns="Jahr_start")

def vorbereiten(df):
    df = df[df["Saison"].notna()]
    df["Saison"] = df["Saison"].astype(str).str.strip()
    return filter_letzte_saisons(df, jahre=ANALYSE_JAHRE)

def main():
    os.makedirs("daten", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    print("📊 Was möchtest du tun?")
    print("1. Einzelnes Team analysieren")
    print("2. Alle Bundesliga-Teams automatisch crawlen")
    wahl = input("➡️ Auswahl (1/2): ").strip()

    if wahl == "2":
        crawler = BundesligaVerletzungsCrawler()
        df = crawler.crawl_alle_verletzungen()
        df = vorbereiten(df)
        crawler.speichere_als_csv(df, os.path.join("daten", "alle_verletzungen.csv"))
        print("✅ Fertig. Du findest alle Verletzungsdaten unter: daten/alle_verletzungen.csv")
        return

    # Einzelteam-Analyse wie bisher
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
    spieler_info_1 = Teams[teamname_1]
    manager1 = TeamManager(teamname_1, spieler_info_1)
    df1 = manager1.crawl_team_verletzungen()
    df1 = vorbereiten(df1)

    if df1.empty:
        print(f"⚠️ Keine Verletzungsdaten für {teamname_1} in den letzten {ANALYSE_JAHRE} Jahren.")
        return

    df1["Team"] = teamname_1
    dateiname = f"verletzungen_{teamname_1.lower().replace(' ', '_')}.csv"
    speichere_csv(df1, os.path.join("daten", dateiname))
    print(f"📎 Gespeichert: daten/{dateiname}")

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
        spieler_info_2 = Teams[teamname_2]
        manager2 = TeamManager(teamname_2, spieler_info_2)
        df2 = manager2.crawl_team_verletzungen()
        df2 = vorbereiten(df2)

        if df2.empty:
            print(f"⚠️ Keine Verletzungsdaten für {teamname_2} in den letzten {ANALYSE_JAHRE} Jahren.")
            return

        df2["Team"] = teamname_2
        combined_df = pd.concat([df1, df2], ignore_index=True)

        grouped = combined_df.groupby(["Saison", "Team"]).size().unstack(fill_value=0)
        cleaned = grouped[(grouped != 0).any(axis=1)]

        if not cleaned.empty:
            ax = cleaned.plot(kind="bar", figsize=(12, 6), edgecolor="black")
            ax.set_title("Vergleich: Verletzungen pro Saison (letzte 5 Jahre)")
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

    understat_df = erweitere_mit_understat(df1)
    if not understat_df.empty:
        fname = f"understat_erweitert_{teamname_1.lower().replace(' ', '_')}.csv"
        understat_df.to_csv(os.path.join("daten", fname), index=False)
        print(f"📊 Understat-Daten gespeichert: daten/{fname}")
    else:
        print("⚠️ Keine Understat-Daten gefunden.")

    loader = SpielDatenLoader(SPIELE_CSV)
    spiele_df = loader.lade_spiele()
    analyse = Analyse(spiele_df, df1)
    analyse.einfache_analyse()

if __name__ == "__main__":
    main()

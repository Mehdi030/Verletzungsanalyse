import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime

class Analyse:
    def __init__(self, spiele_df: pd.DataFrame, verletzungen_df: pd.DataFrame):
        self.spiele_df = spiele_df
        self.verletzungen_df = verletzungen_df

    def einfache_analyse(self):

        self.spiele_df["Ergebnis"] = self.spiele_df["Ergebnis"].map({
            "H": "S",  # Sieg
            "A": "N",  # Niederlage
            "D": "U"  # Unentschieden
        })

        print("\n📊 --- SPIELDATEN ---")
        print(self.spiele_df.head())

        print("\n🩹 --- VERLETZUNGSDATEN ---")
        print(self.verletzungen_df.head())

        print(f"\n📈 Gesamtanzahl Spiele: {len(self.spiele_df)}")
        print(f"🧑‍⚕️ Gesamtanzahl Verletzungen: {len(self.verletzungen_df)}")

        print("\n📊 --- ANALYSEN ---")
        self.zeige_verletzungen_pro_saison()
        self.zeige_verletzungen_pro_team()
        self.verletzte_spieler_pro_spiel()

        print("\n🆕 Neue Spalte 'Verletzte_Spieler' (Vorschau):")
        print(self.spiele_df[["Datum", "Heim", "Auswaerts", "Verletzte_Spieler"]].head())

    def zeige_verletzungen_pro_saison(self):
        if self.verletzungen_df.empty or "Saison" not in self.verletzungen_df.columns:
            print("⚠️ Keine gültigen Verletzungsdaten zur Visualisierung.")
            return

        saisonen = self.verletzungen_df["Saison"].value_counts().sort_index()

        plt.figure(figsize=(10, 5))
        saisonen.plot(kind="bar", color="skyblue", edgecolor="black")
        plt.title("Verletzungen pro Saison")
        plt.xlabel("Saison")
        plt.ylabel("Anzahl Verletzungen")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.savefig("output/verletzungen_pro_saison.png")
        print("📸 Diagramm gespeichert: output/verletzungen_pro_saison.png")
        plt.show()

    def zeige_verletzungen_pro_team(self):
        if self.verletzungen_df.empty or "Team" not in self.verletzungen_df.columns:
            print("⚠️ Keine Team-Verletzungsdaten zur Visualisierung.")
            return

        df = self.verletzungen_df.copy()
        gruppiert = df.groupby(["Team", "Saison"]).size().unstack(fill_value=0)

        gruppiert.T.plot(kind="bar", figsize=(10, 6), edgecolor="black")
        plt.title("Verletzungen pro Team und Saison")
        plt.xlabel("Saison")
        plt.ylabel("Anzahl Verletzungen")
        plt.xticks(rotation=45)
        plt.legend(title="Team")
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.savefig("output/verletzungen_teams_saisons.png")
        print("📸 Diagramm gespeichert: output/verletzungen_teams_saisons.png")
        plt.show()

    def verletzte_spieler_pro_spiel(self):
        if self.spiele_df.empty or self.verletzungen_df.empty:
            print("⚠️ Nicht genug Daten für Spiel-Verletzungs-Abgleich.")
            return

        verletzungs_map = {}
        for _, row in self.verletzungen_df.iterrows():
            spieler = row["Spieler"]
            try:
                start = datetime.strptime(row["von"], "%d.%m.%Y")
                ende = datetime.strptime(row["bis"], "%d.%m.%Y")
            except:
                continue

            if spieler not in verletzungs_map:
                verletzungs_map[spieler] = []
            verletzungs_map[spieler].append((start, ende))

        def zaehle_verletzte(datum_str):
            try:
                spiel_datum = datetime.strptime(datum_str, "%d/%m/%Y")
            except:
                return 0

            count = 0
            for spieler, zeiten in verletzungs_map.items():
                for start, ende in zeiten:
                    if start <= spiel_datum <= ende:
                        count += 1
                        break
            return count

        self.spiele_df["Verletzte_Spieler"] = self.spiele_df["Datum"].apply(zaehle_verletzte)
        print("\n📊 Neue Spalte 'Verletzte_Spieler' hinzugefügt.")
        print(self.spiele_df[["Datum", "Heim", "Auswaerts", "Verletzte_Spieler"]].head())

    # Optional: alte Auswertung nur für Thomas Müller
    def auswertung_mueller_ausfall_vs_ergebnis(self):
        zeitraeume = []
        for _, row in self.verletzungen_df.iterrows():
            try:
                start = datetime.strptime(row["von"], "%d.%m.%Y")
                ende = datetime.strptime(row["bis"], "%d.%m.%Y")
                zeitraeume.append((start, ende))
            except:
                continue

        def war_verletzt(datum_str):
            try:
                datum = datetime.strptime(datum_str, "%d/%m/%Y")
            except:
                return False
            return any(start <= datum <= ende for start, ende in zeitraeume)

        self.spiele_df["Mueller_verletzt"] = self.spiele_df["Datum"].apply(war_verletzt)
        ergebnisse = self.spiele_df.groupby("Mueller_verletzt")["Ergebnis"].value_counts()
        print("\n📈 Ergebnisverteilung mit/ohne Müller-Verletzung:")
        print(ergebnisse)

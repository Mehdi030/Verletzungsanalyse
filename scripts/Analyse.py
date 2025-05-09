import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

class Analyse:
    def __init__(self, spiele_df: pd.DataFrame, verletzungen_df: pd.DataFrame):
        self.spiele_df = spiele_df
        self.verletzungen_df = verletzungen_df

    def einfache_analyse(self):
        if self.spiele_df.empty:
            print("⚠️ Keine Spieldaten vorhanden.")
        else:
            print("🔍 Vorschau Spieldaten:")
            print(self.spiele_df.head())

        if self.verletzungen_df.empty:
            print("⚠️ Keine Verletzungsdaten vorhanden.")
        else:
            print("\n🩹 Vorschau Verletzungsdaten:")
            print(self.verletzungen_df.head())

        print(f"\n📊 Anzahl Spiele: {len(self.spiele_df)}")
        print(f"📊 Anzahl Verletzungen: {len(self.verletzungen_df)}")

        # Zusätzliche Analysen
        self.zeige_verletzungen_pro_saison()
        self.auswertung_mueller_ausfall_vs_ergebnis()

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

    def auswertung_mueller_ausfall_vs_ergebnis(self):
        if self.spiele_df.empty or self.verletzungen_df.empty:
            print("⚠️ Nicht genug Daten für Auswertung.")
            return

        # Verletzungszeiträume extrahieren
        zeitraeume = []
        for _, row in self.verletzungen_df.iterrows():
            try:
                start = datetime.strptime(row["von"], "%d.%m.%Y")
                ende = datetime.strptime(row["bis"], "%d.%m.%Y")
                zeitraeume.append((start, ende))
            except:
                continue

        # Prüfen, ob Müller zum Spielzeitpunkt verletzt war
        def war_verletzt(datum_str):
            try:
                datum = datetime.strptime(datum_str, "%d/%m/%Y")
            except:
                return False
            return any(start <= datum <= ende for start, ende in zeitraeume)

        self.spiele_df["Mueller_verletzt"] = self.spiele_df["Datum"].apply(war_verletzt)

        # Ergebnisanalyse
        ergebnisse = self.spiele_df.groupby("Mueller_verletzt")["Ergebnis"].value_counts()

        print("\n📈 Ergebnisverteilung mit/ohne Müller-Verletzung:")
        print(ergebnisse)

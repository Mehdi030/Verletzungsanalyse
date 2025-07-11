
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def lade_daten(pfad="daten/alle_verletzungen.csv"):
    if not os.path.exists(pfad):
        print(f"❌ Datei nicht gefunden: {pfad}")
        return None
    return pd.read_csv(pfad)

def vorbereiten(df):
    df = df[df["Saison"].notna()]
    df["Saison"] = df["Saison"].astype(str).str.strip()
    return df

def plot_verletzungen_pro_team_saison(df):
    grouped = df.groupby(["Saison", "Team"]).size().unstack(fill_value=0)
    grouped.plot(kind="bar", figsize=(14, 6), edgecolor="black")
    plt.title("Verletzungen pro Team und Saison")
    plt.xlabel("Saison")
    plt.ylabel("Anzahl Verletzungen")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    os.makedirs("output", exist_ok=True)
    plt.savefig("output/verletzungen_pro_team_saison.png")
    print("📊 Gespeichert: output/verletzungen_pro_team_saison.png")
    plt.show()

def plot_top_verletzte_spieler(df, top_n=10):
    if "Spieler" in df.columns:
        grouped = df["Spieler"].value_counts().head(top_n)
    else:
        grouped = df["Verletzung"].groupby(df["Team"]).count().nlargest(top_n)
    grouped.plot(kind="bar", figsize=(10, 5), color="red", edgecolor="black")
    plt.title(f"Top {top_n} Verletzte Spieler (nach Einträgen)")
    plt.xlabel("Spieler")
    plt.ylabel("Verletzungseinträge")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/top_verletzte_spieler.png")
    print("📊 Gespeichert: output/top_verletzte_spieler.png")
    plt.show()

def plot_zeitverlauf(df):
    df["von"] = pd.to_datetime(df["von"], errors="coerce")
    df = df.dropna(subset=["von"])
    df["Monat"] = df["von"].dt.to_period("M")
    verlauf = df.groupby("Monat").size()
    verlauf.plot(kind="line", figsize=(12, 4), marker="o")
    plt.title("Zeitverlauf der Verletzungen")
    plt.xlabel("Monat")
    plt.ylabel("Anzahl Verletzungen")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("output/zeitverlauf_verletzungen.png")
    print("📊 Gespeichert: output/zeitverlauf_verletzungen.png")
    plt.show()

def main():
    df = lade_daten()
    if df is None:
        return
    df = vorbereiten(df)
    plot_verletzungen_pro_team_saison(df)
    plot_top_verletzte_spieler(df)
    plot_zeitverlauf(df)

if __name__ == "__main__":
    main()

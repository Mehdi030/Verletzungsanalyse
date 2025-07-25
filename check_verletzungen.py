import pandas as pd

# Pfad zur CSV-Datei (je nach Struktur ggf. anpassen)
csv_path = "src/data/verletzungen_gesamt.csv"

# Lade CSV
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"❌ Datei nicht gefunden: {csv_path}")
    exit()

# Übersicht
print(f"📊 Gesamtanzahl Einträge: {len(df)}")
print(f"🧍‍♂️ Einzigartige Spieler: {df['Spieler'].nunique()}")
print(f"🏥 Teams mit Verletzungen:\n{df['Team'].value_counts()}")

# Leere Werte prüfen
print("\n🔎 Anzahl leerer Werte pro Spalte:")
print(df.isna().sum())

# Beispielausgabe
print("\n👀 Beispiel-Einträge:")
print(df.head(5))


import os
import pandas as pd
from datetime import datetime

# Basisverzeichnis für Daten
DATEN_VERZEICHNIS = "daten"

# Pfade definieren
SPIELE_CSV = os.path.join(DATEN_VERZEICHNIS, "D1.csv")
VERLETZUNGEN_CSV = os.path.join(DATEN_VERZEICHNIS, "verletzungen_muller.csv")


def lade_csv(pfad):
    """Lädt eine CSV-Datei, gibt leeres DataFrame zurück, wenn sie fehlt."""
    try:
        return pd.read_csv(pfad)
    except FileNotFoundError:
        print(f"❌ Datei nicht gefunden: {pfad}")
        return pd.DataFrame()


def speichere_csv(df, pfad):
    """Speichert ein DataFrame als CSV."""
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    df.to_csv(pfad, index=False)
    print(f"💾 Gespeichert: {pfad}")


def konvertiere_datum(text: str) -> datetime:
    """Konvertiert Datum im Format TT.MM.JJJJ zu datetime."""
    try:
        return datetime.strptime(text, "%d.%m.%Y")
    except Exception as e:
        print(f"⚠️ Fehler beim Konvertieren von '{text}': {e}")
        return None

# Projekt: Verletzungsanalyse im Fußball

## Ziel
Untersuchung, ob und wie stark verletzungsbedingte Ausfälle Einfluss auf Spielergebnisse in der Fußball-Bundesliga haben.

## Datenquellen
- Verletzungsdaten: transfermarkt.de (per Web Crawling)
- Spielergebnisse: football-data.co.uk (CSV D1.csv)

## Funktionen
- Web Scraping mit BeautifulSoup
- CSV-Handling und zentrale Dateipfade
- Analysemodul mit Datenvorschau
- Erweiterbar für Visualisierung und Statistik

## Projektstruktur
- main.py: Ablaufsteuerung
- scripts/: Enthält alle Module (Crawler, Analyse, etc.)
- daten/: CSV-Dateien
- output/: spätere Ausgaben wie Diagramme

## Ausführung
```bash
python main.py

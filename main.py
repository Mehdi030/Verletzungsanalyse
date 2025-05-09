import os
from scripts import VerletzungCrawler, SpielDatenLoader, Analyse
from scripts.daten import speichere_csv, VERLETZUNGEN_CSV, SPIELE_CSV

def main():
    # Ordner sicherstellen
    os.makedirs("daten", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # 1. Verletzungsdaten crawlen
    url = "https://www.transfermarkt.de/thomas-muller/verletzungen/spieler/58358"
    crawler = VerletzungCrawler(url)
    verletzungen_df = crawler.scrape()
    speichere_csv(verletzungen_df, VERLETZUNGEN_CSV)

    # 2. Spieldaten laden
    loader = SpielDatenLoader(SPIELE_CSV)
    spiele_df = loader.lade_spiele()

    # 3. Analyse starten
    analyse = Analyse(spiele_df, verletzungen_df)
    analyse.einfache_analyse()

if __name__ == "__main__":
    main()

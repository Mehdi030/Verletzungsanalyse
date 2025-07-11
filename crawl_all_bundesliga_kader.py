
import requests
from bs4 import BeautifulSoup
import time
import json
import os

def extrahiere_kader(vorname_der_mannschaft, vereins_id):
    url = f"https://www.transfermarkt.de/{vorname_der_mannschaft}/kader/verein/{vereins_id}/saison_id/2023"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print(f"❌ Fehler beim Abrufen von {url}")
        return {}

    soup = BeautifulSoup(res.text, "html.parser")
    spieler_tabelle = soup.find("table", class_="items")
    if not spieler_tabelle:
        print("⚠️ Keine Tabelle gefunden")
        return {}

    spieler_dict = {}
    rows = spieler_tabelle.find_all("tr", class_=["odd", "even"])

    for row in rows:
        try:
            name_tag = row.find("td", class_="hauptlink").find("a")
            name = name_tag.text.strip()
            link = name_tag["href"]
            transfermarkt_id = int(link.split("/")[4])
            position = row.find_all("td")[4].text.strip()
            spieler_dict[name] = {
                "transfermarkt_id": transfermarkt_id,
                "position": position
            }
        except Exception:
            continue

    return spieler_dict

# Alle Bundesliga-Teams 2023/24 mit Transfermarkt-URL-Namen + IDs
bundesliga_teams = {
    "FC Bayern": ("fc-bayern-munchen", 27),
    "Borussia Dortmund": ("borussia-dortmund", 16),
    "RB Leipzig": ("rb-leipzig", 23826),
    "Bayer Leverkusen": ("bayer-04-leverkusen", 15),
    "VfB Stuttgart": ("vfb-stuttgart", 79),
    "Eintracht Frankfurt": ("eintracht-frankfurt", 24),
    "SC Freiburg": ("sc-freiburg", 60),
    "1. FC Union Berlin": ("1-fc-union-berlin", 89),
    "TSG Hoffenheim": ("1899-hoffenheim", 533),
    "Werder Bremen": ("sv-werder-bremen", 86),
    "VfL Wolfsburg": ("vfl-wolfsburg", 82),
    "1. FSV Mainz 05": ("1-fsv-mainz-05", 39),
    "Borussia Mönchengladbach": ("borussia-moenchengladbach", 18),
    "FC Augsburg": ("fc-augsburg", 167),
    "1. FC Heidenheim": ("1-fc-heidenheim", 3709),
    "Darmstadt 98": ("sv-darmstadt-98", 105),
    "VfL Bochum": ("vfl-bochum", 80),
    "1. FC Köln": ("1-fc-koln", 3)
}

def crawl_alle_teams():
    all_teams_data = {}
    for teamname, (url_name, tm_id) in bundesliga_teams.items():
        print(f"🔄 Crawle {teamname}...")
        daten = extrahiere_kader(url_name, tm_id)
        if daten:
            all_teams_data[teamname] = daten
        time.sleep(1)  # freundlich sein ;)
    return all_teams_data

if __name__ == "__main__":
    ergebnis = crawl_alle_teams()
    output_path = "teams_full.py"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Teams = ")
        json.dump(ergebnis, f, indent=4, ensure_ascii=False)
    print(f"✅ Alle Teams gespeichert in {output_path}")

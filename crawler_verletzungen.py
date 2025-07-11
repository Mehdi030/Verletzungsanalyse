import requests
from bs4 import BeautifulSoup
import json

def crawl_verletzungen_fuer_team(team_url, team_name):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(team_url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Fehler bei {team_name}: {response.status_code}")
        return {team_name: []}

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="items")
    if not table:
        print(f"❌ Tabelle nicht gefunden für {team_name}")
        return {team_name: []}

    verletzungen = []
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) < 9:
            continue

        img_tag = cols[0].find("img")
        spieler = img_tag["alt"] if img_tag else cols[0].get_text(strip=True)

        verletzungen.append({
            "spieler": spieler,
            "alter": cols[4].get_text(strip=True),
            "grund": cols[5].get_text(strip=True),
            "seit": cols[6].get_text(strip=True),
            "bis_voraussichtlich": cols[7].get_text(strip=True),
            "verpasste_spiele": cols[8].get_text(strip=True)
        })

    return {team_name: verletzungen}


if __name__ == "__main__":
    # 👇 Beispielhafte Vereine & URLs aus deiner Datei (verein: URL)
    teams = {
        "FC Bayern München": "https://www.transfermarkt.de/fc-bayern-munchen/sperrenundverletzungen/verein/27",
        "Borussia Dortmund": "https://www.transfermarkt.de/borussia-dortmund/sperrenundverletzungen/verein/16",
        "RB Leipzig": "https://www.transfermarkt.de/rb-leipzig/sperrenundverletzungen/verein/23826/plus/1",
        "Bayer Leverkusen": "https://www.transfermarkt.de/bayer-04-leverkusen/sperrenundverletzungen/verein/15/plus/1",
        "VfB Stuttgart": "https://www.transfermarkt.de/vfb-stuttgart/sperrenundverletzungen/verein/79/plus/1",
    "Eintracht Frankfurt": "https://www.transfermarkt.de/eintracht-frankfurt/sperrenundverletzungen/verein/24/plus/1",
        
    "SC Freiburg": "https://www.transfermarkt.de/sc-freiburg/sperrenundverletzungen/verein/60/plus/1",
    "1. FC Union Berlin": "https://www.transfermarkt.de/1-fc-union-berlin/sperrenundverletzungen/verein/89/plus/1",
    "TSG Hoffenheim": "https://www.transfermarkt.de/tsg-1899-hoffenheim/sperrenundverletzungen/verein/533/plus/1",
        
    "Werder Bremen": "https://www.transfermarkt.de/sv-werder-bremen/sperrenundverletzungen/verein/86/plus/1",
        
    "VfL Wolfsburg": "https://www.transfermarkt.de/vfl-wolfsburg/sperrenundverletzungen/verein/82/plus/1",
        
    "1. FSV Mainz 05": "https://www.transfermarkt.de/1-fsv-mainz-05/sperrenundverletzungen/verein/39/plus/1",
        
    "Borussia Mönchengladbach": "https://www.transfermarkt.de/borussia-monchengladbach/sperrenundverletzungen/verein/18/plus/1",
        
    "FC Augsburg": "https://www.transfermarkt.de/fc-augsburg/sperrenundverletzungen/verein/167/plus/1",
        
    "1. FC Heidenheim": "https://www.transfermarkt.de/1-fc-heidenheim-1846/sperrenundverletzungen/verein/2036/plus/1",
        
    "Hamburger SV": "https://www.transfermarkt.de/hamburger-sv/sperrenundverletzungen/verein/41/plus/1",
        
    "FC St. Pauli": "https://www.transfermarkt.de/fc-st-pauli/sperrenundverletzungen/verein/35/plus/1",
        
    "1. FC Köln": "https://www.transfermarkt.de/1-fc-koln/sperrenundverletzungen/verein/3/plus/1"
    }

    gesamt_daten = {}
    for team_name, team_url in teams.items():
        print(f"🔄 Verarbeite: {team_name}")
        daten = crawl_verletzungen_fuer_team(team_url, team_name)
        gesamt_daten.update(daten)

    with open("verletzungen_gesamt.json", "w", encoding="utf-8") as f:
        json.dump(gesamt_daten, f, indent=2, ensure_ascii=False)

    print("✅ Alles gespeichert in: verletzungen_gesamt.json")

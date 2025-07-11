import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.transfermarkt.de"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Liste der Vereine und IDs für die Bundesliga-Saison 2023/2024
teams = {
    "FC Bayern München": 27,
    "Borussia Dortmund": 16,
    "RB Leipzig": 23826,
    "Bayer Leverkusen": 15,
    "VfB Stuttgart": 79,
    "Eintracht Frankfurt": 24,
    "SC Freiburg": 60,
    "1. FC Union Berlin": 89,
    "TSG Hoffenheim": 533,
    "Werder Bremen": 86,
    "VfL Wolfsburg": 82,
    "1. FSV Mainz 05": 39,
    "Borussia Mönchengladbach": 18,
    "FC Augsburg": 167,
    "1. FC Heidenheim": 3709,
    "SV Darmstadt 98": 105,
    "VfL Bochum": 80,
    "1. FC Köln": 3
}

saisons = ["2021", "2022", "2023", "2024"]

def crawl_ausfallzeiten(team_id, saison):
    url = f"{BASE_URL}/xxx/ausfallzeiten/verein/{team_id}?reldata=L1%26{saison}"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", class_="items")
    result = []

    if not table:
        return result

    rows = table.find_all("tr", class_=["odd", "even"])
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 6:
            result.append({
                "name": cols[0].text.strip(),
                "from": cols[2].text.strip(),
                "to": cols[3].text.strip(),
                "days_missed": cols[4].text.strip(),
                "games_missed": cols[5].text.strip(),
                "saison": f"{saison}/2024" if saison == "2023" else f"{saison}/{int(saison)+1}"
            })
    return result

def crawl_sperrenundverletzungen(team_id):
    url = f"{BASE_URL}/xxx/sperrenundverletzungen/verein/{team_id}/plus/1"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", class_="items")
    result = {}

    if not table:
        return result

    rows = table.find_all("tr", class_=["odd", "even"])
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            name = cols[0].text.strip()
            reason = cols[1].text.strip()
            result[name] = reason
    return result

def main():
    all_data = {}
    for team, team_id in teams.items():
        print(f"🔄 Verarbeite {team}...")
        team_data = []
        art_dict = crawl_sperrenundverletzungen(team_id)

        for saison in saisons:
            ausfälle = crawl_ausfallzeiten(team_id, saison)
            for eintrag in ausfälle:
                name = eintrag["name"]
                eintrag["injury"] = art_dict.get(name, None)
                team_data.append(eintrag)

            time.sleep(1)

        all_data[team] = team_data
        time.sleep(1)

    with open("daten/vereins_verletzungen.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("✅ Fertig! Daten gespeichert in daten/vereins_verletzungen.json")

if __name__ == "__main__":
    main()
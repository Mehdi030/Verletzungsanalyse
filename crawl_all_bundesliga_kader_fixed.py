import requests
from bs4 import BeautifulSoup
import time
import json

def extrahiere_kader(team_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(team_url, headers=headers)

    if res.status_code != 200:
        print(f"❌ Fehler beim Abrufen von {team_url}")
        return {}

    soup = BeautifulSoup(res.text, "html.parser")
    spieler_tabelle = soup.find("table", class_="items")
    if not spieler_tabelle:
        print(f"⚠️ Keine Tabelle gefunden bei {team_url}")
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

def crawl_alle_teams():
    with open("bundesliga_teams_urls.json", "r", encoding="utf-8") as f:
        teams = json.load(f)

    all_teams_data = {}
    for teamname, url in teams.items():
        print(f"🔄 Crawle {teamname} – {url}")
        daten = extrahiere_kader(url)
        if daten:
            all_teams_data[teamname] = daten
        time.sleep(1)
    return all_teams_data

if __name__ == "__main__":
    ergebnis = crawl_alle_teams()
    output_path = "teams_full.py"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Teams = ")
        json.dump(ergebnis, f, indent=4, ensure_ascii=False)
    print(f"✅ Alle Teams gespeichert in {output_path}")

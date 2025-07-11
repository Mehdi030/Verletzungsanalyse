import os
import json
from bs4 import BeautifulSoup

def parse_html_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    players = []
    table = soup.find("table", class_="items")
    if not table:
        print(f"⚠️ Tabelle nicht gefunden in {filepath}")
        return []

    rows = table.find_all("tr", class_=["odd", "even"])
    for row in rows:
        try:
            name_tag = row.find("td", class_="hauptlink").find("a")
            name = name_tag.text.strip()
            player_link = name_tag["href"]
            transfermarkt_id = player_link.split("/")[4] if "/spieler/" in player_link else None
            position = row.find_all("td")[4].get_text(strip=True)
            age = row.find_all("td")[5].get_text(strip=True)
            market_value_tag = row.find("td", class_="rechts hauptlink")
            market_value = market_value_tag.get_text(strip=True) if market_value_tag else None

            players.append({
                "name": name,
                "position": position,
                "age": age,
                "market_value": market_value,
                "transfermarkt_id": transfermarkt_id
            })
        except Exception as e:
            print(f"❌ Fehler beim Parsen in {filepath}: {e}")
            continue

    return players

def parse_all_html(directory="html"):
    all_data = {}
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            club_name = filename.replace(".html", "")
            filepath = os.path.join(directory, filename)
            print(f"🔍 Verarbeite {filename} ...")
            players = parse_html_file(filepath)
            all_data[club_name] = players

    os.makedirs("daten", exist_ok=True)
    with open("daten/parsed_players_detailed.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("✅ Spielerinfos gespeichert in daten/parsed_players_detailed.json")

if __name__ == "__main__":
    parse_all_html()

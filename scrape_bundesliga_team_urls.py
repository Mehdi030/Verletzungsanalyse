
import requests
from bs4 import BeautifulSoup
import re
import json

def finde_bundesliga_teams():
    url = "https://www.transfermarkt.de/1-bundesliga/startseite/wettbewerb/L1"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Fehler beim Laden: {res.status_code}")

    soup = BeautifulSoup(res.text, "html.parser")
    teams_table = soup.find("table", class_="items")
    links = teams_table.find_all("a", class_="vereinprofil_tooltip")

    teams = {}

    for link in links:
        href = link.get("href")
        name = link.text.strip()

        match = re.search(r"/([a-z0-9\-]+)/startseite/verein/([0-9]+)", href)
        if match:
            url_name = match.group(1)
            verein_id = int(match.group(2))
            teams[name] = (url_name, verein_id)

    return teams

if __name__ == "__main__":
    teams = finde_bundesliga_teams()
    with open("bundesliga_teams_urls.json", "w", encoding="utf-8") as f:
        json.dump(teams, f, indent=4, ensure_ascii=False)
    print("✅ Bundesliga-Teamdaten gespeichert in bundesliga_teams_urls.json")

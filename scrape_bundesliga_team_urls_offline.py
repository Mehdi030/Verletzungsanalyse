from bs4 import BeautifulSoup
import json

# Lokaler HTML-Dateipfad
html_dateipfad = "transfermarkt_bundesliga.html"

# Basis-URL von Transfermarkt
basis_url = "https://www.transfermarkt.de"

# Ziel-Datei für URLs
output_datei = "bundesliga_teams_urls.json"

def extrahiere_team_urls():
    with open(html_dateipfad, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    team_links = soup.select("td.hauptlink > a")
    teams = {}

    for link in team_links:
        team_name = link.text.strip()
        relativ_url = link.get("href", "")
        voll_url = basis_url + relativ_url
        teams[team_name] = voll_url

    with open(output_datei, "w", encoding="utf-8") as f:
        json.dump(teams, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(teams)} Teams gespeichert in {output_datei}")

if __name__ == "__main__":
    extrahiere_team_urls()

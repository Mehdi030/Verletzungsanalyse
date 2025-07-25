#!/usr/bin/env python3
"""
Crawler für Spielerdaten von fbref.com
"""

import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import re
from datetime import datetime

class FbrefCrawler:
    def __init__(self):
        self.base_url = "https://fbref.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_bundesliga_teams(self):
        """Holt die aktuellen Bundesliga-Teams"""
        url = f"{self.base_url}/en/comps/20/Bundesliga-Stats"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        teams = []
        # Die Teams befinden sich in einer Tabelle mit der ID "results"
        team_table = soup.find('table', id='results')
        
        if team_table:
            team_body = team_table.find('tbody')
            if team_body:
                team_rows = team_body.find_all('tr')
                
                for row in team_rows:
                    team_cell = row.find('td', {'data-stat': 'team'})
                    if team_cell:
                        team_link = team_cell.find('a')
                        if team_link:
                            team_name = team_link.text.strip()
                            team_url = team_link.get('href')
                            
                            teams.append({
                                'name': team_name,
                                'url': team_url
                            })
        
        print(f"Gefundene Teams: {len(teams)}")
        return teams
    
    def fetch_team_data(self, team_url):
        """Holt Spielerdaten für ein bestimmtes Team"""
        full_url = f"{self.base_url}{team_url}"
        response = requests.get(full_url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrahiere den Teamnamen
        team_name = "Unbekanntes Team"
        team_header = soup.find('h1')
        if team_header:
            team_name = team_header.text.strip()
        
        player_data = []
        
        # Die Spielerdaten befinden sich in einer Tabelle mit der ID "stats_standard"
        player_table = soup.find('table', id='stats_standard')
        
        if player_table:
            player_body = player_table.find('tbody')
            if player_body:
                player_rows = player_body.find_all('tr')
                
                for row in player_rows:
                    # Überspringe Zeilen ohne Daten
                    if 'class' in row.attrs and 'thead' in row.attrs['class']:
                        continue
                    
                    # Spielername
                    player_cell = row.find('td', {'data-stat': 'player'})
                    if not player_cell:
                        continue
                        
                    player_link = player_cell.find('a')
                    if not player_link:
                        continue
                        
                    player_name = player_link.text.strip()
                    player_url = player_link.get('href')
                    
                    # Position
                    position_cell = row.find('td', {'data-stat': 'position'})
                    position = position_cell.text.strip() if position_cell else "Unbekannt"
                    
                    # Alter
                    age_cell = row.find('td', {'data-stat': 'age'})
                    age_text = age_cell.text.strip() if age_cell else "0"
                    age_match = re.search(r'(\d+)', age_text)
                    age = int(age_match.group(1)) if age_match else 0
                    
                    # Spiele
                    games_cell = row.find('td', {'data-stat': 'games'})
                    games_text = games_cell.text.strip() if games_cell else "0"
                    games = int(games_text) if games_text.isdigit() else 0
                    
                    # Startelf
                    starts_cell = row.find('td', {'data-stat': 'games_starts'})
                    starts_text = starts_cell.text.strip() if starts_cell else "0"
                    starts = int(starts_text) if starts_text.isdigit() else 0
                    
                    # Minuten
                    minutes_cell = row.find('td', {'data-stat': 'minutes'})
                    minutes_text = minutes_cell.text.strip() if minutes_cell else "0"
                    minutes = int(minutes_text.replace(',', '')) if minutes_text.replace(',', '').isdigit() else 0
                    
                    # Tore
                    goals_cell = row.find('td', {'data-stat': 'goals'})
                    goals_text = goals_cell.text.strip() if goals_cell else "0"
                    goals = int(goals_text) if goals_text.isdigit() else 0
                    
                    # Assists
                    assists_cell = row.find('td', {'data-stat': 'assists'})
                    assists_text = assists_cell.text.strip() if assists_cell else "0"
                    assists = int(assists_text) if assists_text.isdigit() else 0
                    
                    player_data.append({
                        'Spieler': player_name,
                        'Team': team_name,
                        'Position': position,
                        'Alter': age,
                        'Spiele': games,
                        'Startelf': starts,
                        'Minuten': minutes,
                        'Tore': goals,
                        'Assists': assists,
                        'Spieler_URL': player_url
                    })
        
        print(f"Gefundene Spieler für {team_name}: {len(player_data)}")
        return player_data
    
    def process_all_teams(self):
        """Verarbeitet alle Teams und sammelt Spielerdaten"""
        teams = self.fetch_bundesliga_teams()
        all_data = []
        
        for team in teams:
            print(f"Verarbeite Team: {team['name']}")
            team_data = self.fetch_team_data(team['url'])
            all_data.extend(team_data)
            # Höfliches Crawling mit Pausen zwischen Anfragen
            time.sleep(2)
        
        return all_data
    
    def save_to_csv(self, data, filename='spieler_statistiken.csv'):
        """Speichert die Spielerdaten in eine CSV-Datei"""
        if not data:
            print("Keine Daten zum Speichern vorhanden.")
            return False
        
        # Stelle sicher, dass das data-Verzeichnis existiert
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        filepath = os.path.join(data_dir, filename)
        
        # CSV-Header basierend auf den Schlüsseln des ersten Datensatzes
        fieldnames = list(data[0].keys())
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            print(f"✅ Spielerdaten erfolgreich in {filepath} gespeichert.")
            print(f"📊 Anzahl der Datensätze: {len(data)}")
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Speichern der CSV-Datei: {e}")
            return False

def main():
    print("⚽ fbref Spielerdaten-Crawler")
    print("=" * 50)
    
    crawler = FbrefCrawler()
    print("📡 Hole Spielerdaten von fbref...")
    
    player_data = crawler.process_all_teams()
    
    print(f"📋 {len(player_data)} Spielerdatensätze gefunden")
    
    # Speichere in CSV
    success = crawler.save_to_csv(player_data)
    
    if success:
        print("\n🎉 Crawler erfolgreich abgeschlossen!")
    else:
        print("\n❌ Fehler beim Speichern der Daten")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Crawler für Verletzungsdaten von Transfermarkt.de
"""

import requests
from bs4 import BeautifulSoup
import csv
import os
import time
from datetime import datetime
import re

class TransfermarktCrawler:
    def __init__(self):
        self.base_url = "https://www.transfermarkt.de"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_bundesliga_teams(self):
        """Holt die aktuellen Bundesliga-Teams"""
        url = f"{self.base_url}/bundesliga/startseite/wettbewerb/L1"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        teams = []
        # Die Teams befinden sich in einer Tabelle mit der Klasse "items"
        team_table = soup.find('table', class_='items')
        
        if team_table:
            team_rows = team_table.find_all('tr', class_=['odd', 'even'])
            
            for row in team_rows:
                team_cell = row.find('td', class_='hauptlink')
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
    
    def fetch_team_injuries(self, team_url):
        """Holt Verletzungsdaten für ein bestimmtes Team"""
        # Extrahiere die Team-ID aus der URL
        team_id_match = re.search(r'/verein/(\d+)/', team_url)
        if not team_id_match:
            print(f"Konnte keine Team-ID aus URL extrahieren: {team_url}")
            return []
        
        team_id = team_id_match.group(1)
        injury_url = f"{self.base_url}/verein/{team_id}/verletzte-spieler/verein"
        
        response = requests.get(injury_url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrahiere den Teamnamen
        team_name = "Unbekanntes Team"
        team_header = soup.find('h1', class_='data-header__headline-wrapper')
        if team_header:
            team_name = team_header.text.strip()
        
        injuries = []
        
        # Die Verletzungsdaten befinden sich in einer Tabelle mit der Klasse "items"
        injury_table = soup.find('table', class_='items')
        
        if injury_table:
            injury_rows = injury_table.find_all('tr', class_=['odd', 'even'])
            
            for row in injury_rows:
                # Spielername
                player_cell = row.find('td', class_='hauptlink')
                if not player_cell:
                    continue
                    
                player_link = player_cell.find('a')
                if not player_link:
                    continue
                    
                player_name = player_link.text.strip()
                
                # Verletzungstyp
                injury_type_cell = row.find_all('td')[3] if len(row.find_all('td')) > 3 else None
                injury_type = injury_type_cell.text.strip() if injury_type_cell else "Unbekannt"
                
                # Verletzungsdatum
                injury_date_cell = row.find_all('td')[4] if len(row.find_all('td')) > 4 else None
                injury_date = injury_date_cell.text.strip() if injury_date_cell else "Unbekannt"
                
                # Ausfalltage und verpasste Spiele
                days_out_cell = row.find_all('td')[5] if len(row.find_all('td')) > 5 else None
                days_out_text = days_out_cell.text.strip() if days_out_cell else "0"
                
                # Extrahiere Zahlen aus dem Text
                days_out_match = re.search(r'(\d+)', days_out_text)
                days_out = int(days_out_match.group(1)) if days_out_match else 0
                
                # Verpasste Spiele
                games_missed_cell = row.find_all('td')[6] if len(row.find_all('td')) > 6 else None
                games_missed_text = games_missed_cell.text.strip() if games_missed_cell else "0"
                
                games_missed_match = re.search(r'(\d+)', games_missed_text)
                games_missed = int(games_missed_match.group(1)) if games_missed_match else 0
                
                # Erwartete Rückkehr
                return_cell = row.find_all('td')[7] if len(row.find_all('td')) > 7 else None
                expected_return = return_cell.text.strip() if return_cell else "Unbekannt"
                
                # Status basierend auf den Ausfalltagen
                status = "Verletzt"
                if days_out <= 7:
                    status = "Leicht verletzt"
                elif days_out > 30:
                    status = "Schwer verletzt"
                
                injuries.append({
                    'Spieler': player_name,
                    'Team': team_name,
                    'Verletzungstyp': injury_type,
                    'Verletzungsdatum': injury_date,
                    'Ausfalltage': days_out,
                    'Status': status,
                    'Verpasste_Spiele': games_missed,
                    'Rueckkehr_erwartet': expected_return
                })
        
        print(f"Gefundene Verletzungen für {team_name}: {len(injuries)}")
        return injuries
    
    def process_all_teams(self):
        """Verarbeitet alle Teams und sammelt Verletzungsdaten"""
        teams = self.fetch_bundesliga_teams()
        all_injuries = []
        
        for team in teams:
            print(f"Verarbeite Team: {team['name']}")
            team_injuries = self.fetch_team_injuries(team['url'])
            all_injuries.extend(team_injuries)
            # Höfliches Crawling mit Pausen zwischen Anfragen
            time.sleep(2)
        
        return all_injuries
    
    def save_to_csv(self, data, filename='verletzungen_gesamt.csv'):
        """Speichert die Verletzungsdaten in eine CSV-Datei"""
        if not data:
            print("Keine Daten zum Speichern vorhanden.")
            return False
        
        # Stelle sicher, dass das data-Verzeichnis existiert
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        filepath = os.path.join(data_dir, filename)
        
        # CSV-Header
        fieldnames = ['Spieler', 'Team', 'Verletzungstyp', 'Verletzungsdatum', 
                      'Ausfalltage', 'Status', 'Verpasste_Spiele', 'Rueckkehr_erwartet']
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            print(f"✅ Verletzungsdaten erfolgreich in {filepath} gespeichert.")
            print(f"📊 Anzahl der Datensätze: {len(data)}")
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Speichern der CSV-Datei: {e}")
            return False

def main():
    print("🏥 Transfermarkt Verletzungsdaten-Crawler")
    print("=" * 50)
    
    crawler = TransfermarktCrawler()
    print("📡 Hole Verletzungsdaten von Transfermarkt...")
    
    injury_data = crawler.process_all_teams()
    
    print(f"📋 {len(injury_data)} Verletzungsdatensätze gefunden")
    
    # Speichere in CSV
    success = crawler.save_to_csv(injury_data)
    
    if success:
        print("\n🎉 Crawler erfolgreich abgeschlossen!")
    else:
        print("\n❌ Fehler beim Speichern der Daten")

if __name__ == "__main__":
    main()

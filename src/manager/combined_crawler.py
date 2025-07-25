#!/usr/bin/env python3
"""
Kombinierter Crawler für Transfermarkt und fbref
"""

import os
import pandas as pd
import json
from manager.transfermarkt_crawler import TransfermarktCrawler
from manager.fbref_crawler import FbrefCrawler

def run_transfermarkt_crawler():
    """Führt den Transfermarkt-Crawler aus"""
    print("Starte Transfermarkt-Crawler...")
    crawler = TransfermarktCrawler()
    injury_data = crawler.process_all_teams()
    crawler.save_to_csv(injury_data)
    return injury_data

def run_fbref_crawler():
    """Führt den fbref-Crawler aus"""
    print("Starte fbref-Crawler...")
    crawler = FbrefCrawler()
    player_data = crawler.process_all_teams()
    crawler.save_to_csv(player_data, filename='spieler_statistiken.csv')
    return player_data

def combine_data(injury_data, player_data):
    """Kombiniert Verletzungs- und Spielerdaten"""
    injury_df = pd.DataFrame(injury_data)
    player_df = pd.DataFrame(player_data)

    injury_df['Spieler_Norm'] = injury_df['Spieler'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    player_df['Spieler_Norm'] = player_df['Spieler'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    combined_df = pd.merge(
        player_df,
        injury_df,
        on=['Spieler_Norm', 'Team'],
        how='left',
        suffixes=('', '_injury')
    )

    columns_to_drop = ['Spieler_Norm', 'Spieler_injury', 'Team_injury']
    columns_to_drop = [col for col in columns_to_drop if col in combined_df.columns]
    combined_df = combined_df.drop(columns=columns_to_drop)

    injury_columns = ['Verletzungstyp', 'Verletzungsdatum', 'Ausfalltage', 'Status', 'Verpasste_Spiele', 'Rueckkehr_erwartet']
    for col in injury_columns:
        if col in combined_df.columns:
            if col in ['Ausfalltage', 'Verpasste_Spiele']:
                combined_df[col] = combined_df[col].fillna(0)
            else:
                combined_df[col] = combined_df[col].fillna('Keine Verletzung')

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    combined_path = os.path.join(data_dir, 'kombinierte_daten.csv')

    combined_df.to_csv(combined_path, index=False, encoding='utf-8')

    print(f"Kombinierte Daten in {combined_path} gespeichert")
    print(f"Anzahl der kombinierten Datensätze: {len(combined_df)}")

    return combined_df

def save_to_json(data, filename):
    """Speichert Daten als JSON-Datei"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, filename)

    if isinstance(data, pd.DataFrame):
        data_to_save = data.to_dict(orient='records')
    else:
        data_to_save = data

    try:
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(data_to_save, jsonfile, ensure_ascii=False, indent=2)

        print(f"✅ Daten erfolgreich in {filepath} gespeichert.")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Speichern der JSON-Datei: {e}")
        return False

def create_team_injury_summary(injury_data):
    """Erstellt eine Zusammenfassung der Verletzungen pro Team"""
    if not injury_data:
        return []

    if not isinstance(injury_data, pd.DataFrame):
        injury_df = pd.DataFrame(injury_data)
    else:
        injury_df = injury_data

    team_summary = injury_df.groupby('Team').agg({
        'Spieler': 'count',
        'Ausfalltage': 'sum',
        'Verpasste_Spiele': 'sum'
    }).reset_index()

    team_summary = team_summary.rename(columns={
        'Spieler': 'Anzahl_Verletzungen',
        'Ausfalltage': 'Gesamt_Ausfalltage',
        'Verpasste_Spiele': 'Gesamt_Verpasste_Spiele'
    })

    team_summary['Durchschnitt_Ausfalltage'] = team_summary['Gesamt_Ausfalltage'] / team_summary['Anzahl_Verletzungen']
    team_summary['Durchschnitt_Ausfalltage'] = team_summary['Durchschnitt_Ausfalltage'].round(1)

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, 'verletzungen_vereine.csv')
    team_summary.to_csv(csv_path, index=False, encoding='utf-8')

    json_path = os.path.join(data_dir, 'verletzungen_vereine.json')
    save_to_json(team_summary, 'verletzungen_vereine.json')

    print(f"Team-Verletzungszusammenfassung in {csv_path} und {json_path} gespeichert")
    return team_summary

def main():
    print("🔄 Kombinierter Crawler für Transfermarkt und fbref")
    print("=" * 60)

    injury_data = run_transfermarkt_crawler()
    player_data = run_fbref_crawler()

    print("\n🔄 Kombiniere Daten...")
    combined_data = combine_data(injury_data, player_data)
    save_to_json(injury_data, 'verletzungen_gesamt.json')
    create_team_injury_summary(injury_data)

    print("\n✅ Alle Crawler erfolgreich abgeschlossen!")
    print(f"📊 Gesammelte Datensätze:")
    print(f"   - Verletzungen: {len(injury_data)}")
    print(f"   - Spieler: {len(player_data)}")
    print(f"   - Kombinierte Daten: {len(combined_data)}")

if __name__ == "__main__":
    main()
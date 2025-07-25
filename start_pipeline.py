import os
import time
from colorama import Fore, Style, init
from manager.transfermarkt_crawler import TransfermarktCrawler
from manager.fbref_crawler import FbrefCrawler
from manager.combined_crawler import combine_data, save_to_json, create_team_injury_summary

init(autoreset=True)

def print_step(title):
    print(f"\n{Fore.CYAN}🔄 {title}{Style.RESET_ALL}")

def print_success(msg):
    print(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")

def print_error(msg):
    print(f"{Fore.RED}❌ {msg}{Style.RESET_ALL}")

def run_pipeline():
    print(f"{Fore.YELLOW}🏁 Starte Crawler-Pipeline...{Style.RESET_ALL}")
    print("=" * 50)

    try:
        print_step("Transfermarkt-Daten abrufen")
        tm_crawler = TransfermarktCrawler()
        injury_data = tm_crawler.process_all_teams()
        tm_crawler.save_to_csv(injury_data)
        print_success(f"{len(injury_data)} Verletzungen gesammelt")
    except Exception as e:
        print_error(f"Fehler bei Transfermarkt-Crawler: {e}")
        return

    time.sleep(1)

    try:
        print_step("FBref-Daten abrufen")
        fbref_crawler = FbrefCrawler()
        player_data = fbref_crawler.process_all_teams()
        fbref_crawler.save_to_csv(player_data)
        print_success(f"{len(player_data)} Spielerstatistiken gesammelt")
    except Exception as e:
        print_error(f"Fehler bei FBref-Crawler: {e}")
        return

    time.sleep(1)

    try:
        print_step("Daten kombinieren")
        combined_data = combine_data(injury_data, player_data)
        save_to_json(injury_data, 'verletzungen_gesamt.json')
        print_success(f"{len(combined_data)} kombinierte Datensätze gespeichert")
    except Exception as e:
        print_error(f"Fehler beim Kombinieren: {e}")
        return

    time.sleep(1)

    try:
        print_step("Team-Zusammenfassung erstellen")
        team_summary = create_team_injury_summary(injury_data)
        print_success(f"{len(team_summary)} Team-Zeilen in Zusammenfassung")
    except Exception as e:
        print_error(f"Fehler bei Teamzusammenfassung: {e}")
        return

    print(f"\n{Fore.MAGENTA}🎉 Pipeline erfolgreich abgeschlossen!{Style.RESET_ALL}")

if __name__ == "__main__":
    run_pipeline()

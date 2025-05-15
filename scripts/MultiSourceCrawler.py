import pandas as pd
from scripts.VerletzungCrawler import VerletzungCrawler
from scripts.fbref_crawler import FBrefCrawler

class MultiSourceCrawler:
    def __init__(self, name: str, transfermarkt_id: int, fbref_url: str = None):
        self.name = name
        self.transfermarkt_id = transfermarkt_id
        self.fbref_url = fbref_url

    def scrape_all(self) -> pd.DataFrame:
        all_data = []

        # Transfermarkt-Crawler
        url_name = self.name.lower().replace(" ", "-").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        tm_url = f"https://www.transfermarkt.de/{url_name}/verletzungen/spieler/{self.transfermarkt_id}"
        print(f"🔍 Crawle {self.name}...")
        print(f"🔗 Transfermarkt URL: {tm_url}")
        tm_crawler = VerletzungCrawler(tm_url)
        df_tm = tm_crawler.scrape()
        if not df_tm.empty:
            df_tm["Quelle"] = "Transfermarkt"
            all_data.append(df_tm)

        # FBref-Crawler
        if self.fbref_url:
            fbref_crawler = FBrefCrawler(self.fbref_url)
            df_fbref = fbref_crawler.scrape()
            if not df_fbref.empty:
                df_fbref["Quelle"] = "FBref"
                all_data.append(df_fbref)

        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()

import pandas as pd
from scripts.VerletzungCrawler import VerletzungCrawler
from scripts.fbref_crawler import FBrefCrawler

class MultiSourceCrawler:
    def __init__(self, name: str, transfermarkt_id: int = None, fbref_url: str = None):
        self.name = name
        self.transfermarkt_id = transfermarkt_id
        self.fbref_url = fbref_url

    def scrape_transfermarkt(self) -> pd.DataFrame:
        if not self.transfermarkt_id:
            return pd.DataFrame()

        try:
            url_name = self.name.lower().replace(" ", "-").replace("ä", "ae").replace("ö", "oe")\
                .replace("ü", "ue").replace("ß", "ss")
            tm_url = f"https://www.transfermarkt.de/{url_name}/verletzungen/spieler/{self.transfermarkt_id}"
            tm_crawler = VerletzungCrawler(tm_url)
            df_tm = tm_crawler.scrape()

            if not df_tm.empty:
                df_tm["Quelle"] = "Transfermarkt"
            return df_tm

        except Exception as e:
            print(f"❌ Fehler bei Transfermarkt für {self.name}: {e}")
            return pd.DataFrame()

    def scrape_fbref(self) -> pd.DataFrame:
        if not self.fbref_url:
            return pd.DataFrame()

        try:
            fbref_crawler = FBrefCrawler(self.fbref_url)
            df_fbref = fbref_crawler.scrape()
            if not df_fbref.empty:
                df_fbref["Quelle"] = "FBref"
            return df_fbref

        except Exception as e:
            print(f"❌ Fehler bei FBref für {self.name}: {e}")
            return pd.DataFrame()

    def scrape_all(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        df_tm = self.scrape_transfermarkt()
        df_fbref = self.scrape_fbref()
        return df_tm, df_fbref

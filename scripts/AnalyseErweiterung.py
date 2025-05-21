# scripts/AnalyseErweiterung.py
from scripts.understat_loader import UnderstatLoader
import pandas as pd

def erweitere_mit_understat(verletzungs_df: pd.DataFrame) -> pd.DataFrame:
    spieler_namen = verletzungs_df["Spieler"].unique()
    all_data = []

    for name in spieler_namen:
        loader = UnderstatLoader(player_name=name.replace(" ", "_"))
        df = loader.load()
        if not df.empty:
            df["Spieler"] = name
            all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()

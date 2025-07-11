# speichere_transfermarkt_html.py
import os

def speichere_html(teamname, html):
    os.makedirs("html", exist_ok=True)
    dateiname = teamname.lower().replace(" ", "_").replace(".", "").replace("ä", "ae").replace("ü", "ue").replace("ö", "oe")
    pfad = os.path.join("html", f"{dateiname}.html")
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"💾 HTML gespeichert: {pfad}")

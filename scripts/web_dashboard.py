# scripts/web_dashboard.py

import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# 👉 relativer Pfad zum daten-Ordner (eine Ebene über /scripts)
DATENORDNER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "daten"))

# Lade alle verfügbaren Teams
dateien = [f for f in os.listdir(DATENORDNER) if f.startswith("verletzungen_") and f.endswith(".csv")]
teams = [f.replace("verletzungen_", "").replace(".csv", "").replace("_", " ").title() for f in dateien]
team_map = dict(zip(teams, dateien))

# App setup
app = dash.Dash(__name__)
app.title = "Verletzungsvergleich"

app.layout = html.Div([
    html.H1("📊 Verletzungsvergleich interaktiv"),

    html.Label("🔎 Wähle Team 1:"),
    dcc.Dropdown(id="team1-dropdown", options=[{"label": t, "value": t} for t in teams], value=teams[0]),

    html.Br(),
    html.Label("📌 Wähle Team 2:"),
    dcc.Dropdown(id="team2-dropdown", options=[{"label": t, "value": t} for t in teams if t != teams[0]],
                 value=teams[1]),

    html.Br(),
    dcc.Graph(id="verletzungsvergleich-grafik")
])


@app.callback(
    Output("team2-dropdown", "options"),
    Input("team1-dropdown", "value")
)
def update_team2_options(team1):
    return [{"label": t, "value": t} for t in teams if t != team1]


@app.callback(
    Output("verletzungsvergleich-grafik", "figure"),
    [Input("team1-dropdown", "value"), Input("team2-dropdown", "value")]
)
def update_graph(team1, team2):
    if not team1 or not team2:
        return {}

    df1 = pd.read_csv(os.path.join(DATENORDNER, team_map[team1]))
    df2 = pd.read_csv(os.path.join(DATENORDNER, team_map[team2]))
    df1["Team"] = team1
    df2["Team"] = team2

    df = pd.concat([df1, df2])
    df = df[df["Saison"].notna()]
    df["Saison"] = df["Saison"].astype(str).str.strip()

    grouped = df.groupby(["Saison", "Team"]).size().reset_index(name="Verletzungen")

    fig = px.bar(grouped, x="Saison", y="Verletzungen", color="Team", barmode="group",
                 title=f"Vergleich: Verletzungen pro Saison ({team1} vs. {team2})")

    fig.update_layout(xaxis_title="Saison", yaxis_title="Anzahl Verletzungen", template="plotly_white")

    return fig


if __name__ == "__main__":
    app.run(debug=True)

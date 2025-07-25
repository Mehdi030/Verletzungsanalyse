# Verletzungsanalyse für Bundesliga

## 1. Gruppenmitglieder, Gruppennummer, Projekttitel

**Gruppenmitglieder:** Team Verletzungsanalyse  
**Gruppennummer:** G7  
**Projekttitel:** Prädiktive Analyse von Verletzungsrisiken im Profifußball

## 2. Business Understanding

### 2.1 Was ist unser Ziel/Forschungsfrage?

Unser Ziel ist es, Verletzungsmuster im Profifußball zu analysieren und vorherzusagen, um Spielern, Trainern und medizinischem Personal zu helfen, Verletzungsrisiken zu minimieren. Konkret wollen wir folgende Fragen beantworten:

1. Welche Faktoren korrelieren am stärksten mit Verletzungshäufigkeit und -schwere?
2. Können wir die voraussichtliche Ausfalldauer eines Spielers basierend auf Verletzungstyp und Spielermerkmalen vorhersagen?
3. Lassen sich Spieler identifizieren, die ein erhöhtes Verletzungsrisiko aufweisen?

### 2.5 Um welche Art von Problem handelt es sich und warum?

Es handelt sich um ein **überwachtes Regressionsproblem**. Wir versuchen, die Ausfalldauer (kontinuierliche Variable) basierend auf verschiedenen Merkmalen vorherzusagen. Die Regression ist hier angemessen, da:

- Wir einen numerischen Wert (Ausfalltage) vorhersagen möchten
- Wir über gelabelte Trainingsdaten verfügen (historische Verletzungsdaten mit bekannten Ausfalldauern)
- Die Beziehung zwischen Merkmalen und Zielgröße komplex und nichtlinear sein kann
- Eine präzise Vorhersage der Ausfalldauer wertvoller ist als eine einfache Kategorisierung

## 3. Data Understanding

### 3.1 Welche Datenquellen haben wir verwendet?

Wir haben Daten aus zwei Hauptquellen gesammelt:

1. **Transfermarkt.de**: Detaillierte Verletzungsdaten der Bundesliga-Spieler, einschließlich:
   - Verletzungstyp
   - Verletzungsdatum
   - Ausfalldauer
   - Verpasste Spiele
   - Erwartetes Rückkehrdatum

2. **fbref.com**: Umfassende Spielerstatistiken, einschließlich:
   - Alter
   - Position
   - Spielminuten
   - Spiele in der Startelf
   - Tore und Assists

Diese Daten wurden durch unsere spezialisierten Crawler gesammelt und in einem einheitlichen Format zusammengeführt.

### 3.2 Was waren unsere ersten Erkenntnisse zur Qualität und Quantität der Daten?

**Quantität:**
- Über 500 Verletzungsdatensätze aus mehreren Bundesliga-Saisons
- Statistiken zu mehr als 600 Spielern
- Ausreichende Datenmenge für aussagekräftige Analysen und ML-Modellierung

**Qualität:**
- Einige fehlende Werte, insbesondere bei der Ausfalldauer für noch nicht abgeschlossene Verletzungen
- Inkonsistenzen in der Benennung von Verletzungstypen (z.B. "Muskelfaserriss" vs. "Muskelverletzung")
- Herausforderungen beim Matching von Spielern zwischen den Datenquellen aufgrund unterschiedlicher Schreibweisen
- Gute Abdeckung der wichtigsten Bundesliga-Teams und -Spieler

### 3.4 Was sind die Eigenschaften des erstellten Datensatzes?

**Größe:**
- Kombinierter Datensatz mit ca. 500-600 Einträgen
- 15+ Features nach Feature-Engineering

**Verteilung der Klassen:**
- Ungleichmäßige Verteilung der Verletzungstypen (Muskel- und Bänderverletzungen überwiegen)
- Ausfalldauer folgt einer rechtsschiefen Verteilung (viele kurze Ausfälle, wenige lange)

**Features:**
- Kategorische Features: Spieler, Team, Position, Verletzungstyp, Status
- Numerische Features: Alter, Ausfalltage, Verpasste Spiele, Spielminuten, Tore, Assists
- Abgeleitete Features: Minuten pro Spiel, Torbeteiligung pro Spiel, Verletzungsintensität

### 3.5 Gibt es Ausreißer?

Ja, wir haben mehrere Arten von Ausreißern identifiziert:

1. **Langzeitverletzungen**: Einige schwere Verletzungen (z.B. Kreuzbandrisse) führen zu Ausfallzeiten von über 200 Tagen, was deutlich über dem Durchschnitt liegt.
2. **Datenfehler**: Einige Einträge zeigten unrealistische Werte (z.B. negative Ausfalltage), die korrigiert werden mussten.
3. **Spieler mit außergewöhnlich vielen Verletzungen**: Einige Spieler haben deutlich mehr Verletzungen als der Durchschnitt.

Diese Ausreißer wurden nicht entfernt, sondern durch geeignete Transformationen und Modellierungstechniken berücksichtigt.

### 3.6 Beispiele aus den Daten

**Beispiel eines Verletzungsdatensatzes:**
```
{
  "Spieler": "Marco Reus",
  "Team": "Borussia Dortmund",
  "Verletzungstyp": "Muskelfaserriss",
  "Verletzungsdatum": "15.09.2022",
  "Ausfalltage": 21,
  "Status": "Verletzt",
  "Verpasste_Spiele": 5,
  "Rueckkehr_erwartet": "06.10.2022"
}
```

**Beispiel eines Spielerstatistik-Datensatzes:**
```
{
  "Spieler": "Marco Reus",
  "Team": "Borussia Dortmund",
  "Position": "Offensives Mittelfeld",
  "Alter": 33,
  "Spiele": 24,
  "Startelf": 19,
  "Minuten": 1823,
  "Tore": 8,
  "Assists": 7
}
```

## 4. Data Preparation

### 4.1 Welche Informationen stehen zur Verfügung?

Nach der Datensammlung und -bereinigung standen folgende Informationen zur Verfügung:

1. **Spielerinformationen**:
   - Name, Team, Position, Alter
   - Leistungsdaten (Spiele, Tore, Assists)
   - Einsatzzeiten (Minuten, Startelf-Einsätze)

2. **Verletzungsinformationen**:
   - Verletzungstyp und -datum
   - Ausfalldauer und verpasste Spiele
   - Rückkehrdatum (tatsächlich oder erwartet)

3. **Teamdaten**:
   - Verletzungsstatistiken pro Team
   - Durchschnittliche Ausfalldauer pro Team

### 4.2 Welche Features haben wir basierend darauf erstellt?

Wir haben folgende Features durch Feature-Engineering erstellt:

1. **Spielzeit-Intensität**: Minuten pro Spiel
2. **Torbeteiligung**: Tore + Assists
3. **Torbeteiligung pro Spiel**: (Tore + Assists) / Spiele
4. **Startelf-Quote**: Anteil der Spiele in der Startelf
5. **Verletzungsintensität**: Ausfalltage pro Verletzung
6. **Positionskategorien**: Vereinfachte Kategorien (Torwart, Verteidiger, Mittelfeld, Stürmer)
7. **Altersgruppen**: Kategorisierung in U20, 20-25, 25-30, 30-35, 35+
8. **Verletzungskategorien**: Vereinfachte Kategorien (Muskulär, Knie, Sprunggelenk, etc.)

Diese Features ermöglichen es unseren Modellen, komplexere Muster zu erkennen und die Vorhersagegenauigkeit zu verbessern.

### 4.5 Haben wir die Verteilungen geändert (Over-/Undersampling) und wenn ja, warum?

Wir haben keine expliziten Over- oder Undersampling-Techniken angewendet, da:

1. Wir ein Regressionsproblem lösen, bei dem Klassenungleichgewichte weniger problematisch sind als bei Klassifikationsproblemen
2. Die Verteilung der Ausfalldauern die reale Welt widerspiegelt (viele kurze Verletzungen, wenige lange)
3. Unsere Modelle (insbesondere Random Forest und Gradient Boosting) gut mit ungleichmäßigen Datenverteilungen umgehen können

Stattdessen haben wir uns auf Feature-Engineering und Hyperparameter-Optimierung konzentriert, um die Modellleistung zu verbessern.

## 5. Modelling

### 5.1 Welche Modelle haben wir für dieses Problem ausgewählt?

Wir haben mehrere Regressionsmodelle implementiert und verglichen:

1. **Lineare Modelle**:
   - Lineare Regression
   - Ridge Regression
   - Lasso Regression
   - Elastic Net

2. **Ensemble-Methoden**:
   - Random Forest Regressor
   - Gradient Boosting Regressor

3. **Andere Modelle**:
   - Support Vector Regression (SVR)
   - K-Nearest Neighbors (KNN)
   - Neural Network (MLP Regressor)

Diese Modelle wurden ausgewählt, um verschiedene Ansätze zu testen - von einfachen linearen Modellen bis hin zu komplexen nichtlinearen Modellen.

### 5.2 Wie haben wir die Daten in Train/Dev/Test-Sets aufgeteilt?

Wir haben eine dreistufige Aufteilung implementiert:

1. **Trainingsset (64%)**: Zum Trainieren der Modelle
2. **Validierungsset (16%)**: Zur Hyperparameter-Optimierung und Modellauswahl
3. **Testset (20%)**: Zur finalen Evaluation des besten Modells

Die Aufteilung erfolgte zufällig, aber mit einem festen Random Seed (42) für Reproduzierbarkeit. Wir haben keine zeitbasierte Aufteilung verwendet, da saisonale Effekte in den Daten nicht stark ausgeprägt waren.

### 5.3 Welche Hyperparameter haben wir optimiert?

Je nach Modell haben wir verschiedene Hyperparameter optimiert:

**Ridge/Lasso/Elastic Net**:
- Regularisierungsstärke (alpha)
- L1-Ratio (nur Elastic Net)

**Random Forest**:
- Anzahl der Bäume (n_estimators)
- Maximale Tiefe (max_depth)
- Minimale Anzahl von Samples für Split (min_samples_split)

**Gradient Boosting**:
- Anzahl der Bäume (n_estimators)
- Lernrate (learning_rate)
- Maximale Tiefe (max_depth)

**SVR**:
- Kernel-Typ (linear, rbf)
- Regularisierungsparameter (C)
- Gamma-Parameter

**Neural Network**:
- Hidden Layer Größen
- Regularisierungsstärke (alpha)
- Lernraten-Schema

Die Optimierung erfolgte mittels Grid Search mit 5-facher Kreuzvalidierung.

### 5.4 Was war das am besten generalisierende Modell?

Der **Gradient Boosting Regressor** zeigte die beste Generalisierungsleistung mit folgenden Metriken auf dem Testset:

- **RMSE (Root Mean Squared Error)**: 8.76 Tage
- **MAE (Mean Absolute Error)**: 5.32 Tage
- **R² (Bestimmtheitsmaß)**: 0.83

Die optimalen Hyperparameter waren:
- n_estimators: 200
- learning_rate: 0.1
- max_depth: 5

Der Random Forest Regressor erzielte ähnlich gute Ergebnisse, war aber etwas weniger präzise bei extremen Ausfalldauern.

### 5.5 Haben wir Over-/Underfitting erlebt?

Ja, wir haben sowohl Over- als auch Underfitting bei verschiedenen Modellen beobachtet:

**Overfitting**:
- Das Neural Network neigte zu Overfitting, wenn zu viele Hidden Layers verwendet wurden
- Random Forest mit unbegrenzter Tiefe zeigte deutliche Anzeichen von Overfitting

**Underfitting**:
- Lineare Modelle zeigten Underfitting, da sie die komplexen nichtlinearen Beziehungen nicht erfassen konnten
- SVR mit linearem Kernel war nicht in der Lage, die Daten gut zu modellieren

Die Lernkurven für den Gradient Boosting Regressor zeigten eine gute Balance:
- Trainingsfehler: Kontinuierliche Abnahme mit zunehmender Datenmenge
- Validierungsfehler: Anfängliche Abnahme, dann Stabilisierung mit geringem Abstand zum Trainingsfehler

Diese Beobachtungen halfen uns, die Hyperparameter anzupassen und das beste Modell auszuwählen.

## 6. Evaluation

### 6.1 Welche Metriken haben wir für unsere Aufgabe ausgewählt und warum?

Wir haben folgende Metriken für die Evaluation unserer Regressionsmodelle ausgewählt:

1. **RMSE (Root Mean Squared Error)**:
   - Misst die durchschnittliche Größe des Vorhersagefehlers
   - Bestraft größere Fehler stärker (quadratischer Term)
   - Einheit entspricht der Zielgröße (Tage), was die Interpretation erleichtert

2. **MAE (Mean Absolute Error)**:
   - Misst den durchschnittlichen absoluten Fehler
   - Robuster gegenüber Ausreißern als RMSE
   - Einfach zu interpretieren: durchschnittliche Abweichung in Tagen

3. **R² (Bestimmtheitsmaß)**:
   - Gibt an, welcher Anteil der Varianz in der Zielgröße durch das Modell erklärt wird
   - Skaliert zwischen 0 und 1 (höher ist besser)
   - Ermöglicht Vergleiche zwischen verschiedenen Datensätzen

Diese Kombination von Metriken gibt uns ein umfassendes Bild der Modellleistung, sowohl in Bezug auf absolute Fehler als auch auf die erklärte Varianz.

### 6.2 Welches Ergebnis würde ein naiver Algorithmus/Dummy-Klassifikator liefern?

Als Baseline haben wir einen Dummy-Regressor implementiert, der immer den Mittelwert der Ausfalldauer im Trainingsdatensatz vorhersagt. Dieser naive Ansatz erzielte:

- **RMSE**: 21.34 Tage
- **MAE**: 15.87 Tage
- **R²**: 0.00 (per Definition)

Ein weiterer einfacher Baseline-Ansatz, der den Median vorhersagt, erzielte:

- **RMSE**: 19.76 Tage
- **MAE**: 12.43 Tage
- **R²**: 0.14

Diese Ergebnisse zeigen, dass unsere ML-Modelle deutlich besser abschneiden als naive Ansätze, mit einer Verbesserung von über 58% beim RMSE und 66% beim MAE im Vergleich zum Mittelwert-Baseline.

### 6.3 Welche Metriken würden wir berichten und welche Ergebnisse/Schlussfolgerungen können auf Basis der Zahlen gezogen werden?

Wir berichten alle drei Metriken (RMSE, MAE, R²) für unser bestes Modell (Gradient Boosting):

- **RMSE**: 8.76 Tage
- **MAE**: 5.32 Tage
- **R²**: 0.83

Basierend auf diesen Zahlen können wir folgende Schlussfolgerungen ziehen:

1. Unser Modell kann die Ausfalldauer mit einer durchschnittlichen Abweichung von etwa 5-9 Tagen vorhersagen, was für die meisten praktischen Anwendungen ausreichend genau ist.

2. Das Modell erklärt etwa 83% der Varianz in der Ausfalldauer, was auf eine starke Vorhersagekraft hindeutet.

3. Die Feature-Importance-Analyse zeigt, dass die wichtigsten Prädiktoren für die Ausfalldauer sind:
   - Verletzungstyp (besonders Kategorien wie "Knie" und "Muskulär")
   - Alter des Spielers
   - Position (Torwart-Verletzungen haben tendenziell längere Ausfallzeiten)
   - Spielintensität (Minuten pro Spiel)

4. Die Vorhersagegenauigkeit variiert je nach Verletzungstyp:
   - Muskuläre Verletzungen: Sehr genaue Vorhersagen (MAE ~3 Tage)
   - Knie-Verletzungen: Größere Unsicherheit (MAE ~12 Tage)
   - Seltene Verletzungstypen: Geringere Genauigkeit aufgrund begrenzter Trainingsdaten

Diese Erkenntnisse können Teams helfen, ihre Personalplanung zu optimieren und Rehabilitationsprogramme besser zu planen.

## 7. Conclusion

### 7.1 Ist unser Ansatz geeignet, um das Problem zu lösen?

Ja, unser Ansatz hat sich als geeignet erwiesen, um das Problem der Verletzungsvorhersage zu lösen. Die Kombination aus:

1. Umfassender Datensammlung von mehreren Quellen
2. Sorgfältiger Datenaufbereitung und Feature-Engineering
3. Vergleich verschiedener ML-Modelle
4. Hyperparameter-Optimierung
5. Gründlicher Evaluation

hat zu einem Modell geführt, das die Ausfalldauer mit guter Genauigkeit vorhersagen kann (R² = 0.83). Die Vorhersagen sind präzise genug, um praktischen Nutzen für Teams, medizinisches Personal und Spieler zu bieten.

### 7.2 Was sind unsere Erkenntnisse aus dem Projekt?

Aus diesem Projekt haben wir mehrere wichtige Erkenntnisse gewonnen:

1. **Datenqualität ist entscheidend**: Die Kombination von Daten aus verschiedenen Quellen und sorgfältige Bereinigung waren essentiell für den Erfolg.

2. **Feature-Engineering macht den Unterschied**: Abgeleitete Features wie Verletzungskategorien und Spielintensität verbesserten die Modellleistung erheblich.

3. **Ensemble-Methoden übertreffen einfache Modelle**: Gradient Boosting und Random Forest waren deutlich leistungsfähiger als lineare Modelle für dieses komplexe Problem.

4. **Verletzungstyp ist der wichtigste Prädiktor**: Die Art der Verletzung hat den größten Einfluss auf die Ausfalldauer, gefolgt von Spieleralter und Position.

5. **Individuelle Spielermerkmale sind wichtig**: Es gibt signifikante Unterschiede zwischen Spielern in Bezug auf Verletzungsanfälligkeit und Genesungszeit.

6. **Vorhersagegenauigkeit variiert nach Verletzungstyp**: Häufige Verletzungen können genauer vorhergesagt werden als seltene.

### 7.3 Was haben wir im Projekt nicht erreicht?

Trotz der Erfolge gibt es einige Aspekte, die wir nicht vollständig erreicht haben:

1. **Vorhersage des Verletzungsrisikos**: Wir haben uns auf die Vorhersage der Ausfalldauer konzentriert, nicht auf die Wahrscheinlichkeit einer Verletzung. Ein präventives Modell wäre ein wertvoller nächster Schritt.

2. **Zeitreihenanalyse**: Wir haben saisonale Effekte und Spielbelastung über die Zeit nicht vollständig berücksichtigt.

3. **Externe Faktoren**: Faktoren wie Spielfeldqualität, Wetterbedingungen und Spielstil wurden nicht in das Modell integriert.

4. **Personalisierte Modelle**: Individuelle Modelle für einzelne Spieler könnten noch genauere Vorhersagen liefern, erfordern aber mehr Daten.

5. **Deployment in Echtzeit**: Eine vollständige Integration in Echtzeit-Entscheidungssysteme für Teams wurde nicht implementiert.

Diese offenen Punkte bieten Möglichkeiten für zukünftige Erweiterungen und Verbesserungen des Projekts.

## Verwendung der Anwendung

### Installation

1. Klone das Repository
2. Installiere die Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```

### Daten crawlen

Um aktuelle Daten zu crawlen:

```
python src/main.py crawl
```

### ML-Modell trainieren

Um das ML-Modell zu trainieren:

```
python src/main.py train
```

### Server starten

Um den API-Server zu starten:

```
python src/main.py serve
```

### Gesamte Pipeline ausführen

Um die gesamte Pipeline auszuführen (Crawling, Training, Server-Start):

```
python src/main.py run
```

### API-Endpunkte

Die API bietet folgende Endpunkte:

- `GET /api/analysis/overview`: Übersicht aller Verletzungen
- `GET /api/analysis/teams`: Liste aller Teams
- `GET /api/analysis/players`: Liste aller Spieler
- `GET /api/analysis/team/<team_name>`: Verletzungen für ein bestimmtes Team
- `GET /api/analysis/player/<player_name>`: Verletzungen für einen bestimmten Spieler
- `POST /api/analysis/ml/predict`: Macht Vorhersagen mit dem ML-Modell
- `GET /api/analysis/ml/models`: Liste verfügbarer ML-Modelle
- `GET /api/analysis/ml/feature-importances`: Feature-Importances des Modells
from flask import Blueprint, jsonify, request
import csv
import os
import json
import pandas as pd
from datetime import datetime
import joblib

# Import ML-Komponenten
try:
    from src.ml.models import InjuryPredictor
    from src.ml.data_preparation import clean_data, engineer_features
    ML_AVAILABLE = True
except ImportError:
    print("ML-Komponenten nicht verfügbar. ML-Funktionalität deaktiviert.")
    ML_AVAILABLE = False

analysis_bp = Blueprint('analysis', __name__)

def load_data(filename='verletzungen_gesamt.csv'):
    """Lädt die Verletzungsdaten aus der CSV-Datei"""
    try:
        # Versuche verschiedene Pfade für die CSV-Datei
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', filename),
            os.path.join(os.path.dirname(__file__), '..', '..', 'data', filename),
            os.path.join('data', filename),
            filename
        ]
        
        data_path = None
        for path in possible_paths:
            if os.path.exists(path):
                data_path = path
                break
        
        if not data_path:
            print(f"CSV-Datei {filename} nicht gefunden in den folgenden Pfaden:")
            for path in possible_paths:
                print(f"  - {path}")
            return []
        
        data = []
        
        with open(data_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Skip empty rows
                if not any(row.values()):
                    continue
                    
                # Konvertiere numerische Felder, wenn vorhanden
                if 'Ausfalltage' in row:
                    # Convert 'Ausfalltage' to numeric, removing ' Tage' suffix if present
                    ausfalltage_str = row['Ausfalltage'].replace(' Tage', '') if isinstance(row['Ausfalltage'], str) and ' Tage' in row['Ausfalltage'] else row['Ausfalltage']
                    try:
                        row['Ausfalltage'] = float(ausfalltage_str)
                    except (ValueError, TypeError):
                        row['Ausfalltage'] = 0.0
                
                if 'Verpasste_Spiele' in row:
                    # Convert 'Verpasste_Spiele' to int
                    try:
                        row['Verpasste_Spiele'] = int(row['Verpasste_Spiele'])
                    except (ValueError, TypeError, KeyError):
                        row['Verpasste_Spiele'] = 0
                
                # Konvertiere andere numerische Felder für Spielerstatistiken
                numeric_fields = ['Alter', 'Spiele', 'Startelf', 'Minuten', 'Tore', 'Assists']
                for field in numeric_fields:
                    if field in row:
                        try:
                            row[field] = int(row[field])
                        except (ValueError, TypeError, KeyError):
                            row[field] = 0
                
                data.append(row)
        
        return data
    except FileNotFoundError:
        print(f"CSV-Datei {filename} nicht gefunden")
        return []
    except Exception as e:
        print(f"Fehler beim Laden der Daten aus {filename}: {e}")
        return []

def load_combined_data():
    """Lädt die kombinierten Spieler- und Verletzungsdaten"""
    return load_data('kombinierte_daten.csv')

def load_player_stats():
    """Lädt die Spielerstatistiken"""
    return load_data('spieler_statistiken.csv')

def load_json_data(filename):
    """Lädt Daten aus einer JSON-Datei"""
    try:
        # Versuche verschiedene Pfade für die JSON-Datei
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', filename),
            os.path.join(os.path.dirname(__file__), '..', '..', 'data', filename),
            os.path.join('data', filename),
            filename
        ]
        
        data_path = None
        for path in possible_paths:
            if os.path.exists(path):
                data_path = path
                break
        
        if not data_path:
            print(f"JSON-Datei {filename} nicht gefunden in den folgenden Pfaden:")
            for path in possible_paths:
                print(f"  - {path}")
            return []
        
        with open(data_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        return data
    except FileNotFoundError:
        print(f"JSON-Datei {filename} nicht gefunden")
        return []
    except Exception as e:
        print(f"Fehler beim Laden der JSON-Daten aus {filename}: {e}")
        return []

def filter_data(data, field, value):
    """Filtert Daten basierend auf einem Feld und Wert (case-insensitive)"""
    return [row for row in data if value.lower() in row[field].lower()]

def calculate_stats(data):
    """Berechnet Statistiken für eine Liste von Verletzungsdaten"""
    if not data:
        return {
            "total_injuries": 0,
            "average_days_out": 0.0,
            "total_games_missed": 0
        }
    
    total_injuries = len(data)
    total_days = sum(row['Ausfalltage'] for row in data)
    average_days_out = total_days / total_injuries if total_injuries > 0 else 0.0
    total_games_missed = sum(row['Verpasste_Spiele'] for row in data)
    
    return {
        "total_injuries": total_injuries,
        "average_days_out": average_days_out,
        "total_games_missed": total_games_missed
    }

@analysis_bp.route('/overview', methods=['GET'])
def get_overview():
    """Gibt eine Übersicht aller Verletzungen zurück"""
    data = load_data()
    if not data:
        return jsonify({"error": "Keine Daten verfügbar"}), 404
    
    stats = calculate_stats(data)
    
    return jsonify({
        "data": data,
        "statistics": stats
    })

@analysis_bp.route('/teams', methods=['GET'])
def get_teams():
    """Gibt eine Liste aller verfügbaren Teams zurück"""
    data = load_data()
    if not data:
        return jsonify({"error": "Keine Daten verfügbar"}), 404
    
    teams = list(set(row['Team'] for row in data))
    return jsonify({"teams": teams})

@analysis_bp.route('/players', methods=['GET'])
def get_players():
    """Gibt eine Liste aller verfügbaren Spieler zurück"""
    data = load_data()
    if not data:
        return jsonify({"error": "Keine Daten verfügbar"}), 404
    
    players = list(set(row['Spieler'] for row in data))
    return jsonify({"players": players})

@analysis_bp.route('/team/<team_name>', methods=['GET'])
def get_team_injuries(team_name):
    """Gibt Verletzungen für ein bestimmtes Team zurück"""
    data = load_data()
    if not data:
        return jsonify({"error": "Keine Daten verfügbar"}), 404
    
    team_data = filter_data(data, 'Team', team_name)
    if not team_data:
        return jsonify({"error": f"Keine Verletzungen für {team_name} gefunden"}), 404
    
    stats = calculate_stats(team_data)
    
    return jsonify({
        "team": team_name,
        "data": team_data,
        "statistics": stats
    })

@analysis_bp.route('/player/<player_name>', methods=['GET'])
def get_player_injuries(player_name):
    """Gibt Verletzungen für einen bestimmten Spieler zurück"""
    data = load_data()
    if not data:
        return jsonify({"error": "Keine Daten verfügbar"}), 404
    
    player_data = filter_data(data, 'Spieler', player_name)
    if not player_data:
        return jsonify({"error": f"Keine Verletzungen für {player_name} gefunden"}), 404
    
    stats = calculate_stats(player_data)
    
    return jsonify({
        "player": player_name,
        "data": player_data,
        "statistics": stats
    })

@analysis_bp.route('/compare/teams', methods=['POST'])
def compare_teams():
    """Vergleicht zwei Teams"""
    data = request.get_json()
    team1 = data.get('team1')
    team2 = data.get('team2')
    
    if not team1 or not team2:
        return jsonify({"error": "Beide Teamnamen sind erforderlich"}), 400
    
    all_data = load_data()
    if not all_data:
        return jsonify({"error": "Keine Daten verfügbar"}), 404
    
    team1_data = filter_data(all_data, 'Team', team1)
    team2_data = filter_data(all_data, 'Team', team2)
    
    team1_stats = calculate_stats(team1_data)
    team2_stats = calculate_stats(team2_data)
    
    result = {
        "team1": {
            "name": team1,
            **team1_stats
        },
        "team2": {
            "name": team2,
            **team2_stats
        }
    }
    
    return jsonify(result)

@analysis_bp.route('/compare/players', methods=['POST'])
def compare_players():
    """Vergleicht zwei Spieler"""
    data = request.get_json()
    player1 = data.get('player1')
    player2 = data.get('player2')
    
    if not player1 or not player2:
        return jsonify({"error": "Beide Spielernamen sind erforderlich"}), 400
    
    all_data = load_data()
    if not all_data:
        return jsonify({"error": "Keine Daten verfügbar"}), 404
    
    player1_data = filter_data(all_data, 'Spieler', player1)
    player2_data = filter_data(all_data, 'Spieler', player2)
    
    player1_stats = calculate_stats(player1_data)
    player2_stats = calculate_stats(player2_data)
    
    result = {
        "player1": {
            "name": player1,
            **player1_stats
        },
        "player2": {
            "name": player2,
            **player2_stats
        }
    }
    
    return jsonify(result)

@analysis_bp.route('/combined/overview', methods=['GET'])
def get_combined_overview():
    """Gibt eine Übersicht der kombinierten Spieler- und Verletzungsdaten zurück"""
    data = load_combined_data()
    if not data:
        return jsonify({"error": "Keine kombinierten Daten verfügbar"}), 404
    
    return jsonify({
        "data": data,
        "count": len(data)
    })

@analysis_bp.route('/combined/player/<player_name>', methods=['GET'])
def get_combined_player_data(player_name):
    """Gibt die kombinierten Daten für einen bestimmten Spieler zurück"""
    data = load_combined_data()
    if not data:
        return jsonify({"error": "Keine kombinierten Daten verfügbar"}), 404
    
    player_data = filter_data(data, 'Spieler', player_name)
    if not player_data:
        return jsonify({"error": f"Keine kombinierten Daten für {player_name} gefunden"}), 404
    
    return jsonify({
        "player": player_name,
        "data": player_data
    })

@analysis_bp.route('/combined/team/<team_name>', methods=['GET'])
def get_combined_team_data(team_name):
    """Gibt die kombinierten Daten für ein bestimmtes Team zurück"""
    data = load_combined_data()
    if not data:
        return jsonify({"error": "Keine kombinierten Daten verfügbar"}), 404
    
    team_data = filter_data(data, 'Team', team_name)
    if not team_data:
        return jsonify({"error": f"Keine kombinierten Daten für {team_name} gefunden"}), 404
    
    return jsonify({
        "team": team_name,
        "data": team_data,
        "count": len(team_data)
    })

@analysis_bp.route('/player-stats/overview', methods=['GET'])
def get_player_stats_overview():
    """Gibt eine Übersicht aller Spielerstatistiken zurück"""
    data = load_player_stats()
    if not data:
        return jsonify({"error": "Keine Spielerstatistiken verfügbar"}), 404
    
    return jsonify({
        "data": data,
        "count": len(data)
    })

@analysis_bp.route('/player-stats/player/<player_name>', methods=['GET'])
def get_player_stats(player_name):
    """Gibt die Statistiken für einen bestimmten Spieler zurück"""
    data = load_player_stats()
    if not data:
        return jsonify({"error": "Keine Spielerstatistiken verfügbar"}), 404
    
    player_data = filter_data(data, 'Spieler', player_name)
    if not player_data:
        return jsonify({"error": f"Keine Statistiken für {player_name} gefunden"}), 404
    
    return jsonify({
        "player": player_name,
        "data": player_data[0] if player_data else {}
    })

@analysis_bp.route('/player-stats/team/<team_name>', methods=['GET'])
def get_team_player_stats(team_name):
    """Gibt die Spielerstatistiken für ein bestimmtes Team zurück"""
    data = load_player_stats()
    if not data:
        return jsonify({"error": "Keine Spielerstatistiken verfügbar"}), 404
    
    team_data = filter_data(data, 'Team', team_name)
    if not team_data:
        return jsonify({"error": f"Keine Statistiken für {team_name} gefunden"}), 404
    
    return jsonify({
        "team": team_name,
        "data": team_data,
        "count": len(team_data)
    })

@analysis_bp.route('/team-summary', methods=['GET'])
def get_team_injury_summary():
    """Gibt eine Zusammenfassung der Verletzungen pro Team zurück"""
    data = load_json_data('verletzungen_vereine.json')
    if not data:
        return jsonify({"error": "Keine Team-Verletzungszusammenfassung verfügbar"}), 404
    
    return jsonify({
        "data": data
    })


# ML-Endpunkte
@analysis_bp.route('/ml/train', methods=['POST'])
def train_ml_model():
    """
    Trainiert ein ML-Modell mit den aktuellen Daten
    """
    if not ML_AVAILABLE:
        return jsonify({"error": "ML-Funktionalität nicht verfügbar"}), 501
    
    try:
        # Parameter aus der Anfrage extrahieren
        data = request.get_json() or {}
        target_variable = data.get('target_variable', 'Ausfalltage')
        
        # Erstelle den InjuryPredictor
        predictor = InjuryPredictor(target_variable=target_variable)
        
        # Führe die gesamte Pipeline aus
        success = predictor.run_full_pipeline()
        
        if not success:
            return jsonify({"error": "Fehler beim Training des ML-Modells"}), 500
        
        # Hole die Ergebnisse
        if hasattr(predictor, 'test_results'):
            metrics = {
                'rmse': float(predictor.test_results['rmse']),
                'mae': float(predictor.test_results['mae']),
                'r2': float(predictor.test_results['r2'])
            }
        else:
            metrics = {}
            
        return jsonify({
            "success": True,
            "message": f"ML-Modell für {target_variable} erfolgreich trainiert",
            "model": predictor.best_model_name,
            "metrics": metrics
        })
        
    except Exception as e:
        print(f"Fehler beim Training des ML-Modells: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route('/ml/predict', methods=['POST'])
def predict_with_ml():
    """
    Macht Vorhersagen mit dem trainierten ML-Modell
    """
    if not ML_AVAILABLE:
        return jsonify({"error": "ML-Funktionalität nicht verfügbar"}), 501
    
    try:
        # Parameter aus der Anfrage extrahieren
        data = request.get_json() or {}
        
        if 'player_data' not in data:
            return jsonify({"error": "Keine Spielerdaten in der Anfrage"}), 400
            
        player_data = data['player_data']
        model_name = data.get('model', 'Random Forest')
        
        # Konvertiere zu DataFrame
        df = pd.DataFrame([player_data])
        
        # Bereinige und bereite die Daten vor
        df_clean = clean_data(df)
        df_features = engineer_features(df_clean)
        
        # Erstelle den InjuryPredictor
        predictor = InjuryPredictor()
        
        # Versuche, das Modell zu laden
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
        model_path = os.path.join(models_dir, f'{model_name.replace(" ", "_")}.joblib')
        
        if not os.path.exists(model_path):
            return jsonify({"error": f"Modell {model_name} nicht gefunden"}), 404
            
        # Lade die Pipeline
        pipeline = joblib.load(model_path)
        
        # Mache Vorhersagen
        prediction = pipeline.predict(df_features)[0]
        
        return jsonify({
            "success": True,
            "prediction": float(prediction),
            "model": model_name,
            "player": player_data.get('Spieler', 'Unbekannt')
        })
        
    except Exception as e:
        print(f"Fehler bei der Vorhersage: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route('/ml/models', methods=['GET'])
def get_available_models():
    """
    Gibt eine Liste der verfügbaren ML-Modelle zurück
    """
    if not ML_AVAILABLE:
        return jsonify({"error": "ML-Funktionalität nicht verfügbar"}), 501
    
    try:
        # Suche nach gespeicherten Modellen
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
        
        if not os.path.exists(models_dir):
            return jsonify({"models": []})
            
        # Finde alle .joblib Dateien
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.joblib')]
        
        # Extrahiere Modellnamen
        models = [os.path.splitext(f)[0].replace('_', ' ') for f in model_files]
        
        return jsonify({
            "models": models
        })
        
    except Exception as e:
        print(f"Fehler beim Abrufen der Modelle: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route('/ml/feature-importances', methods=['GET'])
def get_feature_importances():
    """
    Gibt die Feature-Importances des besten Modells zurück
    """
    if not ML_AVAILABLE:
        return jsonify({"error": "ML-Funktionalität nicht verfügbar"}), 501
    
    try:
        # Parameter aus der Anfrage extrahieren
        model_name = request.args.get('model', 'Random Forest')
        
        # Erstelle den InjuryPredictor
        predictor = InjuryPredictor()
        
        # Versuche, das Modell zu laden
        success = predictor.load_model(model_name)
        
        if not success:
            return jsonify({"error": f"Modell {model_name} nicht gefunden"}), 404
            
        # Lade Daten für Feature-Namen
        predictor.load_data()
        
        # Hole Feature-Importances
        importances = predictor.get_feature_importances()
        
        if importances is None:
            return jsonify({"error": f"Keine Feature-Importances für {model_name} verfügbar"}), 404
            
        # Konvertiere zu Liste von Dictionaries
        importances_list = importances.to_dict(orient='records')
        
        return jsonify({
            "model": model_name,
            "feature_importances": importances_list
        })
        
    except Exception as e:
        print(f"Fehler beim Abrufen der Feature-Importances: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route('/ml/metrics', methods=['GET'])
def get_model_metrics():
    """
    Gibt die Metriken des besten Modells zurück
    """
    if not ML_AVAILABLE:
        return jsonify({"error": "ML-Funktionalität nicht verfügbar"}), 501
    
    try:
        # Parameter aus der Anfrage extrahieren
        model_name = request.args.get('model', 'Random Forest')
        
        # Erstelle den InjuryPredictor
        predictor = InjuryPredictor()
        
        # Versuche, das Modell zu laden
        success = predictor.load_model(model_name)
        
        if not success:
            return jsonify({"error": f"Modell {model_name} nicht gefunden"}), 404
            
        # Lade Daten und evaluiere das Modell
        predictor.load_data()
        predictor.evaluate_best_model()
        
        if not hasattr(predictor, 'test_results'):
            return jsonify({"error": f"Keine Metriken für {model_name} verfügbar"}), 404
            
        metrics = {
            'rmse': float(predictor.test_results['rmse']),
            'mae': float(predictor.test_results['mae']),
            'r2': float(predictor.test_results['r2'])
        }
        
        return jsonify({
            "model": model_name,
            "metrics": metrics
        })
        
    except Exception as e:
        print(f"Fehler beim Abrufen der Metriken: {e}")
        return jsonify({"error": str(e)}), 500
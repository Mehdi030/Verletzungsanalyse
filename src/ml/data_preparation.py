"""
Modul für die Datenaufbereitung für Machine Learning
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

def load_combined_data(filename='kombinierte_daten.csv'):
    """
    Lädt die kombinierten Spieler- und Verletzungsdaten
    """
    # Versuche verschiedene Pfade für die CSV-Datei
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', filename),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', filename),
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
        return None
    
    try:
        df = pd.read_csv(data_path, encoding='utf-8')
        print(f"Daten erfolgreich geladen: {len(df)} Einträge")
        return df
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        return None

def clean_data(df):
    """
    Bereinigt die Daten für das Machine Learning
    - Entfernt Duplikate
    - Behandelt fehlende Werte
    - Konvertiert Datentypen
    """
    if df is None or df.empty:
        print("Keine Daten zum Bereinigen vorhanden")
        return None
    
    print("Bereinige Daten...")
    
    # Kopie erstellen, um die Originaldaten nicht zu verändern
    df_clean = df.copy()
    
    # Duplikate entfernen
    initial_rows = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    print(f"Duplikate entfernt: {initial_rows - len(df_clean)} Zeilen")
    
    # Fehlende Werte behandeln
    # Für numerische Spalten: Mittelwert verwenden
    numeric_cols = df_clean.select_dtypes(include=['int64', 'float64']).columns
    for col in numeric_cols:
        if df_clean[col].isna().sum() > 0:
            print(f"Fehlende Werte in {col}: {df_clean[col].isna().sum()}")
            df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
    
    # Für kategorische Spalten: Häufigster Wert verwenden
    categorical_cols = df_clean.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df_clean[col].isna().sum() > 0:
            print(f"Fehlende Werte in {col}: {df_clean[col].isna().sum()}")
            df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0])
    
    # Datentypen konvertieren
    # Stelle sicher, dass numerische Spalten auch wirklich numerisch sind
    for col in ['Ausfalltage', 'Verpasste_Spiele', 'Alter', 'Spiele', 'Startelf', 'Minuten', 'Tore', 'Assists']:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            df_clean[col] = df_clean[col].fillna(0)
    
    print(f"Daten bereinigt: {len(df_clean)} Einträge")
    return df_clean

def engineer_features(df):
    """
    Feature Engineering für die Verletzungsdaten
    - Erstellt neue Features aus den vorhandenen Daten
    - Transformiert kategorische Variablen
    """
    if df is None or df.empty:
        print("Keine Daten für Feature Engineering vorhanden")
        return None
    
    print("Führe Feature Engineering durch...")
    
    # Kopie erstellen, um die Originaldaten nicht zu verändern
    df_features = df.copy()
    
    # Neue Features erstellen
    
    # 1. Spielzeit-Intensität: Minuten pro Spiel
    if 'Minuten' in df_features.columns and 'Spiele' in df_features.columns:
        df_features['Minuten_pro_Spiel'] = df_features['Minuten'] / df_features['Spiele'].replace(0, 1)
    
    # 2. Torbeteiligung: Tore + Assists
    if 'Tore' in df_features.columns and 'Assists' in df_features.columns:
        df_features['Torbeteiligung'] = df_features['Tore'] + df_features['Assists']
    
    # 3. Torbeteiligung pro Spiel
    if 'Torbeteiligung' in df_features.columns and 'Spiele' in df_features.columns:
        df_features['Torbeteiligung_pro_Spiel'] = df_features['Torbeteiligung'] / df_features['Spiele'].replace(0, 1)
    
    # 4. Startelf-Quote: Anteil der Spiele in der Startelf
    if 'Startelf' in df_features.columns and 'Spiele' in df_features.columns:
        df_features['Startelf_Quote'] = df_features['Startelf'] / df_features['Spiele'].replace(0, 1)
    
    # 5. Verletzungsintensität: Ausfalltage pro Verletzung
    if 'Ausfalltage' in df_features.columns and 'Verpasste_Spiele' in df_features.columns:
        # Wenn Ausfalltage > 0, aber Verpasste_Spiele = 0, setze Verpasste_Spiele = 1
        mask = (df_features['Ausfalltage'] > 0) & (df_features['Verpasste_Spiele'] == 0)
        df_features.loc[mask, 'Verpasste_Spiele'] = 1
        
        df_features['Verletzungsintensität'] = df_features['Ausfalltage'] / df_features['Verpasste_Spiele'].replace(0, 1)
    
    # 6. Positionskategorien erstellen (falls Position vorhanden)
    if 'Position' in df_features.columns:
        # Vereinfachte Positionskategorien
        def categorize_position(pos):
            pos = str(pos).lower()
            if 'torwart' in pos or 'keeper' in pos or 'tw' in pos:
                return 'Torwart'
            elif 'verteidiger' in pos or 'abwehr' in pos or 'defender' in pos:
                return 'Verteidiger'
            elif 'mittelfeld' in pos or 'midfielder' in pos:
                return 'Mittelfeld'
            elif 'stürmer' in pos or 'angriff' in pos or 'forward' in pos:
                return 'Stürmer'
            else:
                return 'Sonstige'
        
        df_features['Positionskategorie'] = df_features['Position'].apply(categorize_position)
    
    # 7. Altersgruppen erstellen
    if 'Alter' in df_features.columns:
        bins = [0, 20, 25, 30, 35, 100]
        labels = ['U20', '20-25', '25-30', '30-35', '35+']
        df_features['Altersgruppe'] = pd.cut(df_features['Alter'], bins=bins, labels=labels, right=False)
    
    # 8. Verletzungstyp-Kategorien (falls vorhanden)
    if 'Verletzungstyp' in df_features.columns:
        # Vereinfachte Verletzungskategorien
        def categorize_injury(injury):
            injury = str(injury).lower()
            if 'muskel' in injury or 'faser' in injury or 'zerrung' in injury:
                return 'Muskulär'
            elif 'knie' in injury or 'kreuzband' in injury or 'meniskus' in injury:
                return 'Knie'
            elif 'sprunggelenk' in injury or 'knöchel' in injury or 'ankle' in injury:
                return 'Sprunggelenk'
            elif 'schulter' in injury or 'arm' in injury or 'hand' in injury:
                return 'Oberkörper'
            elif 'kopf' in injury or 'gehirn' in injury or 'concussion' in injury:
                return 'Kopf'
            elif 'keine verletzung' in injury:
                return 'Keine'
            else:
                return 'Sonstige'
        
        df_features['Verletzungskategorie'] = df_features['Verletzungstyp'].apply(categorize_injury)
    
    print(f"Feature Engineering abgeschlossen: {len(df_features.columns)} Features")
    return df_features

def prepare_data_for_ml(df, target_variable='Ausfalltage', test_size=0.2, val_size=0.25):
    """
    Bereitet die Daten für das Machine Learning vor
    - Teilt die Daten in Trainings-, Validierungs- und Testsets
    - Erstellt Feature-Pipelines für numerische und kategorische Variablen
    - Transformiert die Daten
    
    Returns:
        X_train, X_val, X_test, y_train, y_val, y_test, preprocessor
    """
    if df is None or df.empty:
        print("Keine Daten für ML-Vorbereitung vorhanden")
        return None, None, None, None, None, None, None
    
    print("Bereite Daten für Machine Learning vor...")
    
    # Kopie erstellen, um die Originaldaten nicht zu verändern
    df_ml = df.copy()
    
    # Zielgröße und Features trennen
    if target_variable not in df_ml.columns:
        print(f"Zielgröße {target_variable} nicht in den Daten vorhanden")
        return None, None, None, None, None, None, None
    
    # Entferne Spalten, die nicht für das Training verwendet werden sollen
    columns_to_drop = ['Spieler', 'Team', 'Spieler_URL', 'Verletzungsdatum', 'Rueckkehr_erwartet']
    columns_to_drop = [col for col in columns_to_drop if col in df_ml.columns]
    
    X = df_ml.drop(columns=[target_variable] + columns_to_drop)
    y = df_ml[target_variable]
    
    # Identifiziere numerische und kategorische Features
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    print(f"Numerische Features: {len(numeric_features)}")
    print(f"Kategorische Features: {len(categorical_features)}")
    
    # Erstelle Preprocessing-Pipeline
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # Teile die Daten in Trainings- und Testset
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=test_size, random_state=42)
    
    # Teile das temporäre Set in Validierungs- und Testset
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
    
    print(f"Trainingsdaten: {X_train.shape[0]} Einträge")
    print(f"Validierungsdaten: {X_val.shape[0]} Einträge")
    print(f"Testdaten: {X_test.shape[0]} Einträge")
    
    return X_train, X_val, X_test, y_train, y_val, y_test, preprocessor

def get_processed_data(target_variable='Ausfalltage'):
    """
    Führt den gesamten Datenvorbereitungsprozess durch und gibt die verarbeiteten Daten zurück
    """
    # Daten laden
    df = load_combined_data()
    
    # Daten bereinigen
    df_clean = clean_data(df)
    
    # Feature Engineering
    df_features = engineer_features(df_clean)
    
    # Daten für ML vorbereiten
    X_train, X_val, X_test, y_train, y_val, y_test, preprocessor = prepare_data_for_ml(df_features, target_variable)
    
    return X_train, X_val, X_test, y_train, y_val, y_test, preprocessor, df_features

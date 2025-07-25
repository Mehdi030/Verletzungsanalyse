"""
Modul für Machine Learning Modelle zur Verletzungsvorhersage
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV, learning_curve
from sklearn.pipeline import Pipeline

# Lokale Importe
from src.ml.data_preparation import get_processed_data

class InjuryPredictor:
    """
    Klasse für die Vorhersage von Verletzungen mit verschiedenen ML-Modellen
    """
    
    def __init__(self, target_variable='Ausfalltage', models_dir=None):
        """
        Initialisiert den InjuryPredictor
        
        Args:
            target_variable: Die Zielvariable für die Vorhersage (Standard: 'Ausfalltage')
            models_dir: Verzeichnis zum Speichern der trainierten Modelle
        """
        self.target_variable = target_variable
        
        if models_dir is None:
            self.models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
        else:
            self.models_dir = models_dir
            
        # Stelle sicher, dass das Verzeichnis existiert
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Initialisiere Attribute
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        self.preprocessor = None
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.feature_importances = None
        
    def load_data(self):
        """
        Lädt die vorbereiteten Daten für das Training
        """
        print(f"Lade Daten für Zielgröße: {self.target_variable}")
        
        # Verwende die Funktion aus data_preparation.py
        self.X_train, self.X_val, self.X_test, self.y_train, self.y_val, self.y_test, self.preprocessor, self.df_features = get_processed_data(self.target_variable)
        
        if self.X_train is None:
            print("Fehler beim Laden der Daten")
            return False
            
        print(f"Daten erfolgreich geladen: {self.X_train.shape[0]} Trainingsbeispiele, {self.X_val.shape[0]} Validierungsbeispiele, {self.X_test.shape[0]} Testbeispiele")
        return True
        
    def initialize_models(self):
        """
        Initialisiert verschiedene ML-Modelle für den Vergleich
        """
        print("Initialisiere Modelle...")
        
        # Definiere verschiedene Modelle
        self.models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(),
            'Lasso Regression': Lasso(),
            'Elastic Net': ElasticNet(),
            'Random Forest': RandomForestRegressor(random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(random_state=42),
            'SVR': SVR(),
            'KNN': KNeighborsRegressor(),
            'Neural Network': MLPRegressor(random_state=42, max_iter=1000)
        }
        
        print(f"{len(self.models)} Modelle initialisiert")
        
    def train_models(self):
        """
        Trainiert alle initialisierten Modelle
        """
        if self.X_train is None or self.y_train is None:
            print("Keine Trainingsdaten vorhanden. Bitte zuerst load_data() aufrufen.")
            return False
            
        if not self.models:
            self.initialize_models()
            
        print("Trainiere Modelle...")
        
        # Transformiere die Trainingsdaten
        X_train_transformed = self.preprocessor.fit_transform(self.X_train)
        X_val_transformed = self.preprocessor.transform(self.X_val)
        
        # Trainiere jedes Modell und evaluiere es
        results = {}
        
        for name, model in self.models.items():
            print(f"Trainiere {name}...")
            
            # Trainiere das Modell
            model.fit(X_train_transformed, self.y_train)
            
            # Evaluiere auf Validierungsdaten
            y_val_pred = model.predict(X_val_transformed)
            
            # Berechne Metriken
            mse = mean_squared_error(self.y_val, y_val_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(self.y_val, y_val_pred)
            r2 = r2_score(self.y_val, y_val_pred)
            
            results[name] = {
                'model': model,
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            }
            
            print(f"  {name}: RMSE = {rmse:.2f}, MAE = {mae:.2f}, R² = {r2:.2f}")
            
        # Finde das beste Modell basierend auf RMSE
        self.best_model_name = min(results, key=lambda x: results[x]['rmse'])
        self.best_model = results[self.best_model_name]['model']
        
        print(f"\nBestes Modell: {self.best_model_name}")
        print(f"  RMSE = {results[self.best_model_name]['rmse']:.2f}")
        print(f"  MAE = {results[self.best_model_name]['mae']:.2f}")
        print(f"  R² = {results[self.best_model_name]['r2']:.2f}")
        
        # Speichere die Ergebnisse
        self.results = results
        
        return True
        
    def optimize_hyperparameters(self, model_name=None):
        """
        Optimiert die Hyperparameter für ein bestimmtes Modell oder das beste Modell
        """
        if self.X_train is None or self.y_train is None:
            print("Keine Trainingsdaten vorhanden. Bitte zuerst load_data() aufrufen.")
            return False
            
        if not self.models:
            print("Keine Modelle initialisiert. Bitte zuerst initialize_models() aufrufen.")
            return False
            
        # Wenn kein Modellname angegeben wurde, verwende das beste Modell
        if model_name is None:
            if self.best_model_name is None:
                print("Kein bestes Modell gefunden. Bitte zuerst train_models() aufrufen.")
                return False
            model_name = self.best_model_name
            
        print(f"Optimiere Hyperparameter für {model_name}...")
        
        # Definiere Hyperparameter-Grids für verschiedene Modelle
        param_grids = {
            'Linear Regression': {},  # Keine Hyperparameter
            'Ridge Regression': {
                'alpha': [0.01, 0.1, 1.0, 10.0, 100.0]
            },
            'Lasso Regression': {
                'alpha': [0.001, 0.01, 0.1, 1.0, 10.0]
            },
            'Elastic Net': {
                'alpha': [0.001, 0.01, 0.1, 1.0],
                'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9]
            },
            'Random Forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10]
            },
            'Gradient Boosting': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            'SVR': {
                'C': [0.1, 1, 10],
                'gamma': ['scale', 'auto', 0.1, 1],
                'kernel': ['linear', 'rbf']
            },
            'KNN': {
                'n_neighbors': [3, 5, 7, 9, 11],
                'weights': ['uniform', 'distance'],
                'p': [1, 2]
            },
            'Neural Network': {
                'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)],
                'alpha': [0.0001, 0.001, 0.01],
                'learning_rate': ['constant', 'adaptive']
            }
        }
        
        if model_name not in param_grids:
            print(f"Keine Hyperparameter-Grid für {model_name} definiert.")
            return False
            
        # Transformiere die Trainingsdaten
        X_train_transformed = self.preprocessor.fit_transform(self.X_train)
        X_val_transformed = self.preprocessor.transform(self.X_val)
        
        # Kombiniere Trainings- und Validierungsdaten für die Hyperparameter-Optimierung
        X_combined = np.vstack((X_train_transformed, X_val_transformed))
        y_combined = np.concatenate((self.y_train, self.y_val))
        
        # Erstelle GridSearchCV
        grid_search = GridSearchCV(
            estimator=self.models[model_name],
            param_grid=param_grids[model_name],
            scoring='neg_root_mean_squared_error',
            cv=5,
            n_jobs=-1,
            verbose=1
        )
        
        # Führe die Suche durch
        grid_search.fit(X_combined, y_combined)
        
        # Aktualisiere das Modell mit den besten Parametern
        self.models[model_name] = grid_search.best_estimator_
        
        print(f"Beste Parameter für {model_name}:")
        for param, value in grid_search.best_params_.items():
            print(f"  {param}: {value}")
            
        print(f"Bester RMSE: {-grid_search.best_score_:.2f}")
        
        # Wenn das optimierte Modell das beste Modell ist, aktualisiere es
        if model_name == self.best_model_name:
            self.best_model = grid_search.best_estimator_
            
        return True
        
    def evaluate_best_model(self):
        """
        Evaluiert das beste Modell auf den Testdaten
        """
        if self.X_test is None or self.y_test is None:
            print("Keine Testdaten vorhanden. Bitte zuerst load_data() aufrufen.")
            return False
            
        if self.best_model is None:
            print("Kein bestes Modell gefunden. Bitte zuerst train_models() aufrufen.")
            return False
            
        print(f"Evaluiere bestes Modell ({self.best_model_name}) auf Testdaten...")
        
        # Transformiere die Testdaten
        X_test_transformed = self.preprocessor.transform(self.X_test)
        
        # Mache Vorhersagen
        y_test_pred = self.best_model.predict(X_test_transformed)
        
        # Berechne Metriken
        mse = mean_squared_error(self.y_test, y_test_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(self.y_test, y_test_pred)
        r2 = r2_score(self.y_test, y_test_pred)
        
        print(f"Testdaten-Metriken:")
        print(f"  RMSE = {rmse:.2f}")
        print(f"  MAE = {mae:.2f}")
        print(f"  R² = {r2:.2f}")
        
        # Speichere die Testergebnisse
        self.test_results = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'y_true': self.y_test,
            'y_pred': y_test_pred
        }
        
        return True
        
    def plot_learning_curves(self, model_name=None):
        """
        Zeichnet Lernkurven für ein bestimmtes Modell oder das beste Modell
        """
        if self.X_train is None or self.y_train is None:
            print("Keine Trainingsdaten vorhanden. Bitte zuerst load_data() aufrufen.")
            return False
            
        if not self.models:
            print("Keine Modelle initialisiert. Bitte zuerst initialize_models() aufrufen.")
            return False
            
        # Wenn kein Modellname angegeben wurde, verwende das beste Modell
        if model_name is None:
            if self.best_model_name is None:
                print("Kein bestes Modell gefunden. Bitte zuerst train_models() aufrufen.")
                return False
            model_name = self.best_model_name
            
        print(f"Zeichne Lernkurven für {model_name}...")
        
        # Erstelle eine Pipeline mit dem Preprocessor und dem Modell
        pipeline = Pipeline([
            ('preprocessor', self.preprocessor),
            ('model', self.models[model_name])
        ])
        
        # Berechne die Lernkurven
        train_sizes, train_scores, val_scores = learning_curve(
            pipeline, self.X_train, self.y_train,
            train_sizes=np.linspace(0.1, 1.0, 10),
            cv=5, scoring='neg_root_mean_squared_error',
            n_jobs=-1, random_state=42
        )
        
        # Berechne Mittelwert und Standardabweichung
        train_mean = -np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        val_mean = -np.mean(val_scores, axis=1)
        val_std = np.std(val_scores, axis=1)
        
        # Erstelle den Plot
        plt.figure(figsize=(10, 6))
        plt.title(f'Lernkurven für {model_name}')
        plt.xlabel('Trainingsdaten-Größe')
        plt.ylabel('RMSE')
        plt.grid()
        
        plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color='blue')
        plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1, color='orange')
        plt.plot(train_sizes, train_mean, 'o-', color='blue', label='Training')
        plt.plot(train_sizes, val_mean, 'o-', color='orange', label='Validierung')
        
        plt.legend(loc='best')
        
        # Speichere den Plot
        plots_dir = os.path.join(self.models_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        plt.savefig(os.path.join(plots_dir, f'learning_curve_{model_name.replace(" ", "_")}.png'))
        
        # Zeige den Plot
        plt.close()
        
        print(f"Lernkurven für {model_name} gespeichert")
        
        # Analysiere Overfitting/Underfitting
        gap = val_mean[-1] - train_mean[-1]
        
        if gap > 0.5 * val_mean[-1]:
            print(f"Overfitting erkannt: Die Validierungskurve liegt deutlich über der Trainingskurve (Gap: {gap:.2f})")
        elif train_mean[-1] > 0.9 * val_mean[-1]:
            print(f"Underfitting erkannt: Beide Kurven sind hoch und liegen nah beieinander (Train RMSE: {train_mean[-1]:.2f}, Val RMSE: {val_mean[-1]:.2f})")
        else:
            print(f"Gute Generalisierung: Die Kurven konvergieren mit angemessenem Abstand (Train RMSE: {train_mean[-1]:.2f}, Val RMSE: {val_mean[-1]:.2f})")
            
        return True
        
    def save_model(self, model_name=None):
        """
        Speichert ein trainiertes Modell
        """
        if not self.models:
            print("Keine Modelle initialisiert. Bitte zuerst initialize_models() aufrufen.")
            return False
            
        # Wenn kein Modellname angegeben wurde, verwende das beste Modell
        if model_name is None:
            if self.best_model_name is None:
                print("Kein bestes Modell gefunden. Bitte zuerst train_models() aufrufen.")
                return False
            model_name = self.best_model_name
            model = self.best_model
        else:
            if model_name not in self.models:
                print(f"Modell {model_name} nicht gefunden.")
                return False
            model = self.models[model_name]
            
        print(f"Speichere Modell {model_name}...")
        
        # Erstelle eine Pipeline mit dem Preprocessor und dem Modell
        pipeline = Pipeline([
            ('preprocessor', self.preprocessor),
            ('model', model)
        ])
        
        # Speichere die Pipeline
        model_path = os.path.join(self.models_dir, f'{model_name.replace(" ", "_")}.joblib')
        joblib.dump(pipeline, model_path)
        
        print(f"Modell gespeichert unter {model_path}")
        
        return True
        
    def load_model(self, model_name):
        """
        Lädt ein gespeichertes Modell
        """
        model_path = os.path.join(self.models_dir, f'{model_name.replace(" ", "_")}.joblib')
        
        if not os.path.exists(model_path):
            print(f"Modell {model_name} nicht gefunden unter {model_path}.")
            return False
            
        print(f"Lade Modell {model_name}...")
        
        # Lade die Pipeline
        pipeline = joblib.load(model_path)
        
        # Extrahiere Preprocessor und Modell
        self.preprocessor = pipeline.named_steps['preprocessor']
        model = pipeline.named_steps['model']
        
        # Aktualisiere das Modell
        self.models[model_name] = model
        self.best_model = model
        self.best_model_name = model_name
        
        print(f"Modell {model_name} erfolgreich geladen")
        
        return True
        
    def predict(self, data):
        """
        Macht Vorhersagen mit dem besten Modell
        
        Args:
            data: DataFrame mit den Eingabedaten
            
        Returns:
            Vorhersagen
        """
        if self.best_model is None:
            print("Kein bestes Modell gefunden. Bitte zuerst train_models() aufrufen.")
            return None
            
        if self.preprocessor is None:
            print("Kein Preprocessor gefunden. Bitte zuerst load_data() aufrufen.")
            return None
            
        print("Mache Vorhersagen...")
        
        # Transformiere die Daten
        X_transformed = self.preprocessor.transform(data)
        
        # Mache Vorhersagen
        predictions = self.best_model.predict(X_transformed)
        
        return predictions
        
    def get_feature_importances(self):
        """
        Extrahiert Feature-Importances aus dem besten Modell (falls verfügbar)
        """
        if self.best_model is None:
            print("Kein bestes Modell gefunden. Bitte zuerst train_models() aufrufen.")
            return None
            
        # Prüfe, ob das Modell Feature-Importances hat
        if hasattr(self.best_model, 'feature_importances_'):
            # Für Tree-basierte Modelle
            importances = self.best_model.feature_importances_
        elif hasattr(self.best_model, 'coef_'):
            # Für lineare Modelle
            importances = np.abs(self.best_model.coef_)
        else:
            print(f"Das Modell {self.best_model_name} unterstützt keine Feature-Importances.")
            return None
            
        # Hole die Feature-Namen
        feature_names = self.X_train.columns.tolist()
        
        # Erstelle ein DataFrame mit den Importances
        feature_importances = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        })
        
        # Sortiere nach Importance
        feature_importances = feature_importances.sort_values('Importance', ascending=False)
        
        self.feature_importances = feature_importances
        
        return feature_importances
        
    def plot_feature_importances(self):
        """
        Zeichnet ein Diagramm der Feature-Importances
        """
        if self.feature_importances is None:
            self.get_feature_importances()
            
        if self.feature_importances is None:
            return False
            
        # Erstelle den Plot
        plt.figure(figsize=(12, 8))
        sns.barplot(x='Importance', y='Feature', data=self.feature_importances.head(20))
        plt.title(f'Top 20 Feature Importances für {self.best_model_name}')
        plt.tight_layout()
        
        # Speichere den Plot
        plots_dir = os.path.join(self.models_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        plt.savefig(os.path.join(plots_dir, 'feature_importances.png'))
        
        # Zeige den Plot
        plt.close()
        
        print("Feature Importances gespeichert")
        
        return True
        
    def run_full_pipeline(self):
        """
        Führt die gesamte ML-Pipeline aus
        """
        print("Starte ML-Pipeline...")
        
        # Lade die Daten
        if not self.load_data():
            return False
            
        # Initialisiere die Modelle
        self.initialize_models()
        
        # Trainiere die Modelle
        if not self.train_models():
            return False
            
        # Optimiere die Hyperparameter für das beste Modell
        if not self.optimize_hyperparameters():
            return False
            
        # Evaluiere das beste Modell
        if not self.evaluate_best_model():
            return False
            
        # Zeichne Lernkurven
        if not self.plot_learning_curves():
            return False
            
        # Extrahiere Feature-Importances
        self.get_feature_importances()
        
        # Zeichne Feature-Importances
        self.plot_feature_importances()
        
        # Speichere das beste Modell
        if not self.save_model():
            return False
            
        print("ML-Pipeline erfolgreich abgeschlossen")
        
        return True


def main():
    """
    Hauptfunktion zum Ausführen der ML-Pipeline
    """
    print("=" * 50)
    print("Verletzungsvorhersage mit Machine Learning")
    print("=" * 50)
    
    # Erstelle den InjuryPredictor
    predictor = InjuryPredictor(target_variable='Ausfalltage')
    
    # Führe die gesamte Pipeline aus
    predictor.run_full_pipeline()
    
    print("\nFertig!")


if __name__ == "__main__":
    main()
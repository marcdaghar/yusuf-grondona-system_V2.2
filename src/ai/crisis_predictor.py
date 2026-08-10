"""
Crisis Predictor – Système d'alerte précoce
===========================================

Prédit les crises économiques/monétaires sur la base de :
- Score ESG
- Ratio dette/PIB
- Entropie logistique
- Inflation
- Chômage

Utilise un Random Forest Classifier pour la prédiction.

License: CC BY-SA 4.0 – Marc Daghar
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')


class CrisisPredictor:
    """
    Prédicteur de crises économiques
    """

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            max_depth=10,
            min_samples_split=5
        )
        self.scaler = StandardScaler()
        self.is_trained = False

        self.feature_names = [
            'esg_global',
            'debt_to_gdp',
            'logistics_entropy',
            'inflation',
            'unemployment',
            'gdp_growth',
            'fulus_velocity',
            'nuqud_reserve_ratio'
        ]

        self.thresholds = {
            'esg_critical': 40,
            'debt_to_gdp_critical': 1.2,
            'logistics_entropy_critical': 0.8,
            'inflation_critical': 0.15,
            'unemployment_critical': 0.12
        }

    def extract_features(self, metrics_history: List[Dict]) -> pd.DataFrame:
        """
        Extrait les features à partir de l'historique des métriques
        """
        df = pd.DataFrame(metrics_history)

        # S'assurer que toutes les colonnes existent
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0

        return df[self.feature_names]

    def train(self, metrics_history: List[Dict],
              labels: List[int],
              test_size: float = 0.2) -> Dict:
        """
        Entraîne le modèle

        Args:
            metrics_history: Historique des métriques
            labels: 0 = pas de crise, 1 = crise imminente (dans les 30 jours)
            test_size: Proportion de données de test

        Returns:
            Dict avec les métriques d'évaluation
        """
        X = self.extract_features(metrics_history)
        y = np.array(labels)

        X_scaled = self.scaler.fit_transform(X)

        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42
        )

        # Entraînement
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Évaluation
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'n_samples': len(X),
            'n_features': len(self.feature_names)
        }

    def train_on_synthetic(self, n_samples: int = 1000) -> Dict:
        """
        Entraîne sur des données synthétiques pour la démonstration
        """
        np.random.seed(42)

        X = np.random.rand(n_samples, len(self.feature_names))
        # Création de labels artificiels
        # Une crise est plus probable quand l'ESG est bas, la dette élevée, etc.
        crisis_score = (
            (1 - X[:, 0]) * 0.3 +  # esg_global (0-1)
            X[:, 1] * 0.3 +          # debt_to_gdp (0-1)
            X[:, 2] * 0.2 +          # logistics_entropy (0-1)
            X[:, 3] * 0.1 +          # inflation (0-1)
            X[:, 4] * 0.1            # unemployment (0-1)
        )
        y = (crisis_score > 0.6).astype(int)

        # Création de l'historique
        history = []
        for i in range(n_samples):
            history.append({
                'esg_global': X[i, 0] * 100,
                'debt_to_gdp': X[i, 1] * 2.0,
                'logistics_entropy': X[i, 2] * 2.0,
                'inflation': X[i, 3] * 0.3,
                'unemployment': X[i, 4] * 0.2,
                'gdp_growth': X[i, 5] * 0.2 - 0.1,
                'fulus_velocity': X[i, 6] * 5,
                'nuqud_reserve_ratio': X[i, 7] * 0.5
            })

        return self.train(history, y)

    def predict(self, current_metrics: Dict) -> Dict:
        """
        Prédit le risque de crise dans les 30 jours

        Args:
            current_metrics: Métriques actuelles

        Returns:
            Dict avec la probabilité et le niveau de risque
        """
        if not self.is_trained:
            return {
                'error': "Model not trained",
                'risk_probability': 0.5,
                'risk_level': 'inconnu'
            }

        # Extraction des features
        features = pd.DataFrame([current_metrics])[self.feature_names]
        features = features.fillna(0)

        # Normalisation
        features_scaled = self.scaler.transform(features)

        # Prédiction
        proba = self.model.predict_proba(features_scaled)[0][1]

        # Niveau de risque
        if proba > 0.7:
            risk_level = "CRITIQUE"
        elif proba > 0.4:
            risk_level = "ÉLEVÉ"
        elif proba > 0.2:
            risk_level = "MOYEN"
        else:
            risk_level = "FAIBLE"

        # Alertes spécifiques
        alerts = []
        for key, threshold in self.thresholds.items():
            if key in current_metrics:
                value = current_metrics[key]
                if key == 'esg_global' and value < threshold:
                    alerts.append(f"ESG critique ({value:.1f} < {threshold})")
                elif key == 'debt_to_gdp' and value > threshold:
                    alerts.append(f"Dette/PIB excessive ({value:.2f} > {threshold})")
                elif key == 'logistics_entropy' and value > threshold:
                    alerts.append(f"Entropie logistique élevée ({value:.2f} > {threshold})")
                elif key == 'inflation' and value > threshold:
                    alerts.append(f"Inflation élevée ({value:.1%} > {threshold:.0%})")
                elif key == 'unemployment' and value > threshold:
                    alerts.append(f"Chômage élevé ({value:.1%} > {threshold:.0%})")

        # Recommandation
        if proba > 0.7:
            recommendation = "Déclencher CRD, libérer stocks, préparer Zakat d'urgence, renforcer les inspections"
        elif proba > 0.4:
            recommendation = "Surveillance renforcée – inspections muhtassib hebdomadaires, préparer plans de contingence"
        elif proba > 0.2:
            recommendation = "Veille normale – surveillance des indicateurs clés"
        else:
            recommendation = "Situation stable – simulation continue"

        return {
            'risk_probability': float(proba),
            'risk_level': risk_level,
            'alerts': alerts,
            'recommendation': recommendation,
            'feature_importance': self._get_feature_importance()
        }

    def _get_feature_importance(self) -> Dict:
        """
        Retourne l'importance des features
        """
        if not self.is_trained:
            return {}

        importance = self.model.feature_importances_
        return {
            name: float(imp)
            for name, imp in zip(self.feature_names, importance)
        }


class EarlyWarningSystem:
    """
    Système d'alerte précoce complet
    """

    def __init__(self):
        self.predictor = CrisisPredictor()
        self.history: List[Dict] = []
        self.alerts: List[Dict] = []

    def add_metrics(self, metrics: Dict) -> None:
        """
        Ajoute des métriques à l'historique
        """
        self.history.append(metrics)

    def train(self) -> Dict:
        """
        Entraîne le prédicteur sur l'historique
        """
        if len(self.history) < 10:
            return {'error': 'Pas assez de données'}

        # Génération de labels synthétiques (pour démonstration)
        labels = []
        for i, m in enumerate(self.history):
            # Une crise est plus probable après une baisse de l'ESG
            if i > 5:
                esg_decline = self.history[i-5].get('esg_global', 50) - m.get('esg_global', 50)
                if esg_decline > 10:
                    labels.append(1)
                    continue
            labels.append(0)

        return self.predictor.train(self.history, labels)

    def check_current(self, current_metrics: Dict) -> Dict:
        """
        Vérifie les métriques actuelles et génère des alertes
        """
        # Ajout aux historiques
        self.add_metrics(current_metrics)

        # Prédiction
        result = self.predictor.predict(current_metrics)

        # Enregistrement des alertes
        if result.get('risk_probability', 0) > 0.4:
            alert = {
                'timestamp': pd.Timestamp.now(),
                'risk_level': result.get('risk_level'),
                'probability': result.get('risk_probability'),
                'alerts': result.get('alerts', []),
                'recommendation': result.get('recommendation')
            }
            self.alerts.append(alert)

        return result

    def get_summary(self) -> Dict:
        """
        Résumé du système d'alerte
        """
        return {
            'total_metrics': len(self.history),
            'total_alerts': len(self.alerts),
            'last_alert': self.alerts[-1] if self.alerts else None,
            'is_trained': self.predictor.is_trained
        }


# Exemple d'utilisation
if __name__ == "__main__":
    # Création du système d'alerte
    warning_system = EarlyWarningSystem()

    # Entraînement sur données synthétiques
    warning_system.predictor.train_on_synthetic(n_samples=500)

    print("=== SYSTÈME D'ALERTE PRÉCOCE ===")

    # Simulation de métriques normales
    normal_metrics = {
        'esg_global': 65,
        'debt_to_gdp': 0.7,
        'logistics_entropy': 0.4,
        'inflation': 0.03,
        'unemployment': 0.07,
        'gdp_growth': 0.02,
        'fulus_velocity': 3.5,
        'nuqud_reserve_ratio': 0.4
    }

    result = warning_system.check_current(normal_metrics)
    print("\nMétriques normales:")
    print(f"  Risque: {result['risk_level']} ({result['risk_probability']:.1%})")

    # Simulation de métriques critiques
    crisis_metrics = {
        'esg_global': 35,
        'debt_to_gdp': 1.4,
        'logistics_entropy': 0.9,
        'inflation': 0.18,
        'unemployment': 0.15,
        'gdp_growth': -0.05,
        'fulus_velocity': 1.2,
        'nuqud_reserve_ratio': 0.1
    }

    result = warning_system.check_current(crisis_metrics)
    print("\nMétriques critiques:")
    print(f"  Risque: {result['risk_level']} ({result['risk_probability']:.1%})")
    print(f"  Alertes: {result['alerts']}")
    print(f"  Recommandation: {result['recommendation']}")

    print(f"\nRésumé: {warning_system.get_summary()}")

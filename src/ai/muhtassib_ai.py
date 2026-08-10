"""
Muhtassib AI – Assistant du muhtassib
=====================================

L'IA assiste le muhtassib dans :
- La détection d'anomalies dans les transactions
- La suggestion d'inspections
- L'analyse des tendances de fraude

L'IA ne prend PAS de décision à la place du muhtassib.
Elle fournit des alertes et des recommandations.

License: CC BY-SA 4.0 – Marc Daghar
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import time


class AnomalyDetector:
    """
    Détecteur d'anomalies basé sur Isolation Forest
    """

    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        """
        Args:
            contamination: Proportion attendue d'anomalies (0-1)
            random_state: Graine aléatoire pour reproductibilité
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.trained = False
        self.history: List[Dict] = []

    def add_transaction(self,
                        price: float,
                        weight: float,
                        delay_days: float,
                        halal_cert_ok: int,
                        quantity: float = 1.0) -> None:
        """
        Ajoute une transaction à l'historique
        """
        self.history.append({
            "price": price,
            "weight": weight,
            "delay": delay_days,
            "halal": 1 if halal_cert_ok else 0,
            "quantity": quantity,
            "timestamp": time.time()
        })

    def train(self) -> bool:
        """
        Entraîne le modèle sur l'historique des transactions
        """
        if len(self.history) < 10:
            return False

        X = np.array([
            [t["price"], t["weight"], t["delay"], t["halal"], t["quantity"]]
            for t in self.history
        ])

        # Normalisation
        X_scaled = self.scaler.fit_transform(X)

        # Entraînement
        self.model.fit(X_scaled)
        self.trained = True
        return True

    def anomaly_score(self, transaction: Dict) -> float:
        """
        Calcule un score d'anomalie pour une transaction (0-1)
        0 = normal, 1 = très anormal
        """
        if not self.trained:
            return 0.5

        X = np.array([[
            transaction.get("price", 0),
            transaction.get("weight", 0),
            transaction.get("delay", 0),
            1 if transaction.get("halal", False) else 0,
            transaction.get("quantity", 1)
        ]])

        X_scaled = self.scaler.transform(X)
        score = self.model.score_samples(X_scaled)[0]

        # Normalisation : score < 0 = anomalie
        # On convertit en 0-1 où 1 = très anormal
        normalized = max(0, min(1, -score / 0.5))
        return normalized

    def get_suspicious_fields(self, transaction: Dict) -> List[str]:
        """
        Identifie les champs suspects dans une transaction
        """
        fields = []
        thresholds = self._get_thresholds()

        price = transaction.get("price", 0)
        if price > thresholds.get("price_high", float('inf')):
            fields.append("price_anormalement_élevé")
        if price < thresholds.get("price_low", 0):
            fields.append("price_anormalement_bas")

        weight = transaction.get("weight", 0)
        if weight > thresholds.get("weight_high", float('inf')):
            fields.append("poids_anormal")

        delay = transaction.get("delay", 0)
        if delay > thresholds.get("delay_high", float('inf')):
            fields.append("délai_anormal")

        if not transaction.get("halal", False):
            fields.append("certificat_halal_manquant")

        return fields

    def _get_thresholds(self) -> Dict:
        """
        Calcule les seuils à partir de l'historique
        """
        if len(self.history) < 10:
            return {
                "price_high": 100,
                "price_low": 0.01,
                "weight_high": 1000,
                "delay_high": 30
            }

        prices = [t["price"] for t in self.history]
        weights = [t["weight"] for t in self.history]
        delays = [t["delay"] for t in self.history]

        return {
            "price_high": np.percentile(prices, 95),
            "price_low": np.percentile(prices, 5),
            "weight_high": np.percentile(weights, 95),
            "delay_high": np.percentile(delays, 95)
        }


class MuhtassibAI:
    """
    Assistant complet du muhtassib
    """

    def __init__(self, contamination: float = 0.1):
        self.detector = AnomalyDetector(contamination=contamination)
        self.inspection_history: List[Dict] = []
        self.alert_threshold: float = 0.7

    def add_transaction(self,
                        price: float,
                        weight: float,
                        delay_days: float,
                        halal_cert_ok: bool,
                        quantity: float = 1.0) -> None:
        """
        Enregistre une transaction pour apprentissage
        """
        self.detector.add_transaction(
            price=price,
            weight=weight,
            delay_days=delay_days,
            halal_cert_ok=1 if halal_cert_ok else 0,
            quantity=quantity
        )

    def train(self) -> bool:
        """
        Entraîne le modèle
        """
        return self.detector.train()

    def analyze_transaction(self, transaction: Dict) -> Dict:
        """
        Analyse une transaction et retourne une recommandation
        """
        score = self.detector.anomaly_score(transaction)
        suspicious_fields = self.detector.get_suspicious_fields(transaction)

        # Niveau de risque
        if score > 0.8:
            risk_level = "CRITIQUE"
        elif score > 0.5:
            risk_level = "ÉLEVÉ"
        elif score > 0.3:
            risk_level = "MOYEN"
        else:
            risk_level = "FAIBLE"

        # Recommendation
        recommendation = "Aucune inspection nécessaire"
        if score > 0.7:
            recommendation = "INSPECTION URGENTE RECOMMANDÉE"
            inspection_type = "complète"
        elif score > 0.4:
            recommendation = "Inspection recommandée"
            inspection_type = "ciblée"
        else:
            inspection_type = "aucune"

        # Enregistrement
        result = {
            "transaction": transaction,
            "anomaly_score": score,
            "risk_level": risk_level,
            "suspicious_fields": suspicious_fields,
            "recommendation": recommendation,
            "inspection_type": inspection_type,
            "timestamp": time.time()
        }

        self.inspection_history.append(result)
        return result

    def suggest_inspection(self, transaction: Dict) -> Dict:
        """
        Suggère une inspection si nécessaire
        """
        analysis = self.analyze_transaction(transaction)

        return {
            "inspect": analysis["anomaly_score"] > self.alert_threshold,
            "score": analysis["anomaly_score"],
            "reason": analysis["recommendation"],
            "fields": analysis["suspicious_fields"],
            "risk_level": analysis["risk_level"],
            "inspection_type": analysis["inspection_type"]
        }

    def get_summary(self) -> Dict:
        """
        Résumé des activités de l'IA
        """
        if not self.inspection_history:
            return {
                "total_analyses": 0,
                "avg_score": 0,
                "alerts": 0
            }

        scores = [h["anomaly_score"] for h in self.inspection_history]
        alerts = [h for h in self.inspection_history if h["anomaly_score"] > self.alert_threshold]

        return {
            "total_analyses": len(self.inspection_history),
            "avg_score": sum(scores) / len(scores),
            "max_score": max(scores),
            "alerts": len(alerts),
            "alert_rate": len(alerts) / len(self.inspection_history),
            "recent_alerts": [
                {
                    "score": h["anomaly_score"],
                    "risk": h["risk_level"],
                    "fields": h["suspicious_fields"]
                }
                for h in alerts[-5:]
            ]
        }


# Exemple d'utilisation
if __name__ == "__main__":
    # Création de l'assistant
    assistant = MuhtassibAI()

    # Ajout de transactions normales pour l'entraînement
    for _ in range(20):
        assistant.add_transaction(
            price=np.random.uniform(1, 10),
            weight=np.random.uniform(1, 5),
            delay_days=np.random.uniform(0, 2),
            halal_cert_ok=True,
            quantity=np.random.uniform(1, 10)
        )

    # Entraînement
    assistant.train()

    # Analyse d'une transaction suspecte
    suspect = {
        "price": 50.0,
        "weight": 100.0,
        "delay": 20.0,
        "halal": False,
        "quantity": 1000.0
    }

    result = assistant.analyze_transaction(suspect)
    print("=== ANALYSE DE TRANSACTION ===")
    print(f"Score d'anomalie: {result['anomaly_score']:.2f}")
    print(f"Niveau de risque: {result['risk_level']}")
    print(f"Champs suspects: {result['suspicious_fields']}")
    print(f"Recommandation: {result['recommendation']}")

    # Suggestion d'inspection
    suggestion = assistant.suggest_inspection(suspect)
    print(f"\nInspection suggérée: {suggestion['inspect']}")
    print(f"Type: {suggestion['inspection_type']}")

    print(f"\nRésumé: {assistant.get_summary()}")

"""
Ancient Egypt – Blé, taux d'intérêt négatif sur 4000 ans
=========================================================

L'Égypte antique a pratiqué pendant 4000 ans un système où :
- Le blé était stocké dans les greniers publics
- Le blé se dégradait (pertes d'environ 20% par an)
- Le taux d'intérêt réel du blé était NÉGATIF
- Prêter du blé était un service, pas un investissement

Leçon : Quand une commodité est périssable, son taux d'intérêt
réel est négatif. Elle ne peut pas être thésaurisée comme l'or.

Référence : Georgescu-Roegen, N. (1971). The Entropy Law and
the Economic Process.

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class EgyptCommodity:
    """
    Une commodité dans l'Égypte antique
    """
    name: str
    name_ar: str
    degradation_rate: float  # Perte annuelle (%)
    storage_cost: float
    fraud_rate: float
    storage_years_max: float
    historical_period: str
    significance: str

    def real_interest_rate(self, storage_days: int) -> float:
        """Taux d'intérêt réel (négatif = perte)"""
        years = storage_days / 365
        total_loss = (self.degradation_rate + self.storage_cost + self.fraud_rate) * years
        return -total_loss

    def get_lesson(self) -> str:
        """Leçon historique"""
        return f"""
        Commodité: {self.name}
        Période: {self.historical_period}
        Perte annuelle: {self.degradation_rate:.1%}
        Taux d'intérêt réel: {self.real_interest_rate(365):.1%} (1 an)

        Leçon: Une commodité périssable ne peut pas servir de réserve de valeur.
        Elle doit CIRCULER. C'est la fonction du fulus.
        """


# Commodités de l'Égypte antique
EGYPT_COMMODITIES = {
    'wheat': EgyptCommodity(
        name="Blé",
        name_ar="قمح",
        degradation_rate=0.20,     # -20% par an
        storage_cost=0.03,         # 3% par an
        fraud_rate=0.02,           # 2% perte (rongeurs)
        storage_years_max=3.0,
        historical_period="Ancien Empire (2700-2200 av. J.-C.)",
        significance="Base de l'alimentation égyptienne, stocké dans les greniers"
    ),
    'barley': EgyptCommodity(
        name="Orge",
        name_ar="شعير",
        degradation_rate=0.18,     # -18% par an
        storage_cost=0.03,
        fraud_rate=0.02,
        storage_years_max=3.0,
        historical_period="Moyen Empire (2050-1650 av. J.-C.)",
        significance="Monnaie de base pour les salaires des ouvriers"
    ),
    'flax': EgyptCommodity(
        name="Lin",
        name_ar="كتان",
        degradation_rate=0.12,     # -12% par an (moins périssable)
        storage_cost=0.02,
        fraud_rate=0.02,
        storage_years_max=5.0,
        historical_period="Nouvel Empire (1550-1070 av. J.-C.)",
        significance="Textile de luxe, exportation"
    ),
    'papyrus': EgyptCommodity(
        name="Papyrus",
        name_ar="ورق البردي",
        degradation_rate=0.08,     # -8% par an
        storage_cost=0.01,
        fraud_rate=0.01,
        storage_years_max=10.0,
        historical_period="Toutes périodes",
        significance="Support d'écriture, exportation majeure"
    )
}


class EgyptAncientAnalysis:
    """
    Analyse du système monétaire de l'Égypte antique
    """

    def __init__(self):
        self.commodities = EGYPT_COMMODITIES

    def get_commodity(self, name: str) -> Optional[EgyptCommodity]:
        """Récupère une commodité par son nom"""
        for key, value in self.commodities.items():
            if key == name or value.name == name:
                return value
        return None

    def get_grain_storage_lesson(self) -> str:
        """
        Leçon sur le stockage des grains en Égypte antique
        """
        return """
        === LEÇON DES GRENIERS ÉGYPTIENS ===

        L'Égypte antique a développé un système de stockage des grains
        qui a fonctionné pendant 4000 ans :

        1. Principe de Yusuf (Coran 12:47-48) :
           - Stocker en abondance (7 années grasses)
           - Distribuer en rareté (7 années maigres)

        2. Taux d'intérêt réel NÉGATIF :
           - Le blé perd 20% de sa valeur par an
           - Prêter du blé = perdre de l'argent
           - Donc le blé ne peut pas être thésaurisé

        3. Leçon pour notre système :
           - Une commodité périssable doit CIRCULER
           - Elle n'est pas une réserve de valeur
           - Elle est un excellent fulus (monnaie de vélocité)

        4. Le blé comme nuqud ?
           - IMPOSSIBLE : il se dégrade trop vite
           - Mais il peut entrer dans le panier Grondona
           - Avec un prix plancher/plafond qui tient compte de la dégradation
        """

    def compare_with_grondona(self) -> Dict:
        """
        Compare le système égyptien avec le système Grondona
        """
        return {
            'egyptian_system': {
                'commodity': 'Blé',
                'storage': 'Greniers publics',
                'degradation': '-20%/an',
                'interest_rate': 'Négatif',
                'currency': 'In-kind (blé)'
            },
            'grondona_system': {
                'commodity': 'Blé (dans le panier)',
                'storage': 'Stockpiles publics (CRD)',
                'degradation': 'Prix plancher/plafond',
                'interest_rate': 'Négatif (compensé par le CRD)',
                'currency': 'Fulus (monnaie de vélocité)'
            },
            'continuity': {
                'principle': 'Principe de Yusuf : stocker en abondance, distribuer en rareté',
                'innovation': 'Le CRD Grondona ajoute un prix plancher/plafond',
                'lesson': 'Les commodités périssables doivent circuler vite'
            }
        }

    def get_timeline(self) -> List[Dict]:
        """
        Chronologie du système monétaire égyptien
        """
        return [
            {
                'period': 'Ancien Empire (2700-2200 av. J.-C.)',
                'system': 'Stockage des grains, paiement en nature',
                'key_event': 'Construction des pyramides (paiement en blé/orge)'
            },
            {
                'period': 'Moyen Empire (2050-1650 av. J.-C.)',
                'system': 'Standardisation des mesures (coudée, hekat)',
                'key_event': 'Introduction du hekat comme mesure standard'
            },
            {
                'period': 'Nouvel Empire (1550-1070 av. J.-C.)',
                'system': 'Système de crédit, prêts en grains',
                'key_event': 'Taux d\'intérêt négatif documenté sur les prêts en blé'
            },
            {
                'period': 'Période ptolémaïque (332-30 av. J.-C.)',
                'system': 'Introduction de la monnaie (drachme)',
                'key_event': 'Première monnaie métallique, mais le blé reste la référence'
            }
        ]

    def get_summary(self) -> Dict:
        """Résumé de l'analyse égyptienne"""
        return {
            'commodities': [
                {
                    'name': c.name,
                    'arabic': c.name_ar,
                    'degradation': f"{c.degradation_rate:.1%}",
                    'interest_rate_1y': f"{c.real_interest_rate(365):.1%}",
                    'period': c.historical_period
                }
                for c in self.commodities.values()
            ],
            'lesson': self.get_grain_storage_lesson(),
            'comparison': self.compare_with_grondona(),
            'timeline': self.get_timeline()
        }


# Exemple d'utilisation
if __name__ == "__main__":
    analysis = EgyptAncientAnalysis()

    print("=== ÉGYPTE ANTIQUE – 4000 ANS DE TAUX NÉGATIFS ===")
    print(analysis.get_grain_storage_lesson())

    print("\n=== COMMODITÉS ÉGYPTIENNES ===")
    for name, commodity in analysis.commodities.items():
        print(f"\n{commodity.name} ({commodity.name_ar})")
        print(f"  Période: {commodity.historical_period}")
        print(f"  Dégradation: {commodity.degradation_rate:.1%}/an")
        print(f"  Taux d'intérêt réel (1 an): {commodity.real_interest_rate(365):.1%}")

    print("\n=== COMPARAISON AVEC GRONDONA ===")
    comparison = analysis.compare_with_grondona()
    print(f"\nSystème égyptien: {comparison['egyptian_system']}")
    print(f"Système Grondona: {comparison['grondona_system']}")
    print(f"Continuité: {comparison['continuity']}")

"""
Gold & Silver – Métaux précieux, thaman primus inter pares
===========================================================

L'or et l'argent sont les étalons fondamentaux du système.
Ils sont :
- Non périssables (dégradation 0%)
- Stockables éternellement
- Reconnus universellement
- Divisible et mesurable

Référence : Jastram, R. (1977). The Golden Constant.

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class MetalCommodity:
    """
    Caractéristiques d'un métal précieux comme thaman
    """
    name: str
    name_arabic: str
    symbol: str
    is_primary_thaman: bool = True
    degradation_rate: float = 0.0  # 0% par an
    storage_years_max: Optional[float] = None  # Infini
    historical_context: str = ""

    # Paramètres économiques
    zakat_rate: float = 0.025  # 2.5%
    nisab_grams: float = 85.0  # Pour l'or (595g pour l'argent)

    # Ratio historique
    gold_silver_ratio: float = 10.0  # 1g or = 10g argent

    def real_interest_rate(self, storage_days: int) -> float:
        """Taux d'intérêt réel = 0% (pas de dégradation)"""
        return 0.0

    def value_in_gold_equivalent(self, weight_grams: float) -> float:
        """Convertit la valeur en équivalent or"""
        if self.name.lower() == 'gold':
            return weight_grams
        elif self.name.lower() == 'silver':
            return weight_grams / self.gold_silver_ratio
        return weight_grams

    def zakat_due(self, weight_grams: float) -> float:
        """Calcule la Zakat due sur ce métal"""
        if weight_grams < self.nisab_grams:
            return 0.0
        return weight_grams * self.zakat_rate


# Métaux primaires
PRIMARY_METALS = [
    MetalCommodity(
        name="Gold",
        name_arabic="ذهبي (Dahabi)",
        symbol="Au",
        is_primary_thaman=True,
        degradation_rate=0.0,
        historical_context="The Golden Constant (Jastram, 1977) : 400 ans de stabilité",
        nisab_grams=85.0,
        gold_silver_ratio=10.0
    ),
    MetalCommodity(
        name="Silver",
        name_arabic="فضي (Fiddi)",
        symbol="Ag",
        is_primary_thaman=True,
        degradation_rate=0.0,
        historical_context="Le dirham islamique, monnaie du Prophète",
        nisab_grams=595.0,
        gold_silver_ratio=10.0
    )
]


class GoldSilverAnalysis:
    """
    Analyse du rôle de l'or et de l'argent dans le système
    """

    def __init__(self):
        self.metals = {m.name.lower(): m for m in PRIMARY_METALS}

    def get_metal(self, name: str) -> Optional[MetalCommodity]:
        """Récupère un métal par son nom"""
        return self.metals.get(name.lower())

    def compare_metals(self) -> Dict:
        """
        Compare l'or et l'argent comme thaman
        """
        return {
            'gold': {
                'advantages': [
                    'Plus grande valeur par gramme',
                    'Plus compact pour les grandes valeurs',
                    'Reconnaissance universelle plus forte',
                    'Plus stable historiquement'
                ],
                'disadvantages': [
                    'Moins divisible pour les petits achats',
                    'Moins courant dans les transactions quotidiennes'
                ],
                'score': 95
            },
            'silver': {
                'advantages': [
                    'Plus divisible',
                    'Plus utilisé dans les transactions courantes',
                    'Plus accessible pour les petits épargnants',
                    'Tradition islamique plus forte (dirham)'
                ],
                'disadvantages': [
                    'Moindre valeur par gramme',
                    'Plus volumineux pour les grandes valeurs',
                    'Plus sensible aux chocs de marché'
                ],
                'score': 85
            }
        }

    def get_historical_ratio(self, year: int = 2024) -> float:
        """
        Retourne le ratio or/argent historique
        """
        # Données historiques simplifiées
        historical_ratios = {
            1800: 15.5,
            1850: 15.3,
            1900: 16.0,
            1913: 15.5,  # Crime de 1873
            1950: 25.0,
            1970: 30.0,
            1980: 40.0,
            1990: 60.0,
            2000: 70.0,
            2010: 65.0,
            2020: 80.0,
            2024: 85.0
        }

        # Interpolation pour les années intermédiaires
        years = sorted(historical_ratios.keys())
        if year in historical_ratios:
            return historical_ratios[year]

        for i in range(len(years) - 1):
            if years[i] <= year <= years[i + 1]:
                ratio1 = historical_ratios[years[i]]
                ratio2 = historical_ratios[years[i + 1]]
                t = (year - years[i]) / (years[i + 1] - years[i])
                return ratio1 + t * (ratio2 - ratio1)

        # Approximation
        return 85.0

    def is_bimetallism_viable(self, legal_ratio: float,
                              current_ratio: float,
                              tolerance: float = 0.2) -> Dict:
        """
        Vérifie si le bimétallisme est viable à un ratio donné

        Référence : Velde & Weber (2000)
        """
        lower_bound = legal_ratio * (1 - tolerance)
        upper_bound = legal_ratio * (1 + tolerance)

        is_viable = lower_bound <= current_ratio <= upper_bound

        if current_ratio < lower_bound:
            deviation = "gold_dominance"  # L'or devient trop cher
        elif current_ratio > upper_bound:
            deviation = "silver_dominance"  # L'argent devient trop cher
        else:
            deviation = "bimetallic_equilibrium"

        return {
            'legal_ratio': legal_ratio,
            'current_ratio': current_ratio,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'is_viable': is_viable,
            'deviation': deviation,
            'message': self._get_viability_message(deviation)
        }

    def _get_viability_message(self, deviation: str) -> str:
        """Message explicatif sur la viabilité"""
        messages = {
            'gold_dominance': "L'or domine l'argent. Les gens thésaurisent l'or, font circuler l'argent. Loi de Gresham.",
            'silver_dominance': "L'argent domine l'or. Les gens thésaurisent l'argent, font circuler l'or.",
            'bimetallic_equilibrium': "Équilibre bimétallique. Les deux métaux circulent librement."
        }
        return messages.get(deviation, "Situation indéterminée")

    def get_summary(self) -> Dict:
        """Résumé de l'analyse"""
        return {
            'primary_metals': [
                {
                    'name': m.name,
                    'arabic': m.name_arabic,
                    'symbol': m.symbol,
                    'nisab_grams': m.nisab_grams,
                    'zakat_rate': m.zakat_rate
                }
                for m in PRIMARY_METALS
            ],
            'current_ratio': self.get_historical_ratio(2024),
            'comparison': self.compare_metals()
        }


# Exemple d'utilisation
if __name__ == "__main__":
    analysis = GoldSilverAnalysis()

    print("=== OR ET ARGENT – THAMAN PRIMUS ===")
    print(f"Or: Nisab = {analysis.get_metal('gold').nisab_grams}g")
    print(f"Argent: Nisab = {analysis.get_metal('silver').nisab_grams}g")

    # Ratio historique
    ratio_1873 = analysis.get_historical_ratio(1873)
    ratio_2024 = analysis.get_historical_ratio(2024)

    print(f"\nRatio or/argent :")
    print(f"  1873 (Crime de 1873): {ratio_1873:.1f}:1")
    print(f"  2024: {ratio_2024:.1f}:1")

    # Viabilité du bimétallisme
    legal_ratio = 15.5  # Ratio malikite
    viability = analysis.is_bimetallism_viable(legal_ratio, ratio_2024)

    print(f"\nViabilité du bimétallisme (ratio légal {legal_ratio}:1):")
    print(f"  Ratio actuel: {ratio_2024:.1f}:1")
    print(f"  Viable: {viability['is_viable']}")
    print(f"  Message: {viability['message']}")

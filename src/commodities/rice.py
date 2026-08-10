"""
Rice – Riz, koku japonais, mesure de richesse
==============================================

Le riz a été une forme de monnaie et de mesure de richesse :
- Japon féodal : koku = riz pour 1 personne pour 1 an
- Chine impériale : paiement des impôts en riz pendant des millénaires
- Thaïlande : programme de garantie des prix du riz

Le riz illustre la distinction entre :
- Riz paddy (stockable 8 ans, ~-4%/an) → Grondona basket
- Riz blanc (périssable, ~-20%/an) → doit circuler vite (fulus)

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class RiceType:
    """
    Caractéristiques d'un type de riz
    """
    name: str
    name_fr: str
    degradation_rate: float
    storage_cost: float
    fraud_rate: float
    storage_years_max: float
    layer: str  # grondona_basket, currency_velocity, buffer_stock
    historical_context: str = ""
    cultural_significance: str = ""

    def real_interest_rate(self, storage_days: int) -> float:
        """Taux d'intérêt réel (négatif = perte)"""
        years = storage_days / 365
        total_loss = (self.degradation_rate + self.storage_cost + self.fraud_rate) * years
        return -total_loss

    def required_velocity(self, max_allowed_loss: float = 0.05) -> Dict:
        """
        Vélocité minimale pour limiter la perte
        """
        total_loss_rate = self.degradation_rate + self.storage_cost + self.fraud_rate
        if total_loss_rate == 0:
            return {
                'velocity_needed': 0,
                'message': 'Pas de contrainte de vélocité (stockage éternel)'
            }

        velocity_needed = total_loss_rate / max_allowed_loss
        return {
            'velocity_needed': velocity_needed,
            'turnover_days': 365 / velocity_needed if velocity_needed > 0 else float('inf'),
            'message': f"Le {self.name_fr} doit être renouvelé toutes les {365/velocity_needed:.0f} jours"
        }


# Types de riz
RICE_TYPES = {
    'paddy': RiceType(
        name="paddy",
        name_fr="Riz paddy (non décortiqué)",
        degradation_rate=0.04,     # -4% par an
        storage_cost=0.01,         # 1% par an
        fraud_rate=0.02,           # 2% (insectes, humidité)
        storage_years_max=8.0,     # 8-10 ans selon climat
        layer="grondona_basket",
        historical_context="Japon féodal : stocké dans les greniers seigneuriaux (kura)",
        cultural_significance="Mesure de richesse pendant l'ère Edo"
    ),
    'white': RiceType(
        name="white",
        name_fr="Riz blanc (décortiqué)",
        degradation_rate=0.20,     # -20% par an
        storage_cost=0.03,         # 3% par an
        fraud_rate=0.02,           # 2%
        storage_years_max=1.0,     # 6-12 mois
        layer="currency_velocity",
        historical_context="Chine ancienne : consommé frais, prêt à taux négatif réel",
        cultural_significance="Le riz blanc doit circuler vite"
    ),
    'parboiled': RiceType(
        name="parboiled",
        name_fr="Riz étuvé (parboiled)",
        degradation_rate=0.10,     # -10% par an
        storage_cost=0.02,         # 2% par an
        fraud_rate=0.02,           # 2%
        storage_years_max=2.5,     # 2-3 ans
        layer="buffer_stock",
        historical_context="Inde du Sud : invention ancienne pour prolonger la durée",
        cultural_significance="Stock tampon entre couches 2 et 3"
    )
}


class RiceCommodityAnalysis:
    """
    Analyse du riz comme commodité monétaire
    """

    def __init__(self):
        self.rice_types = RICE_TYPES

    def get_rice_type(self, name: str) -> Optional[RiceType]:
        """Récupère un type de riz par son nom"""
        return self.rice_types.get(name)

    def historical_context(self) -> Dict:
        """
        Contexte historique du riz comme monnaie
        """
        return {
            'japan_koku': {
                'period': '1603-1868 (Edo period)',
                'fact': '1 koku = 180.39 litres = riz pour 1 personne pour 1 an',
                'lesson': 'Le riz comme unité de mesure de richesse (thaman asiatique)'
            },
            'china_tax': {
                'period': '700 BCE - 1911 CE',
                'fact': 'Le riz comme paiement des impôts pendant des millénaires',
                'lesson': 'Le riz comme réserve de valeur étatique (principe Yusuf)'
            },
            'thailand_pledge': {
                'period': '1980-2020 (Pledge Scheme)',
                'fact': "Programme de garantie des prix du riz (populisme, inflation)",
                'lesson': 'Danger du prix plancher sans stockage physique réel'
            }
        }

    def koku_to_grams(self, koku: float) -> float:
        """
        Convertit les koku japonais en grammes de riz
        """
        liters = koku * 180.39  # 1 koku = 180.39 litres
        grams = liters * 0.85   # densité approximative du riz
        return grams

    def grams_to_koku(self, grams: float) -> float:
        """
        Convertit les grammes en koku
        """
        liters = grams / 0.85
        return liters / 180.39

    def compare_rice_with_thaman(self) -> Dict:
        """
        Compare le riz avec l'or/l'argent comme thaman potentiel
        """
        return {
            'gold_as_thaman': {
                'is_suitable': True,
                'reason': 'Perte 0%, stockage éternel, reconnaissance universelle',
                'layer': 'thaman_primary'
            },
            'silver_as_thaman': {
                'is_suitable': True,
                'reason': 'Perte 0%, stockage éternel, reconnaissance universelle (moindre)',
                'layer': 'thaman_primary'
            },
            'rice_paddy_as_thaman': {
                'is_suitable': False,
                'reason': f'Perte -4%/an, stockage max 8 ans, reconnaissance régionale (Asie seulement)',
                'layer': 'grondona_basket',
                'note': 'Peut servir de thaman régional, pas universel'
            },
            'rice_white_as_thaman': {
                'is_suitable': False,
                'reason': f'Perte -20%/an, stockage max 1 an, trop périssable',
                'layer': 'currency_velocity',
                'note': "Ne peut PAS être thaman — doit circuler vite"
            },
            'rice_parboiled_as_thaman': {
                'is_suitable': False,
                'reason': 'Perte -10%/an, stockage max 2.5 ans, semi-périssable',
                'layer': 'buffer_stock',
                'note': "Stock tampon entre le thaman et la monnaie de vélocité"
            }
        }

    def get_summary(self) -> Dict:
        """Résumé de l'analyse du riz"""
        return {
            'rice_types': [
                {
                    'name': k,
                    'fr': v.name_fr,
                    'layer': v.layer,
                    'degradation': f"{v.degradation_rate:.1%}",
                    'storage_years': v.storage_years_max
                }
                for k, v in self.rice_types.items()
            ],
            'historical_context': self.historical_context(),
            'comparison_with_thaman': self.compare_rice_with_thaman(),
            'koku_conversion': {
                '1_koku_grams': self.koku_to_grams(1),
                '1000_grams_koku': self.grams_to_koku(1000)
            }
        }


# Exemple d'utilisation
if __name__ == "__main__":
    analysis = RiceCommodityAnalysis()

    print("=== LE RIZ DANS LE SYSTÈME MONÉTAIRE ===")

    print("\n=== TYPES DE RIZ ET LEUR COUCHE ===")
    for name, rice in analysis.rice_types.items():
        print(f"\n{rice.name_fr}:")
        print(f"  Couche: {rice.layer}")
        print(f"  Dégradation: {rice.degradation_rate:.1%}/an")
        print(f"  Stockage max: {rice.storage_years_max} ans")

        # Taux d'intérêt réel
        real_rate = rice.real_interest_rate(365)
        print(f"  Taux d'intérêt réel (1 an): {real_rate:.1%}")

        # Vélocité requise
        velocity = rice.required_velocity()
        if velocity['velocity_needed'] > 0:
            print(f"  Vélocité: {velocity['velocity_needed']:.1f} renouvellements/an")
            print(f"  {velocity['message']}")

    print("\n=== CONVERSION KOKU ===")
    print(f"1 koku = {analysis.koku_to_grams(1):.0f} g de riz")
    print(f"1000g = {analysis.grams_to_koku(1000):.3f} koku")

    print("\n=== LE RIZ PEUT-IL ÊTRE THAMAN ? ===")
    comparison = analysis.compare_rice_with_thaman()
    for item, info in comparison.items():
        suitability = "✅ OUI" if info['is_suitable'] else "❌ NON"
        print(f"\n{item.replace('_', ' ').title()}: {suitability}")
        print(f"  {info['reason']}")
        print(f"  Couche: {info['layer']}")
        if 'note' in info:
            print(f"  Note: {info['note']}")

"""
Grondona Basket – Panier de commodités complet
==============================================

Le panier Grondona est la couche 2 du système monétaire :
- Adossement de la monnaie (fulus)
- Prix plancher/plafond
- Stockpiles publics (principe de Yusuf)

Composition du panier :
1. Métaux précieux : Or, Argent (thaman primus)
2. Semi-thaman : Sel gemme, Cuivre
3. Commodités agricoles : Blé, Riz paddy
4. Commodités industrielles : Coton, Caoutchouc
5. Énergie : Pétrole, Gaz naturel

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class BasketCommodity:
    """
    Une commodité dans le panier Grondona
    """
    name: str
    name_fr: str
    category: str  # metal, semi_thaman, agriculture, industrial, energy
    floor_price: float
    ceiling_price: float
    current_price: float
    stockpile: float = 0.0
    elasticity: float = 100.0

    # Caractéristiques physiques
    degradation_rate: float = 0.0
    storage_years_max: Optional[float] = None

    # Rôle dans le système
    is_nuqud: bool = False  # Devient nuqud une fois dans le panier
    is_fulus: bool = False  # N'est PAS de la monnaie courante

    historical_significance: str = ""

    def real_interest_rate(self, storage_days: int) -> float:
        """Taux d'intérêt réel (négatif = perte)"""
        years = storage_days / 365
        total_loss = self.degradation_rate * years
        return -total_loss

    def to_dict(self) -> Dict:
        """Convertit en dictionnaire"""
        return {
            'name': self.name,
            'name_fr': self.name_fr,
            'category': self.category,
            'floor_price': self.floor_price,
            'ceiling_price': self.ceiling_price,
            'current_price': self.current_price,
            'stockpile': self.stockpile,
            'degradation_rate': self.degradation_rate,
            'storage_years_max': self.storage_years_max,
            'is_nuqud': self.is_nuqud
        }


# Composition du panier Grondona
BASKET_COMPOSITION = {
    # Métaux précieux (thaman primus)
    'gold': BasketCommodity(
        name='gold',
        name_fr='Or',
        category='metal',
        floor_price=1800.0,
        ceiling_price=2200.0,
        current_price=2000.0,
        degradation_rate=0.0,
        storage_years_max=None,
        is_nuqud=True,
        historical_significance="The Golden Constant (Jastram, 1977)"
    ),
    'silver': BasketCommodity(
        name='silver',
        name_fr='Argent',
        category='metal',
        floor_price=22.0,
        ceiling_price=28.0,
        current_price=25.0,
        degradation_rate=0.0,
        storage_years_max=None,
        is_nuqud=True,
        historical_significance="Dirham islamique, monnaie du Prophète"
    ),

    # Semi-thaman (stockage éternel, valeur modérée)
    'rock_salt': BasketCommodity(
        name='rock_salt',
        name_fr='Sel gemme',
        category='semi_thaman',
        floor_price=50.0,
        ceiling_price=70.0,
        current_price=60.0,
        degradation_rate=0.001,
        storage_years_max=None,
        is_nuqud=False,
        historical_significance="Via Salaria, salarium romain"
    ),
    'copper': BasketCommodity(
        name='copper',
        name_fr='Cuivre',
        category='semi_thaman',
        floor_price=8000.0,
        ceiling_price=12000.0,
        current_price=9500.0,
        degradation_rate=0.005,
        storage_years_max=None,
        is_nuqud=False,
        historical_significance="Premier métal utilisé par l'humanité, industrie"
    ),

    # Commodités agricoles (stockage limité)
    'wheat': BasketCommodity(
        name='wheat',
        name_fr='Blé',
        category='agriculture',
        floor_price=180.0,
        ceiling_price=220.0,
        current_price=200.0,
        degradation_rate=0.04,
        storage_years_max=5.0,
        is_nuqud=False,
        historical_significance="Égypte antique : 4000 ans de taux négatifs"
    ),
    'rice_paddy': BasketCommodity(
        name='rice_paddy',
        name_fr='Riz paddy',
        category='agriculture',
        floor_price=300.0,
        ceiling_price=400.0,
        current_price=350.0,
        degradation_rate=0.04,
        storage_years_max=8.0,
        is_nuqud=False,
        historical_significance="Koku japonais, mesure de richesse"
    ),

    # Commodités industrielles
    'cotton': BasketCommodity(
        name='cotton',
        name_fr='Coton',
        category='industrial',
        floor_price=70.0,
        ceiling_price=90.0,
        current_price=80.0,
        degradation_rate=0.08,
        storage_years_max=3.0,
        is_nuqud=False,
        historical_significance="Révolution industrielle, textile"
    ),
    'rubber': BasketCommodity(
        name='rubber',
        name_fr='Caoutchouc',
        category='industrial',
        floor_price=140.0,
        ceiling_price=180.0,
        current_price=160.0,
        degradation_rate=0.05,
        storage_years_max=5.0,
        is_nuqud=False,
        historical_significance="Pneumatiques, industrie automobile"
    ),

    # Énergie
    'oil': BasketCommodity(
        name='oil',
        name_fr='Pétrole brut',
        category='energy',
        floor_price=70.0,
        ceiling_price=100.0,
        current_price=85.0,
        degradation_rate=0.02,
        storage_years_max=2.0,
        is_nuqud=False,
        historical_significance="Économie moderne, énergie"
    ),
    'natural_gas': BasketCommodity(
        name='natural_gas',
        name_fr='Gaz naturel',
        category='energy',
        floor_price=3.0,
        ceiling_price=6.0,
        current_price=4.5,
        degradation_rate=0.01,
        storage_years_max=1.0,
        is_nuqud=False,
        historical_significance="Transition énergétique"
    )
}


class GrondonaBasket:
    """
    Panier Grondona complet
    """

    def __init__(self):
        self.commodities = BASKET_COMPOSITION.copy()

    def get_commodity(self, name: str) -> Optional[BasketCommodity]:
        """Récupère une commodité par son nom"""
        return self.commodities.get(name)

    def get_all_commodities(self) -> List[BasketCommodity]:
        """Retourne toutes les commodités"""
        return list(self.commodities.values())

    def get_by_category(self, category: str) -> List[BasketCommodity]:
        """Retourne les commodités d'une catégorie"""
        return [c for c in self.commodities.values() if c.category == category]

    def get_total_value(self) -> float:
        """Valeur totale du panier (prix × stock)"""
        total = 0.0
        for c in self.commodities.values():
            total += c.current_price * c.stockpile
        return total

    def update_prices(self, new_prices: Dict[str, float]) -> None:
        """
        Met à jour les prix des commodités
        """
        for name, price in new_prices.items():
            if name in self.commodities:
                commodity = self.commodities[name]
                # Vérification des bornes
                commodity.current_price = max(
                    commodity.floor_price,
                    min(commodity.ceiling_price, price)
                )

    def get_stabilization_effect(self) -> Dict:
        """
        Calcule l'effet de stabilisation du panier
        """
        total_volatility = 0.0
        n = len(self.commodities)

        for c in self.commodities.values():
            # Volatilité relative
            range_price = c.ceiling_price - c.floor_price
            if range_price > 0:
                volatility = (c.current_price - c.floor_price) / range_price
                total_volatility += volatility

        avg_volatility = total_volatility / n if n > 0 else 0.5

        return {
            'n_commodities': n,
            'avg_volatility': avg_volatility,
            'stabilization_factor': 1 / (1 + avg_volatility),
            'total_value': self.get_total_value(),
            'categories': {
                cat: len(self.get_by_category(cat))
                for cat in ['metal', 'semi_thaman', 'agriculture', 'industrial', 'energy']
            }
        }

    def get_summary(self) -> Dict:
        """Résumé du panier"""
        return {
            'total_commodities': len(self.commodities),
            'total_value': self.get_total_value(),
            'stabilization': self.get_stabilization_effect(),
            'commodities': {
                name: c.to_dict()
                for name, c in self.commodities.items()
            }
        }


# Exemple d'utilisation
if __name__ == "__main__":
    basket = GrondonaBasket()

    print("=== PANIER GRONDONA ===")
    print(f"Total commodités: {len(basket.commodities)}")

    # Par catégorie
    print("\n=== PAR CATÉGORIE ===")
    for category in ['metal', 'semi_thaman', 'agriculture', 'industrial', 'energy']:
        items = basket.get_by_category(category)
        print(f"\n{category.upper()}: {len(items)} commodités")
        for c in items:
            print(f"  {c.name_fr}: {c.current_price:.0f} (plancher {c.floor_price:.0f} / plafond {c.ceiling_price:.0f})")

    # Effet de stabilisation
    print("\n=== EFFET DE STABILISATION ===")
    stabilization = basket.get_stabilization_effect()
    print(f"Nombre de commodités: {stabilization['n_commodities']}")
    print(f"Volatilité moyenne: {stabilization['avg_volatility']:.2%}")
    print(f"Facteur de stabilisation: {stabilization['stabilization_factor']:.2%}")
    print(f"Valeur totale du panier: {stabilization['total_value']:.2f}")

    # Mise à jour des prix
    print("\n=== MISE À JOUR DES PRIX ===")
    new_prices = {
        'gold': 2100.0,
        'silver': 26.0,
        'wheat': 190.0,
        'oil': 90.0
    }
    basket.update_prices(new_prices)

    for name, price in new_prices.items():
        c = basket.get_commodity(name)
        if c:
            print(f"{c.name_fr}: {c.current_price:.0f}")

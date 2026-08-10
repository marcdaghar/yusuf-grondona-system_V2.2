"""
Grondona CRD (Commodity Reserve Department)
===========================================

Règle fondamentale du système :
"Toute commodité qui entre dans le panier Grondona DEVIENT nuqud :
 - Elle sert d'ÉTALON DE MESURE de la valeur
 - Elle sert de RÉSERVE DE VALEUR
 - Elle SORT de la monnaie courante (n'est plus fulus)

La monnaie courante (fulus) n'a alors qu'une fonction :
 LA VÉLOCITÉ MARCHANDE (facilité des transactions)

Basé sur : Velde & Weber (2000) – modèle bimétallique
          Principe de Yusuf (Coran 12:47-48)

License: CC BY-SA 4.0 – Marc Daghar
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import time
import math


@dataclass
class CommodityInBasket:
    """Une commodité dans le panier Grondona"""
    name: str
    floor_price: float      # Prix plancher (CRD achète)
    ceiling_price: float    # Prix plafond (CRD vend)
    current_price: float
    stockpile: float = 0.0
    elasticity: float = 100.0

    # Devient nuqud → règles strictes du riba
    is_thaman: bool = True       # Étalon de mesure
    is_reserve: bool = True      # Réserve de valeur
    is_fulus: bool = False       # N'est PAS monnaie courante

    historical_context: str = ""


class GrondonaCRD:
    """
    Commodity Reserve Department (CRD)
    Implémente le principe de Yusuf : stocker en abondance, distribuer en rareté
    """

    def __init__(self, commodities: List[CommodityInBasket],
                 initial_currency_supply: float = 10000,
                 storage_cost: float = 0.005,
                 transaction_cost: float = 0.001):
        """
        Args:
            commodities: Liste des commodités dans le panier
            initial_currency_supply: Masse monétaire initiale (fulus)
            storage_cost: Coût de stockage annuel (en %)
            transaction_cost: Coût de transaction (en %)
        """
        self.commodities = {c.name: c for c in commodities}
        self.currency_supply = initial_currency_supply
        self.storage_cost = storage_cost
        self.transaction_cost = transaction_cost

        self.history: List[Dict] = []
        self.intervention_history: List[Dict] = []

    def check_market_prices(self, prices: Dict[str, float], time_step: float = 1.0) -> List[Dict]:
        """
        Opération centrale du CRD

        Quand le prix est BAS (sous le plancher) : CRD ACHÈTE
        - La commodité ENTRE dans le nuqud (devient étalon + réserve)
        - La monnaie courante (fulus) est émise en contrepartie

        Quand le prix est HAUT (au-dessus plafond) : CRD VEND
        - La commodité SORT du nuqud (redevient marchandise ordinaire)
        - La monnaie courante (fulus) est détruite
        """
        operations = []

        for name, price in prices.items():
            commodity = self.commodities.get(name)
            if not commodity:
                continue

            # Mise à jour du prix courant
            commodity.current_price = price

            if price < commodity.floor_price:
                # ZONE D'ABONDANCE : CRD ACHÈTE
                purchase_qty = (commodity.floor_price - price) * commodity.elasticity
                purchase_qty *= (1 - self.transaction_cost)

                # Vérification de la capacité de stockage (limite à 10000 unités)
                max_storage = 10000
                available = max_storage - commodity.stockpile
                purchase_qty = min(purchase_qty, available)

                if purchase_qty > 0:
                    commodity.stockpile += purchase_qty
                    self.currency_supply += purchase_qty * commodity.floor_price
                    self.currency_supply -= commodity.stockpile * self.storage_cost * time_step

                    operation = {
                        'action': 'BUY',
                        'commodity': name,
                        'quantity': purchase_qty,
                        'price': commodity.floor_price,
                        'currency_created': purchase_qty * commodity.floor_price,
                        'message': f"Achat de {commodity.name} à {commodity.floor_price}$/unité. "
                                   f"{commodity.name} ENTRE dans le nuqud (devient étalon + réserve). "
                                   f"Monnaie courante émise : {purchase_qty * commodity.floor_price:.2f} fulus"
                    }
                    operations.append(operation)

            elif price > commodity.ceiling_price:
                # ZONE DE RARETÉ : CRD VEND
                sale_qty = min(commodity.stockpile,
                              (price - commodity.ceiling_price) * commodity.elasticity)
                sale_qty = min(sale_qty, commodity.stockpile * 0.3)  # Ne pas vider les réserves

                if sale_qty > 0:
                    commodity.stockpile -= sale_qty
                    self.currency_supply -= sale_qty * commodity.ceiling_price

                    operation = {
                        'action': 'SELL',
                        'commodity': name,
                        'quantity': sale_qty,
                        'price': commodity.ceiling_price,
                        'currency_destroyed': sale_qty * commodity.ceiling_price,
                        'message': f"Vente de {commodity.name} à {commodity.ceiling_price}$/unité. "
                                   f"{commodity.name} SORT du nuqud (retour au commerce ordinaire). "
                                   f"Monnaie courante détruite : {sale_qty * commodity.ceiling_price:.2f} fulus"
                    }
                    operations.append(operation)

        self.history.append({
            'time': len(self.history),
            'currency_supply': self.currency_supply,
            'operations': operations,
            'timestamp': time.time()
        })

        if operations:
            self.intervention_history.extend(operations)

        return operations

    def release_food(self, quantity: float, commodity: str = "Wheat") -> float:
        """
        Libération de stocks de première nécessité (principe de Yusuf)
        Utilisé en cas de crise ou de pénurie
        """
        commodity_obj = self.commodities.get(commodity)
        if not commodity_obj:
            return 0.0

        release_qty = min(quantity, commodity_obj.stockpile)
        commodity_obj.stockpile -= release_qty
        self.currency_supply -= release_qty * commodity_obj.floor_price * 0.5  # Subventionné

        self.history.append({
            'time': len(self.history),
            'action': 'RELEASE',
            'commodity': commodity,
            'quantity': release_qty,
            'message': f"Libération d'urgence de {release_qty} unités de {commodity}"
        })

        return release_qty

    def get_nuqud_reserves(self) -> Dict[str, float]:
        """Retourne les réserves de nuqud (étalons de mesure + réserves de valeur)"""
        return {name: c.stockpile for name, c in self.commodities.items()}

    def get_fulus_supply(self) -> float:
        """Retourne la masse de fulus (monnaie de vélocité uniquement)"""
        return self.currency_supply

    def is_commodity_nuqud(self, commodity_name: str) -> bool:
        """Une commodité est-elle devenue nuqud ?"""
        c = self.commodities.get(commodity_name)
        return c.is_thaman if c else False

    def velocity_of_fulus(self, annual_transactions: float) -> float:
        """Vélocité du fulus = transactions / masse monétaire"""
        if self.currency_supply == 0:
            return 0.0
        return annual_transactions / self.currency_supply

    def get_total_stockpile_value(self) -> float:
        """Valeur totale des stockpiles"""
        total = 0.0
        for c in self.commodities.values():
            total += c.stockpile * c.current_price
        return total

    def get_status(self) -> Dict:
        """Retourne l'état complet du CRD"""
        return {
            'commodities': {
                name: {
                    'stockpile': c.stockpile,
                    'floor': c.floor_price,
                    'ceiling': c.ceiling_price,
                    'current': c.current_price,
                    'is_nuqud': c.is_thaman
                } for name, c in self.commodities.items()
            },
            'currency_supply': self.currency_supply,
            'total_stockpile_value': self.get_total_stockpile_value(),
            'total_interventions': len(self.intervention_history),
            'last_intervention': self.intervention_history[-1] if self.intervention_history else None
        }


# Exemple d'utilisation
if __name__ == "__main__":
    # Création du panier Grondona
    basket = [
        CommodityInBasket("Wheat", floor_price=180, ceiling_price=220, current_price=200),
        CommodityInBasket("Copper", floor_price=8000, ceiling_price=12000, current_price=9500),
        CommodityInBasket("Salt", floor_price=50, ceiling_price=70, current_price=60),
        CommodityInBasket("Rice", floor_price=300, ceiling_price=400, current_price=350)
    ]

    crd = GrondonaCRD(basket, initial_currency_supply=10000)

    print("=== CRD GRONDONA ===")
    print(f"Masse monétaire initiale: {crd.currency_supply}")

    # Simulation de prix
    prices = {
        "Wheat": 170,  # Sous le plancher → CRD achète
        "Copper": 11000,  # Au-dessus du plafond → CRD vend
        "Salt": 60,  # Dans la fourchette → pas d'intervention
        "Rice": 350  # Dans la fourchette → pas d'intervention
    }

    operations = crd.check_market_prices(prices)

    print(f"\nInterventions: {len(operations)}")
    for op in operations:
        print(f"  {op['action']} {op['commodity']}: {op['quantity']:.2f} unités")

    print(f"\nMasse monétaire finale: {crd.currency_supply:.2f}")
    print(f"Réserves: {crd.get_nuqud_reserves()}")

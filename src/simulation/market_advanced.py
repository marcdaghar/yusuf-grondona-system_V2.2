"""
Marché (Souq) – Main à main
===========================

Marché réel avec :
- Offres et demandes
- Appariement main à main
- Inspection du muhtassib
- CRD Grondona pour stabilisation
- Logistique réelle (délais, dégradation)

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time
import random


@dataclass
class Product:
    """Un produit échangeable sur le marché"""
    name: str
    base_price: float
    perishable: bool = False
    halal_certified: bool = False
    degradation_rate: float = 0.01  # par mois


@dataclass
class Transaction:
    """Une transaction enregistrée"""
    buyer: Any
    seller: Any
    product: str
    quantity: float
    price_per_unit: float
    total_price: float
    timestamp: float = field(default_factory=time.time)
    inspected: bool = False
    inspector: Optional[str] = None
    delivery_days: int = 0
    logistics_cost: float = 0.0


class Souq:
    """
    Marché main à main (pas d'enchères anonymes)
    """

    def __init__(self, name: str, location: str, crd=None, muhtassib=None):
        self.name = name
        self.location = location
        self.offers: List[Dict] = []
        self.demands: List[Dict] = []
        self.transactions: List[Transaction] = []
        self.crd = crd  # Commodity Reserve Department
        self.muhtassib = muhtassib  # Inspecteur

        self.price_history: Dict[str, List[float]] = {}
        self.volume_history: Dict[str, List[float]] = {}

    def add_offer(self, seller: Any, product: str,
                  quantity: float, price: float,
                  delivery_days: int = 0) -> None:
        """
        Ajoute une offre sur le marché
        """
        self.offers.append({
            "seller": seller,
            "product": product,
            "quantity": quantity,
            "price": price,
            "delivery_days": delivery_days,
            "timestamp": time.time()
        })

        # Enregistrement de l'historique des prix
        if product not in self.price_history:
            self.price_history[product] = []
        self.price_history[product].append(price)

    def add_demand(self, buyer: Any, product: str,
                   quantity: float, max_price: float) -> None:
        """
        Ajoute une demande sur le marché
        """
        self.demands.append({
            "buyer": buyer,
            "product": product,
            "quantity": quantity,
            "max_price": max_price,
            "timestamp": time.time()
        })

    def match(self, muhtassib=None, max_iterations: int = 1000) -> List[Transaction]:
        """
        Appariement offre/demande (main à main)
        Avec inspection du muhtassib
        """
        matched_transactions = []

        # Tri des offres par prix croissant, des demandes par prix décroissant
        self.offers.sort(key=lambda x: x["price"])
        self.demands.sort(key=lambda x: -x["max_price"])

        iterations = 0
        while self.offers and self.demands and iterations < max_iterations:
            iterations += 1

            offer = self.offers[0]
            demand = self.demands[0]

            if offer["product"] != demand["product"]:
                # Produits différents, on avance
                self.demands.pop(0)
                continue

            if offer["price"] > demand["max_price"]:
                # Prix trop élevé pour cette demande
                self.demands.pop(0)
                continue

            # Quantité échangée
            quantity = min(offer["quantity"], demand["quantity"])

            # Inspection du muhtassib (si présent)
            inspection_passed = True
            inspector_name = None

            if muhtassib:
                tx_to_inspect = {
                    'product': offer["product"],
                    'quantity': quantity,
                    'price_per_unit': offer["price"],
                    'declared_quantity': quantity,
                    'halal_certified': True,
                    'halal_valid': True
                }
                result = muhtassib.inspect_transaction(tx_to_inspect)
                inspection_passed = result['valid']
                inspector_name = muhtassib.name

                if not inspection_passed:
                    # Transaction rejetée
                    self.offers.pop(0)
                    self.demands.pop(0)
                    continue

            # Création de la transaction
            total_price = quantity * offer["price"]

            # Application du CRD (si présent)
            if self.crd:
                # Vérification des prix plancher/plafond
                floor = self.crd.commodities.get(offer["product"])
                if floor:
                    if offer["price"] < floor.floor_price:
                        # CRD achète
                        total_price = quantity * floor.floor_price
                    elif offer["price"] > floor.ceiling_price:
                        # CRD vend
                        total_price = quantity * floor.ceiling_price

            transaction = Transaction(
                buyer=demand["buyer"],
                seller=offer["seller"],
                product=offer["product"],
                quantity=quantity,
                price_per_unit=total_price / quantity,
                total_price=total_price,
                inspected=inspection_passed,
                inspector=inspector_name,
                delivery_days=offer["delivery_days"]
            )

            matched_transactions.append(transaction)
            self.transactions.append(transaction)

            # Mise à jour des quantités
            offer["quantity"] -= quantity
            demand["quantity"] -= quantity

            # Enregistrement du volume
            if offer["product"] not in self.volume_history:
                self.volume_history[offer["product"]] = []
            self.volume_history[offer["product"]].append(quantity)

            # Suppression des offres/demandes épuisées
            if offer["quantity"] <= 0:
                self.offers.pop(0)
            if demand["quantity"] <= 0:
                self.demands.pop(0)

        return matched_transactions

    def get_average_price(self, product: str) -> float:
        """Calcule le prix moyen d'un produit"""
        if product not in self.price_history or not self.price_history[product]:
            return 0.0
        return sum(self.price_history[product]) / len(self.price_history[product])

    def get_total_volume(self, product: str) -> float:
        """Calcule le volume total échangé d'un produit"""
        if product not in self.volume_history:
            return 0.0
        return sum(self.volume_history[product])

    def get_statistics(self) -> Dict:
        """Retourne les statistiques du marché"""
        return {
            'name': self.name,
            'location': self.location,
            'total_transactions': len(self.transactions),
            'active_offers': len(self.offers),
            'active_demands': len(self.demands),
            'products': list(self.price_history.keys()),
            'average_prices': {
                p: self.get_average_price(p) for p in self.price_history
            },
            'total_volumes': {
                p: self.get_total_volume(p) for p in self.volume_history
            }
        }


# Exemple d'utilisation
if __name__ == "__main__":
    from agents import Guilde, Commercant, Consommateur, MuhtassibAgent

    # Création du marché
    souq = Souq("Grand Souq", "Marseille")

    # Création des acteurs
    boulangerie = Guilde("Boulangerie Centrale", "Marseille")
    epicier = Commercant("Épicerie Al-Nour", "Marseille")
    consommateur = Consommateur("Claire")
    muhtassib = MuhtassibAgent("Ahmed", "Marseille")

    # Production
    boulangerie.produce("pain", 200)

    # Offre
    boulangerie.offer_to_souq(souq, "pain", 100, 2.0)

    # Demande
    epicier.buy_from_souq(souq, "pain", 50, 2.5)

    # Appariement
    transactions = souq.match(muhtassib)

    print(f"Transactions: {len(transactions)}")
    for tx in transactions:
        print(f"  {tx.product}: {tx.quantity} unités à {tx.price_per_unit:.2f} fulus")
        print(f"  Inspecté par: {tx.inspector}")

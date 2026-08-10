"""
Agents économiques – Guildes, Commerçants, Consommateurs
========================================================

Guildes : producteurs (ateliers, entrepôts)
Commerçants : distributeurs (achat/revente main à main)
Consommateurs : utilisateurs finaux
Muhtassib : inspecteur du marché (hérité de core/hisba)

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import random
import time


@dataclass
class Guilde:
    """
    Guilde productive (atelier, entrepôt collectif)
    """
    name: str
    location: str
    production_capacity: float = 1000.0
    fulus_balance: float = 0.0
    nuqud_balance: float = 0.0  # or/argent
    workers: int = 5
    skills: Dict[str, float] = field(default_factory=lambda: {"production": 0.7, "logistics": 0.5})
    stock: Dict[str, float] = field(default_factory=dict)

    def produce(self, product_name: str, quantity: float) -> float:
        """
        Produit une quantité d'un bien
        """
        if quantity <= self.production_capacity:
            self.stock[product_name] = self.stock.get(product_name, 0) + quantity
            # Coût de production (salaires des ouvriers)
            cost = quantity * 0.6  # Coût unitaire simplifié
            self.fulus_balance -= cost
            return quantity
        return 0.0

    def offer_to_souq(self, souq: 'Souq', product_name: str,
                      quantity: float, price: float) -> bool:
        """
        Propose un bien sur le marché
        """
        if self.stock.get(product_name, 0) >= quantity:
            souq.add_offer(self, product_name, quantity, price)
            self.stock[product_name] -= quantity
            return True
        return False

    def receive_payment(self, amount: float, currency: str = "fulus") -> None:
        """Reçoit un paiement"""
        if currency == "fulus":
            self.fulus_balance += amount
        elif currency == "nuqud":
            self.nuqud_balance += amount

    def get_summary(self) -> Dict:
        """Résumé de la guilde"""
        return {
            'name': self.name,
            'location': self.location,
            'workers': self.workers,
            'fulus_balance': self.fulus_balance,
            'nuqud_balance': self.nuqud_balance,
            'stock': self.stock.copy(),
            'skills': self.skills.copy()
        }


@dataclass
class Commercant:
    """
    Commerçant (achat/revente en détail, main à main)
    """
    name: str
    location: str
    fulus: float = 1000.0
    nuqud: float = 0.0
    stock: Dict[str, float] = field(default_factory=dict)
    markup: float = 1.3  # Marge bénéficiaire
    last_buy_price: float = 0.0
    transaction_history: List[Dict] = field(default_factory=list)

    def buy_from_souq(self, souq: 'Souq', product_name: str,
                      quantity: float, max_price: float) -> bool:
        """
        Achète un bien sur le marché
        """
        souq.add_demand(self, product_name, quantity, max_price)
        return True

    def resell(self, product_name: str, quantity: float) -> float:
        """
        Revend un bien en détail
        """
        if self.stock.get(product_name, 0) >= quantity:
            self.stock[product_name] -= quantity
            price = self.markup * self.last_buy_price
            revenue = price * quantity
            self.fulus += revenue
            self.transaction_history.append({
                'type': 'sale',
                'product': product_name,
                'quantity': quantity,
                'price': price,
                'revenue': revenue,
                'timestamp': time.time()
            })
            return revenue
        return 0.0

    def receive_goods(self, product_name: str, quantity: float,
                      price_per_unit: float) -> None:
        """Reçoit des marchandises (après achat)"""
        self.stock[product_name] = self.stock.get(product_name, 0) + quantity
        self.last_buy_price = price_per_unit
        self.fulus -= quantity * price_per_unit

    def get_summary(self) -> Dict:
        """Résumé du commerçant"""
        return {
            'name': self.name,
            'location': self.location,
            'fulus': self.fulus,
            'nuqud': self.nuqud,
            'stock': self.stock.copy(),
            'markup': self.markup,
            'transactions': len(self.transaction_history)
        }


@dataclass
class Consommateur:
    """
    Consommateur final
    """
    name: str
    fulus: float = 500.0
    nuqud: float = 0.0
    utility: float = 0.0
    consumption_history: List[Dict] = field(default_factory=list)
    preferences: Dict[str, float] = field(default_factory=lambda: {
        'food': 0.4,
        'housing': 0.2,
        'health': 0.15,
        'education': 0.1,
        'social': 0.05,
        'luxury': 0.1
    })

    def consume(self, product_name: str, quantity: float,
                price_per_unit: float) -> bool:
        """
        Consomme un bien
        """
        total_price = quantity * price_per_unit
        if self.fulus >= total_price:
            self.fulus -= total_price
            self.utility += quantity * 10  # Satisfaction
            self.consumption_history.append({
                'product': product_name,
                'quantity': quantity,
                'price': price_per_unit,
                'total': total_price,
                'timestamp': time.time()
            })
            return True
        return False

    def get_utility(self) -> float:
        """Retourne l'utilité totale"""
        return self.utility

    def get_summary(self) -> Dict:
        """Résumé du consommateur"""
        return {
            'name': self.name,
            'fulus': self.fulus,
            'nuqud': self.nuqud,
            'utility': self.utility,
            'consumptions': len(self.consumption_history)
        }


@dataclass
class MuhtassibAgent:
    """
    Muhtassib (inspecteur du marché)
    Hérite des fonctionnalités de core/hisba mais adapté à la simulation
    """
    name: str
    jurisdiction: str
    reputation: float = 50.0
    inspections: List[Dict] = field(default_factory=list)

    def inspect_transaction(self, transaction: Dict, tolerance: float = 0.02) -> Dict:
        """
        Inspecte une transaction
        """
        result = {
            'transaction': transaction,
            'inspector': self.name,
            'valid': True,
            'issues': []
        }

        # Vérification du prix
        price = transaction.get('price_per_unit', 0)
        if price < 0:
            result['valid'] = False
            result['issues'].append('prix négatif')
            result['severity'] = 'critical'

        # Vérification de la quantité
        quantity = transaction.get('quantity', 0)
        declared = transaction.get('declared_quantity', quantity)
        if quantity > 0 and abs(quantity - declared) / declared > tolerance:
            result['valid'] = False
            result['issues'].append('fraude sur la quantité')
            result['severity'] = 'high'

        # Vérification halal (si applicable)
        if transaction.get('halal_certified', False):
            if not transaction.get('halal_valid', True):
                result['valid'] = False
                result['issues'].append('certificat halal invalide')
                result['severity'] = 'high'

        # Mise à jour de la réputation
        if result['valid']:
            self.reputation = min(100, self.reputation + 0.5)
        else:
            self.reputation = max(0, self.reputation - 2.0)

        self.inspections.append(result)
        return result

    def get_summary(self) -> Dict:
        """Résumé du muhtassib"""
        valid = sum(1 for i in self.inspections if i['valid'])
        return {
            'name': self.name,
            'jurisdiction': self.jurisdiction,
            'reputation': self.reputation,
            'total_inspections': len(self.inspections),
            'valid_inspections': valid,
            'compliance_rate': valid / len(self.inspections) if self.inspections else 1.0
        }


# Exemple d'utilisation
if __name__ == "__main__":
    # Création des agents
    guilde = Guilde("Boulangerie Centrale", "Marseille", production_capacity=1000)
    commercant = Commercant("Épicerie Al-Nour", "Marseille")
    consommateur = Consommateur("Claire")
    muhtassib = MuhtassibAgent("Ahmed", "Marseille")

    # Production
    guilde.produce("pain", 200)
    print(f"Guilde: stock pain = {guilde.stock.get('pain', 0)}")

    # Transaction simulée
    tx = {
        'product': 'pain',
        'quantity': 10,
        'price_per_unit': 2.0,
        'declared_quantity': 10,
        'halal_certified': True,
        'halal_valid': True
    }

    # Inspection
    result = muhtassib.inspect_transaction(tx)
    print(f"Inspection: {result['valid']}")
    print(f"Réputation du muhtassib: {muhtassib.reputation:.1f}")

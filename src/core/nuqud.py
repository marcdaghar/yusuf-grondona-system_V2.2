"""
Nuqud (نقود) – Argent mesurable et pesable
===========================================

Selon la loi islamique, le nuqud :
1. Est soumis à des règles STRICTES sur le riba (usure)
2. Ne peut pas être échangé avec un surplus (riba al-fadl)
3. Ne peut pas être échangé avec délai (riba al-nasia)
4. Sert d'ÉTALON DE MESURE et de RÉSERVE DE VALEUR

Exemples : Or (dinar), Argent (dirham), Sel (dans l'empire romain)

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


class CommodityStatus(Enum):
    """Statut d'une commodité dans le système"""
    NUQUD = "nuqud"              # Argent mesurable/pesable (riba strict)
    FULUS = "fulus"              # Monnaie de vélocité (riba allégé)
    GRONDONA_BASKET = "grondona"  # Dans le panier (statut hybride)


@dataclass
class NuqudCommodity:
    """
    Une commodité qui entre dans la catégorie nuqud.
    Dès qu'une commodité entre dans le système Grondona,
    elle devient :
    1. Étalon de mesure de la valeur
    2. Réserve de valeur
    3. SORT de la monnaie courante (n'a plus vocation à circuler)
    """
    name: str
    name_arabic: str
    is_primary_thaman: bool  # Or/argent = primus inter pares
    storage_years_max: Optional[float] = None
    degradation_rate: float = 0.0  # Perte annuelle (0% pour or/argent/sel gemme)
    historical_context: str = ""
    riba_rules_strict: bool = True  # Nuqud = règles strictes

    def real_interest_rate(self, storage_days: int) -> float:
        """
        Taux d'intérêt réel du nuqud
        Pour or/argent/sel : ~0%
        Pour autres commodités rentrant dans Grondona : négatif
        """
        years = storage_days / 365
        total_loss = self.degradation_rate * years
        return -total_loss


# Les nuqud fondamentaux (primus inter pares)
PRIMARY_NUQUD = [
    NuqudCommodity(
        name="Gold",
        name_arabic="ذهبي (Dahabi)",
        is_primary_thaman=True,
        storage_years_max=None,
        degradation_rate=0.0,
        historical_context="The Golden Constant (Jastram, 1977) : 400 ans de stabilité"
    ),
    NuqudCommodity(
        name="Silver",
        name_arabic="فضي (Fiddi)",
        is_primary_thaman=True,
        storage_years_max=None,
        degradation_rate=0.0,
        historical_context="Le dirham islamique, monnaie du Prophète"
    ),
]


@dataclass
class Nuqud:
    """
    Représente une quantité de nuqud (or ou argent).
    """
    metal_type: str  # 'gold' ou 'silver'
    weight_grams: float
    owner: Optional[str] = None
    purity: float = 0.917  # 22 carats pour l'or, par défaut

    def value_in_grams_of_silver(self) -> float:
        """Convertit la valeur en grammes d'argent équivalent"""
        if self.metal_type == 'gold':
            # Ratio historique 1:10 (or/argent) – ajustable
            return self.weight_grams * 10
        return self.weight_grams

    def is_above_nisab(self) -> bool:
        """
        Vérifie si le nuqud dépasse le seuil du Nisab.
        Nisab or = 85g, Nisab argent = 595g
        """
        if self.metal_type == 'gold':
            return self.weight_grams >= 85.0
        else:  # silver
            return self.weight_grams >= 595.0

    def zakat_due(self) -> float:
        """
        Calcule la Zakat due sur ce nuqud (2.5%).
        La Zakat n'est due que si le Nisab est atteint.
        """
        if not self.is_above_nisab():
            return 0.0
        return self.weight_grams * 0.025

    def __repr__(self) -> str:
        return f"Nuqud({self.metal_type}, {self.weight_grams}g, owner={self.owner})"


class NuqudSystem:
    """
    Système de gestion du nuqud (argent mesurable/pesable)

    RÈGLE D'OR : Dès qu'une commodité entre dans le système Grondona,
    elle devient nuqud (étalon de mesure + réserve de valeur),
    et SORT de la monnaie courante.

    La monnaie courante (fulus) n'a alors qu'une fonction :
    LA VÉLOCITÉ MARCHANDE.
    """

    def __init__(self):
        self.nuqud_reserves: Dict[str, float] = {}
        self.nuqud_in_system: Dict[str, NuqudCommodity] = {}

        # Initialiser avec or et argent
        for n in PRIMARY_NUQUD:
            self.nuqud_in_system[n.name] = n
            self.nuqud_reserves[n.name] = 0.0

        self.transaction_history: List[Dict] = []

    def add_to_nuqud(self, commodity: NuqudCommodity, initial_reserve: float) -> Dict:
        """
        Ajoute une commodité au nuqud.
        Dès cet instant, cette commodité :
        - Sert d'étalon de mesure
        - Sert de réserve de valeur
        - N'est PLUS de la monnaie courante
        """
        self.nuqud_in_system[commodity.name] = commodity
        self.nuqud_reserves[commodity.name] = initial_reserve

        return {
            'status': 'added_to_nuqud',
            'commodity': commodity.name,
            'message': f"{commodity.name} est désormais un étalon de mesure et une réserve de valeur. "
                       f"Elle n'est plus de la monnaie courante.",
            'riba_rules': 'strict (al-fadl et al-nasia interdits)',
            'reserve': initial_reserve
        }

    def get_reserve(self, commodity: str) -> float:
        """Retourne la réserve d'une commodité"""
        return self.nuqud_reserves.get(commodity, 0.0)

    def get_total_reserve_value(self, in_terms_of: str = "Gold") -> float:
        """Retourne la valeur totale des réserves en équivalent or"""
        total = 0.0
        for name, amount in self.nuqud_reserves.items():
            commodity = self.nuqud_in_system.get(name)
            if commodity:
                if commodity.name == "Gold":
                    total += amount
                elif commodity.name == "Silver":
                    total += amount / 10  # ratio 1:10
                else:
                    # Autres commodités : estimation simplifiée
                    total += amount * 0.01
        return total

    def store_value(self, commodity: str, quantity: float) -> Dict:
        """
        Stocke de la valeur dans le nuqud (réserve)
        À l'inverse du fulus, le nuqud est thésaurisable
        """
        if commodity not in self.nuqud_in_system:
            return {
                'error': f"{commodity} n'est pas dans le nuqud. "
                         f"Seul le nuqud peut servir de réserve de valeur."
            }

        self.nuqud_reserves[commodity] = self.nuqud_reserves.get(commodity, 0) + quantity

        return {
            'status': 'value_stored',
            'commodity': commodity,
            'quantity': quantity,
            'total_reserve': self.nuqud_reserves[commodity],
            'message': f"{quantity} de {commodity} ajouté à la réserve de valeur. "
                       f"Cette marchandise ne circule plus comme monnaie."
        }

    def withdraw_value(self, commodity: str, quantity: float) -> Dict:
        """Retire de la valeur du nuqud (réserve)"""
        if commodity not in self.nuqud_in_system:
            return {'error': f"{commodity} n'est pas dans le nuqud."}

        current = self.nuqud_reserves.get(commodity, 0)
        if current < quantity:
            return {'error': f"Réserve insuffisante. Disponible: {current}"}

        self.nuqud_reserves[commodity] = current - quantity

        return {
            'status': 'value_withdrawn',
            'commodity': commodity,
            'quantity': quantity,
            'remaining_reserve': self.nuqud_reserves[commodity]
        }

    def validate_riba_exchange(self, commodity: str,
                               quantity1: float, quantity2: float,
                               is_same_species: bool,
                               has_delay: bool) -> Tuple[bool, str]:
        """
        Vérifie si un échange de nuqud viole les règles du riba

        Règles strictes pour le nuqud :
        1. Interdiction du riba al-fadl (surplus dans échange même espèce)
        2. Interdiction du riba al-nasia (délai dans l'échange)
        """
        if commodity not in self.nuqud_in_system:
            return True, "Pas un échange de nuqud (règles assouplies)"

        if is_same_species and abs(quantity1 - quantity2) > 0.001:
            return False, f"RIBA AL-FADL : Échange inégal de {commodity} contre {commodity}"

        if has_delay:
            return False, f"RIBA AL-NASIA : Délai dans l'échange de {commodity}"

        return True, "Échange conforme aux règles du nuqud"

    def get_nuqud_status(self) -> Dict:
        """Retourne l'état complet du système nuqud"""
        return {
            'reserves': self.nuqud_reserves.copy(),
            'commodities': {k: {
                'name': v.name,
                'arabic': v.name_arabic,
                'is_primary': v.is_primary_thaman,
                'degradation_rate': v.degradation_rate,
                'max_storage_years': v.storage_years_max
            } for k, v in self.nuqud_in_system.items()},
            'total_reserve_value_gold_eq': self.get_total_reserve_value(),
            'total_transactions': len(self.transaction_history)
        }


# Exemple d'utilisation
if __name__ == "__main__":
    system = NuqudSystem()
    print("=== SYSTÈME NUQUD ===")
    print(f"Réserves initiales: {system.get_nuqud_status()['reserves']}")

    # Ajout d'une réserve d'or
    system.store_value("Gold", 1000.0)
    print(f"Après ajout d'or: {system.get_nuqud_status()['reserves']}")

    # Test de riba
    valid, msg = system.validate_riba_exchange("Gold", 10.0, 12.0, True, False)
    print(f"Échange d'or 10g contre 12g : {msg}")

    valid, msg = system.validate_riba_exchange("Gold", 10.0, 10.0, True, True)
    print(f"Échange d'or 10g contre 10g avec délai : {msg}")

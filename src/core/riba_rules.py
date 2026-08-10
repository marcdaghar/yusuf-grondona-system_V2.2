"""
Règles du Riba (الربا)
======================

Distinction fondamentale entre Nuqud et Fulus

RÉFÉRENCES CORANIQUES :
- Sourate Al-Baqarah (2:275-279) : Interdiction du riba
- Sourate Al-Imran (3:130) : "Ne pratiquez pas le riba multiplié"

La jurisprudence islamique distingue :
1. RIBA AL-FADL : Surplus dans l'échange de biens de même espèce
2. RIBA AL-NASIA : Délai dans l'échange

License: CC BY-SA 4.0 – Marc Daghar
"""

from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import time


class AssetClass(Enum):
    """Classification des biens selon la jurisprudence islamique"""
    NUQUD = "nuqud"      # Or, argent, matière première monétaire (riba strict)
    FULUS = "fulus"      # Monnaie courante (riba assoupli)
    UROOD = "urood"      # Marchandises (pas de riba entre espèces différentes)


@dataclass
class RibaRule:
    """Règle de riba pour une classe d'actifs"""
    asset_class: AssetClass
    al_fadl_prohibited: bool   # Surplus interdit ?
    al_nasia_prohibited: bool  # Délai interdit ?
    max_surplus_percent: float = 0.0  # Si autorisé, quelle limite ?
    note: str = ""


# Les règles selon la classe d'actifs
RIBA_RULES = {
    AssetClass.NUQUD: RibaRule(
        asset_class=AssetClass.NUQUD,
        al_fadl_prohibited=True,   # Riba al-fadl STRICTEMENT interdit
        al_nasia_prohibited=True,  # Riba al-nasia STRICTEMENT interdit
        max_surplus_percent=0.0,
        note="Or, argent : échange égal et immédiat obligatoire"
    ),
    AssetClass.FULUS: RibaRule(
        asset_class=AssetClass.FULUS,
        al_fadl_prohibited=False,   # Autorise un petit surplus (jusqu'à 5%)
        al_nasia_prohibited=False,  # Autorise le délai
        max_surplus_percent=0.05,   # 5% max pour faciliter les échanges
        note="Monnaie de vélocité : règles assouplies pour fluidifier les transactions"
    ),
    AssetClass.UROOD: RibaRule(
        asset_class=AssetClass.UROOD,
        al_fadl_prohibited=False,  # Pas de riba entre espèces différentes
        al_nasia_prohibited=False,  # Le délai est autorisé dans le commerce
        max_surplus_percent=None,
        note="Marchandises : pas d'interdiction de riba entre biens différents"
    )
}


@dataclass
class RibaViolation:
    """Enregistrement d'une violation des règles du riba"""
    type: str  # 'riba_al_fadl', 'riba_al_nasia', 'excess_surplus'
    asset_class: str
    message: str
    timestamp: float = field(default_factory=time.time)


class RibaController:
    """
    Contrôleur des règles du riba
    Applique les règles strictes au nuqud, assouplies au fulus
    """

    def __init__(self):
        self.violations_history: List[RibaViolation] = []

    def check_exchange(self,
                       asset_class: AssetClass,
                       quantity_given: float,
                       quantity_received: float,
                       same_species: bool,
                       has_delay: bool) -> Tuple[bool, str]:
        """
        Vérifie si un échange respecte les règles du riba

        Returns:
            (is_valid, message)
        """
        rules = RIBA_RULES.get(asset_class)
        if not rules:
            return True, "Classe d'actif non reconnue"

        # Vérification riba al-fadl
        if same_species and rules.al_fadl_prohibited:
            if abs(quantity_given - quantity_received) > 0.001:
                violation = RibaViolation(
                    type='riba_al_fadl',
                    asset_class=asset_class.value,
                    message=f"Surplus de {quantity_received - quantity_given:.4f} interdit"
                )
                self.violations_history.append(violation)
                return False, violation.message

        # Vérification riba al-nasia
        if has_delay and rules.al_nasia_prohibited:
            violation = RibaViolation(
                type='riba_al_nasia',
                asset_class=asset_class.value,
                message="Délai dans l'échange interdit"
            )
            self.violations_history.append(violation)
            return False, violation.message

        # Vérification des limites de surplus pour le fulus
        if asset_class == AssetClass.FULUS and same_species:
            if rules.max_surplus_percent is not None:
                if quantity_given > 0:
                    surplus_ratio = abs(quantity_received - quantity_given) / quantity_given
                    if surplus_ratio > rules.max_surplus_percent:
                        violation = RibaViolation(
                            type='excess_surplus',
                            asset_class=asset_class.value,
                            message=f"Surplus excessif : {surplus_ratio:.1%} > {rules.max_surplus_percent:.1%}"
                        )
                        self.violations_history.append(violation)
                        return False, violation.message

        return True, "Échange conforme aux règles du riba"

    def get_violations(self, limit: int = 10) -> List[Dict]:
        """Retourne les dernières violations"""
        return [
            {
                'type': v.type,
                'asset_class': v.asset_class,
                'message': v.message,
                'timestamp': v.timestamp
            }
            for v in self.violations_history[-limit:]
        ]

    def get_statistics(self) -> Dict:
        """Retourne les statistiques des violations"""
        types = {}
        classes = {}

        for v in self.violations_history:
            types[v.type] = types.get(v.type, 0) + 1
            classes[v.asset_class] = classes.get(v.asset_class, 0) + 1

        return {
            'total_violations': len(self.violations_history),
            'by_type': types,
            'by_asset_class': classes,
            'most_recent': self.violations_history[-1] if self.violations_history else None
        }

    def get_nuqud_rules_summary(self) -> Dict:
        """Résumé des règles STRICTES pour le nuqud"""
        rules = RIBA_RULES[AssetClass.NUQUD]
        return {
            'asset_class': 'NUQUD (argent mesurable/pesable)',
            'prohibited_practices': [
                'RIBA AL-FADL : Tout surplus dans l\'échange de même espèce',
                'RIBA AL-NASIA : Tout délai dans l\'échange'
            ],
            'examples': [
                "Échange d'or contre or : quantités égales et immédiates obligatoires",
                "Échange d'argent contre argent : immédiat et égal",
                "Échange de blé contre blé en Grondona : après entrée dans le système, devient nuqud"
            ],
            'threshold': '0% surplus'
        }

    def get_fulus_rules_summary(self) -> Dict:
        """Résumé des règles ASSOUPLIES pour le fulus"""
        rules = RIBA_RULES[AssetClass.FULUS]
        return {
            'asset_class': 'FULUS (monnaie de vélocité)',
            'allowed_practices': [
                f'RIBA AL-FADL : Surplus modéré autorisé jusqu\'à {rules.max_surplus_percent:.0%}',
                'RIBA AL-NASIA : Délai autorisé'
            ],
            'examples': [
                "Échange de fulus contre fulus : petit surplus possible",
                "Paiement différé autorisé pour faciliter les échanges",
                "La monnaie de vélocité n'est ni étalon, ni réserve"
            ],
            'economic_function': 'SIGNAL AUX AGENTS (rationalité limitée, asymétrie des données)'
        }


# Exemple d'utilisation
if __name__ == "__main__":
    controller = RibaController()

    print("=== RÈGLES DU RIBA ===")

    # Test : échange de nuqud inégal
    valid, msg = controller.check_exchange(
        AssetClass.NUQUD,
        quantity_given=10.0,
        quantity_received=12.0,
        same_species=True,
        has_delay=False
    )
    print(f"Échange d'or 10g contre 12g : {msg}")

    # Test : échange de nuqud avec délai
    valid, msg = controller.check_exchange(
        AssetClass.NUQUD,
        quantity_given=10.0,
        quantity_received=10.0,
        same_species=True,
        has_delay=True
    )
    print(f"Échange d'or avec délai : {msg}")

    # Test : échange de fulus avec surplus modéré
    valid, msg = controller.check_exchange(
        AssetClass.FULUS,
        quantity_given=100.0,
        quantity_received=103.0,
        same_species=True,
        has_delay=True
    )
    print(f"Échange de fulus 100 contre 103 : {msg}")

    # Test : échange de fulus avec surplus excessif
    valid, msg = controller.check_exchange(
        AssetClass.FULUS,
        quantity_given=100.0,
        quantity_received=110.0,
        same_species=True,
        has_delay=True
    )
    print(f"Échange de fulus 100 contre 110 : {msg}")

    print("\n=== STATISTIQUES ===")
    print(controller.get_statistics())

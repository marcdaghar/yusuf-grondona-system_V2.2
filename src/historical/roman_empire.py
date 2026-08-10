"""
Roman Empire – Sel, Via Salaria, salarium
=========================================

L'Empire romain a développé un système monétaire basé sur :
- Le sel (Via Salaria) comme réserve de valeur
- Le salarium (ration de sel) → salaire
- Le bimétallisme (or/argent) dans l'empire tardif
- Les routes commerciales comme corridors logistiques

Leçons :
1. Une commodité non périssable peut servir de réserve de valeur
2. Le sel a été une monnaie stable pendant des siècles
3. Les routes (Via Salaria) sont l'équivalent antique des corridors BRI

Référence : Bloch, M. (1925). Le sel dans l'histoire.

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class RomanCommodity:
    """
    Une commodité dans l'Empire romain
    """
    name: str
    name_la: str
    degradation_rate: float
    storage_cost: float
    fraud_rate: float
    storage_years_max: Optional[float]
    layer: str  # thaman, semi_thaman, currency
    historical_significance: str
    roman_context: str

    def real_interest_rate(self, storage_days: int) -> float:
        """Taux d'intérêt réel"""
        years = storage_days / 365
        total_loss = (self.degradation_rate + self.storage_cost + self.fraud_rate) * years
        return -total_loss


# Commodités romaines
ROMAN_COMMODITIES = {
    'salt_rock': RomanCommodity(
        name="Sel gemme",
        name_la="Sal",
        degradation_rate=0.001,
        storage_cost=0.001,
        fraud_rate=0.001,
        storage_years_max=None,
        layer="semi_thaman",
        historical_significance="Via Salaria, fondement du salarium",
        roman_context="Route du sel Rome-Adriatique, salaire des légionnaires"
    ),
    'salt_sea': RomanCommodity(
        name="Sel marin",
        name_la="Sal marinus",
        degradation_rate=0.005,
        storage_cost=0.005,
        fraud_rate=0.002,
        storage_years_max=None,
        layer="semi_thaman",
        historical_significance="Sel de qualité, exporté dans tout l'empire",
        roman_context="Produit dans les salins méditerranéens"
    ),
    'gold': RomanCommodity(
        name="Or",
        name_la="Aurum",
        degradation_rate=0.0,
        storage_cost=0.0,
        fraud_rate=0.0,
        storage_years_max=None,
        layer="thaman",
        historical_significance="Aureus, monnaie d'or",
        roman_context="Monnaie impériale, réserve de valeur"
    ),
    'silver': RomanCommodity(
        name="Argent",
        name_la="Argentum",
        degradation_rate=0.0,
        storage_cost=0.0,
        fraud_rate=0.0,
        storage_years_max=None,
        layer="thaman",
        historical_significance="Denarius, monnaie d'argent",
        roman_context="Monnaie des transactions courantes"
    ),
    'wheat': RomanCommodity(
        name="Blé",
        name_la="Triticum",
        degradation_rate=0.20,
        storage_cost=0.03,
        fraud_rate=0.02,
        storage_years_max=3.0,
        layer="currency",
        historical_significance="Annona, distribution de blé",
        roman_context="Paiement en nature, dole"
    )
}


class RomanEmpireAnalysis:
    """
    Analyse du système monétaire romain
    """

    def __init__(self):
        self.commodities = ROMAN_COMMODITIES

    def get_commodity(self, name: str) -> Optional[RomanCommodity]:
        """Récupère une commodité par son nom"""
        for key, value in self.commodities.items():
            if key == name or value.name == name:
                return value
        return None

    def linguistic_lesson(self) -> str:
        """
        Leçon linguistique : salarium → salaire
        """
        return """
        === LEÇON LINGUISTIQUE : SALARIUM ===

        Le mot latin "sal" (sel) a donné :

        1. "salarium" → la ration de sel des légionnaires
        2. "salarium" → le salaire en français
        3. "salary" → le salaire en anglais
        4. "salario" → le salaire en espagnol/italien

        POURQUOI ?

        Le sel était :
        - INDISPENSABLE à la vie
        - NON PÉRISSABLE (stockable comme l'or)
        - DIVISIBLE (en petites unités)
        - ÉCHANGEABLE (reconnu par tous)

        L'empire romain ne payait pas ses soldats en "monnaie" abstraite.
        Il les payait en ARGENT RÉEL — du sel.

        La langue a gardé la mémoire de cette économie juste.
        Le "salaire" moderne n'a plus aucun lien avec le sel.
        C'est pourquoi il n'a plus la même stabilité.

        APPLICATION AU SYSTÈME YUSUF-GRONDONA :
        - Le sel peut entrer dans le panier Grondona
        - Il sert de semi-thaman (étalon secondaire)
        - Il illustre la distinction nuqud/fulus
        """

    def via_salaria_route(self) -> Dict:
        """
        Description de la Via Salaria (route du sel)
        """
        return {
            'name': 'Via Salaria',
            'description': 'Route du sel reliant Rome à la mer Adriatique',
            'length_km': 250,
            'origin': 'Rome',
            'destination': 'Porto d\'Ascoli (Adriatique)',
            'historical_period': "IVe siècle av. J.-C. - Ve siècle ap. J.-C.",
            'significance': "Premier corridor logistique, ancêtre des corridors BRI",
            'lesson': "Les corridors logistiques sont essentiels à la circulation monétaire"
        }

    def compare_with_bri(self) -> Dict:
        """
        Compare la Via Salaria avec les corridors BRI
        """
        return {
            'via_salaria': {
                'type': 'Route terrestre',
                'commodity': 'Sel',
                'function': 'Transport du sel de l\'Adriatique à Rome',
                'length': '250 km',
                'duration': '7-10 jours'
            },
            'bri_corridor': {
                'type': 'Routes, rails, ports',
                'commodity': 'Nuqud (or/argent) + Fulus',
                'function': 'Transport inter-zones',
                'length': 'Milliers de km',
                'duration': 'Variables'
            },
            'continuity': {
                'principle': 'La logistique est la colonne vertébrale de l\'économie',
                'lesson': 'Les corridors logistiques créent la confiance monétaire',
                'innovation': 'Le corridor BRI connecte les économies comme la Via Salaria'
            }
        }

    def get_timeline(self) -> List[Dict]:
        """
        Chronologie du système monétaire romain
        """
        return [
            {
                'period': 'République (509-27 av. J.-C.)',
                'system': 'Paiement en sel (salarium), début du bimétallisme',
                'key_event': 'Introduction du denarius (argent)'
            },
            {
                'period': 'Empire (27 av. J.-C. - 284 ap. J.-C.)',
                'system': 'Bimétallisme or/argent, Via Salaria, annona',
                'key_event': 'Auguste réforme la monnaie (aureus, denarius)'
            },
            {
                'period': 'Empire tardif (284-476 ap. J.-C.)',
                'system': 'Dévaluation, inflation, crise monétaire',
                'key_event': 'Dioclétien réforme le système (solidus)'
            }
        ]

    def get_summary(self) -> Dict:
        """Résumé de l'analyse romaine"""
        return {
            'commodities': [
                {
                    'name': c.name,
                    'latin': c.name_la,
                    'layer': c.layer,
                    'degradation': f"{c.degradation_rate:.1%}",
                    'interest_rate_1y': f"{c.real_interest_rate(365):.1%}"
                }
                for c in self.commodities.values()
            ],
            'linguistic_lesson': self.linguistic_lesson(),
            'via_salaria': self.via_salaria_route(),
            'comparison_with_bri': self.compare_with_bri(),
            'timeline': self.get_timeline()
        }


# Exemple d'utilisation
if __name__ == "__main__":
    analysis = RomanEmpireAnalysis()

    print("=== EMPIRE ROMAIN – SEL ET SALARIUM ===")
    print(analysis.linguistic_lesson())

    print("\n=== COMMODITÉS ROMAINES ===")
    for name, commodity in analysis.commodities.items():
        print(f"\n{commodity.name} ({commodity.name_la})")
        print(f"  Couche: {commodity.layer}")
        print(f"  Dégradation: {commodity.degradation_rate:.1%}/an")
        print(f"  Taux d'intérêt réel (1 an): {commodity.real_interest_rate(365):.1%}")
        print(f"  Contexte: {commodity.roman_context}")

    print("\n=== VIA SALARIA ===")
    via = analysis.via_salaria_route()
    print(f"{via['name']}: {via['description']}")
    print(f"  Longueur: {via['length_km']} km")
    print(f"  {via['origin']} → {via['destination']}")

    print("\n=== COMPARAISON AVEC BRI ===")
    comparison = analysis.compare_with_bri()
    print(f"Via Salaria: {comparison['via_salaria']}")
    print(f"BRI Corridor: {comparison['bri_corridor']}")

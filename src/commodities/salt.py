"""
Salt – Sel, Via Salaria, salarium romain
========================================

Le sel a été une forme de monnaie pendant des millénaires :
- Via Salaria : route du sel à Rome
- Salarium : ration de sel des soldats → salaire
- Stockable éternellement (sel gemme)
- Reconnu universellement

Référence : Bloch, M. (1925). Le sel dans l'histoire.

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class SaltType:
    """
    Caractéristiques d'un type de sel
    """
    name: str
    name_fr: str
    degradation_rate: float
    storage_cost: float
    fraud_rate: float
    storage_years_max: Optional[float] = None
    layer: str = "semi_thaman"  # semi_thaman, grondona_basket, currency_velocity
    historical_context: str = ""
    roman_context: str = ""

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


# Types de sel
SALT_TYPES = {
    'rock_salt': SaltType(
        name="rock_salt",
        name_fr="Sel gemme",
        degradation_rate=0.000,  # 0% par an
        storage_cost=0.001,       # 0.1% par an
        fraud_rate=0.001,         # 0.1% par an
        storage_years_max=None,   # Éternel
        layer="semi_thaman",
        historical_context="Sel gemme de Pologne (Wieliczka), exploité depuis le XIIIe siècle",
        roman_context="Via Salaria : route du sel Rome-Adriatique"
    ),
    'sea_salt_dry': SaltType(
        name="sea_salt_dry",
        name_fr="Sel marin sec",
        degradation_rate=0.005,   # 0.5% par an
        storage_cost=0.005,       # 0.5% par an
        fraud_rate=0.002,         # 0.2% par an
        storage_years_max=None,   # Décennies
        layer="semi_thaman",
        historical_context="Sel de Guérande, produit depuis 2000 ans",
        roman_context="Exporté dans tout l'empire, sel de qualité"
    ),
    'wet_salt': SaltType(
        name="wet_salt",
        name_fr="Sel humide",
        degradation_rate=0.02,    # 2% par an
        storage_cost=0.01,        # 1% par an
        fraud_rate=0.01,          # 1% par an
        storage_years_max=10.0,   # Max une décennie
        layer="grondona_basket",
        historical_context="Sel de mangrove (Vietnam, Afrique)",
        roman_context="Utilisé localement, moins transporté"
    ),
    'brine': SaltType(
        name="brine",
        name_fr="Saumure",
        degradation_rate=0.99,    # Perte quasi totale
        storage_cost=0.50,        # 50% par mois
        fraud_rate=0.05,          # 5%
        storage_years_max=0.1,    # 1-2 mois max
        layer="currency_velocity",
        historical_context="Saumure pour conservation (olives, fromages)",
        roman_context="Utilisée sur place, jamais transportée loin"
    )
}


class SaltCommodityAnalysis:
    """
    Analyse du sel comme commodité monétaire
    """

    def __init__(self):
        self.salt_types = SALT_TYPES

    def get_salt_type(self, name: str) -> Optional[SaltType]:
        """Récupère un type de sel par son nom"""
        return self.salt_types.get(name)

    def linguistic_lesson(self) -> str:
        """
        Leçon économique de la philologie
        """
        return """
        === LEÇON DU "SAL" ROMAIN ===

        Le mot latin "sal" (sel) a donné "salarium" (ration de sel des soldats)
        Le "salarium" est devenu "salaire" en français, "salary" en anglais.

        Pourquoi ? Parce que le sel était :
        1. INDISPENSABLE à la vie (sa valeur réelle était évidente)
        2. NON PÉRISSABLE (stockable comme l'or)
        3. DIVISIBLE (en petites unités)
        4. ÉCHANGEABLE (reconnu par tous)

        L'empire romain ne payait pas ses légionnaires en "monnaie" abstraite.
        Il les payait en ARGENT RÉEL — du sel.

        La langue a gardé la mémoire de cette économie juste.
        Le "salaire" moderne n'a plus aucun lien avec le sel.
        C'est pourquoi il n'a plus la même stabilité.
        """

    def compare_salt_with_thaman(self) -> Dict:
        """
        Compare le sel avec l'or/l'argent comme thaman potentiel
        """
        return {
            'gold': {
                'can_be_thaman': True,
                'rank': 1,
                'reason': 'Perte 0%, stockage éternel, reconnaissance universelle, valeur élevée/gramme',
                'layer': 'thaman_primary'
            },
            'silver': {
                'can_be_thaman': True,
                'rank': 2,
                'reason': 'Perte 0%, stockage éternel, reconnaissance universelle, plus divisible que l\'or',
                'layer': 'thaman_primary'
            },
            'rock_salt': {
                'can_be_thaman': False,  # Pas thaman primaire
                'rank': 3,
                'reason': 'Perte ~0%, stockage éternel, reconnaissance universelle MAIS valeur/gramme trop faible',
                'layer': 'semi_thaman',
                'note': 'Excellent candidat pour le panier Grondona — quasi-étalon régional'
            },
            'sea_salt_dry': {
                'can_be_thaman': False,
                'rank': 4,
                'reason': 'Perte légère (~0.5%/an), stockable, mais moins stable que sel gemme',
                'layer': 'grondona_basket',
                'note': 'Dans le panier, juste derrière le cuivre'
            }
        }

    def salt_as_salary(self, salt_grams_per_day: float = 1.0,
                       work_days: int = 365,
                       salt_price_usd_per_kg: float = 0.50) -> Dict:
        """
        Calcul historique : combien de sel valait le salaire romain
        """
        total_salt_kg = (salt_grams_per_day * work_days) / 1000
        salary_in_salt_grams = total_salt_kg * 1000
        salary_in_usd = total_salt_kg * salt_price_usd_per_kg

        return {
            'salt_per_day_grams': salt_grams_per_day,
            'work_days': work_days,
            'total_salt_kg': total_salt_kg,
            'salary_in_salt_grams': salary_in_salt_grams,
            'salary_in_usd': salary_in_usd,
            'historical_parallel': f"Le légionnaire romain recevait ~{salt_grams_per_day}g de sel par jour",
            'modern_equivalent': f"Soit l'équivalent de ${salary_in_usd:.2f} en sel aujourd'hui",
            'lesson': "Le salaire était ancré dans une commodité réelle, non dans une monnaie abstraite"
        }

    def get_summary(self) -> Dict:
        """Résumé de l'analyse du sel"""
        return {
            'salt_types': [
                {
                    'name': k,
                    'fr': v.name_fr,
                    'layer': v.layer,
                    'degradation': v.degradation_rate,
                    'storage_years': v.storage_years_max
                }
                for k, v in self.salt_types.items()
            ],
            'linguistic_lesson': self.linguistic_lesson(),
            'comparison_with_thaman': self.compare_salt_with_thaman(),
            'historical_salary': self.salt_as_salary()
        }


# Exemple d'utilisation
if __name__ == "__main__":
    analysis = SaltCommodityAnalysis()

    print("=== LE SEL DANS LE SYSTÈME MONÉTAIRE ===")
    print(analysis.linguistic_lesson())

    print("\n=== TYPES DE SEL ET LEUR COUCHE ===")
    for name, salt in analysis.salt_types.items():
        print(f"\n{salt.name_fr}:")
        print(f"  Couche: {salt.layer}")
        print(f"  Dégradation: {salt.degradation_rate:.1%}/an")
        print(f"  Stockage max: {salt.storage_years_max or 'Éternel'}")

        # Vélocité requise
        velocity = salt.required_velocity()
        if velocity['velocity_needed'] > 0:
            print(f"  Vélocité: {velocity['velocity_needed']:.1f} renouvellements/an")
            print(f"  {velocity['message']}")

    # Salaire en sel
    print("\n=== SALAIRE EN SEL (HISTORIQUE) ===")
    salary = analysis.salt_as_salary(salt_grams_per_day=1, work_days=365)
    print(f"Sel par jour: {salary['salt_per_day_grams']}g")
    print(f"Total sur l'année: {salary['total_salt_kg']:.2f} kg")
    print(f"Valeur en sel aujourd'hui: ${salary['salary_in_usd']:.2f}")
    print(salary['lesson'])

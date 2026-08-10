"""
Zakat sur Nuqud (زكاة النقود)
=============================

La Zakat ne peut être payée qu'en nuqud (or/argent).
Pas de Zakat sur les fulus (monnaie de vélocité).

Règles :
- 2.5% sur l'épargne en or/argent (si Nisab atteint)
- 2.5% sur les profits commerciaux
- 10% sur les récoltes irriguées, 5% sur pluviales
- 2.5% sur le bétail (seuils spécifiques)

8 catégories de bénéficiaires :
1. Fuqara (pauvres)
2. Masakin (indigents)
3. Amilin (collecteurs)
4. Muallafati (nouveaux musulmans)
5. Riqaab (affranchissement)
6. Gharimin (endettés)
7. Fi Sabilillah (cause d'Allah)
8. Ibn Al-Sabil (voyageurs)

License: CC BY-SA 4.0 – Marc Daghar
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ZakatCategory(Enum):
    """Les 8 catégories de bénéficiaires de la Zakat"""
    FUQARA = "fuqara"          # Les pauvres
    MASAKIN = "masakin"        # Les nécessiteux
    AMILIN = "amilin"          # Collecteurs de Zakat
    MUALLAFATI = "muallafati"  # Nouveaux musulmans
    RIQAAB = "riqaab"          # Esclaves (affranchissement)
    GHARIMIN = "gharimin"      # Endettés
    FI_SABILILLAH = "fi_sabilillah"  # Dans le chemin d'Allah
    IBN_AL_SABIL = "ibn_al_sabil"    # Voyageurs en détresse

    @classmethod
    def get_all(cls) -> List['ZakatCategory']:
        return list(cls)

    @classmethod
    def get_names(cls) -> List[str]:
        return [c.value for c in cls]


class ZakatOnNuqud:
    """
    Calcul de la Zakat sur le nuqud (or/argent)
    """

    # Taux
    ZAKAT_RATE: float = 0.025          # 2.5%
    URF_RAINFED: float = 0.10          # 10% pour agriculture pluviale
    URF_IRRIGATED: float = 0.05        # 5% pour agriculture irriguée
    RIKAZ_RATE: float = 0.20           # 20% pour trésors enfouis

    # Seuils Nisab (en grammes)
    NISAB_GOLD: float = 85.0           # 85g d'or
    NISAB_SILVER: float = 595.0        # 595g d'argent

    @classmethod
    def calculate(cls,
                  nuqud_holdings: List[Dict],
                  trade_profit_nuqud: float = 0.0,
                  agricultural_yield_nuqud: float = 0.0,
                  livestock_nuqud: float = 0.0,
                  is_irrigated: bool = True) -> Dict:
        """
        Calcule la Zakat totale due

        Args:
            nuqud_holdings: Liste des avoirs en nuqud
                Ex: [{'metal': 'gold', 'weight': 100}, {'metal': 'silver', 'weight': 500}]
            trade_profit_nuqud: Profits commerciaux en équivalent nuqud
            agricultural_yield_nuqud: Récoltes en équivalent nuqud
            livestock_nuqud: Bétail en équivalent nuqud
            is_irrigated: True si agriculture irriguée, False si pluviale

        Returns:
            Dict avec le détail du calcul
        """
        total_zakat = 0.0
        details = []

        # 1. Zakat sur l'épargne en or/argent (2.5%)
        gold_weight = 0.0
        silver_weight = 0.0

        for holding in nuqud_holdings:
            metal = holding.get('metal', '').lower()
            weight = holding.get('weight', 0.0)

            if metal == 'gold':
                gold_weight += weight
            elif metal == 'silver':
                silver_weight += weight

        # Vérification du Nisab pour l'or
        if gold_weight >= cls.NISAB_GOLD:
            gold_zakat = gold_weight * cls.ZAKAT_RATE
            total_zakat += gold_zakat
            details.append({
                'category': 'gold_savings',
                'weight': gold_weight,
                'rate': cls.ZAKAT_RATE,
                'zakat': gold_zakat,
                'nisab_reached': True
            })
        else:
            details.append({
                'category': 'gold_savings',
                'weight': gold_weight,
                'rate': cls.ZAKAT_RATE,
                'zakat': 0.0,
                'nisab_reached': False,
                'note': f"Nisab or ({cls.NISAB_GOLD}g) non atteint"
            })

        # Vérification du Nisab pour l'argent
        if silver_weight >= cls.NISAB_SILVER:
            silver_zakat = silver_weight * cls.ZAKAT_RATE
            total_zakat += silver_zakat
            details.append({
                'category': 'silver_savings',
                'weight': silver_weight,
                'rate': cls.ZAKAT_RATE,
                'zakat': silver_zakat,
                'nisab_reached': True
            })
        else:
            details.append({
                'category': 'silver_savings',
                'weight': silver_weight,
                'rate': cls.ZAKAT_RATE,
                'zakat': 0.0,
                'nisab_reached': False,
                'note': f"Nisab argent ({cls.NISAB_SILVER}g) non atteint"
            })

        # 2. Zakat sur les profits commerciaux (2.5%)
        if trade_profit_nuqud > 0:
            trade_zakat = trade_profit_nuqud * cls.ZAKAT_RATE
            total_zakat += trade_zakat
            details.append({
                'category': 'trade_profit',
                'amount': trade_profit_nuqud,
                'rate': cls.ZAKAT_RATE,
                'zakat': trade_zakat
            })

        # 3. Zakat sur l'agriculture (10% ou 5%)
        if agricultural_yield_nuqud > 0:
            rate = cls.URF_IRRIGATED if is_irrigated else cls.URF_RAINFED
            agri_zakat = agricultural_yield_nuqud * rate
            total_zakat += agri_zakat
            details.append({
                'category': 'agriculture',
                'amount': agricultural_yield_nuqud,
                'rate': rate,
                'zakat': agri_zakat,
                'type': 'irrigated' if is_irrigated else 'rainfed'
            })

        # 4. Zakat sur le bétail (2.5%)
        if livestock_nuqud > 0:
            livestock_zakat = livestock_nuqud * cls.ZAKAT_RATE
            total_zakat += livestock_zakat
            details.append({
                'category': 'livestock',
                'amount': livestock_nuqud,
                'rate': cls.ZAKAT_RATE,
                'zakat': livestock_zakat
            })

        return {
            'total_zakat': total_zakat,
            'details': details,
            'gold_weight': gold_weight,
            'silver_weight': silver_weight,
            'gold_nisab_reached': gold_weight >= cls.NISAB_GOLD,
            'silver_nisab_reached': silver_weight >= cls.NISAB_SILVER
        }

    @classmethod
    def distribute(cls,
                   zakat_amount: float,
                   distribution_weights: Optional[Dict[ZakatCategory, float]] = None) -> Dict:
        """
        Distribue la Zakat selon les 8 catégories

        Args:
            zakat_amount: Montant total de Zakat à distribuer
            distribution_weights: Poids personnalisés pour chaque catégorie
                Si None, distribution équitable

        Returns:
            Dict avec la distribution par catégorie
        """
        if distribution_weights is None:
            # Distribution équitable par défaut
            weights = {cat: 1/8 for cat in ZakatCategory}
        else:
            # Normalisation des poids
            total = sum(distribution_weights.values())
            weights = {cat: w/total for cat, w in distribution_weights.items()}

        distribution = {}
        for category, weight in weights.items():
            amount = zakat_amount * weight
            distribution[category] = {
                'category': category.value,
                'weight': weight,
                'amount': amount,
                'beneficiaries': 0  # À remplir avec les bénéficiaires réels
            }

        return {
            'total_distributed': zakat_amount,
            'distribution': distribution,
            'timestamp': time.time()
        }

    @classmethod
    def is_payable_in_fulus(cls) -> bool:
        """La Zakat n'est JAMAIS payable en fulus"""
        return False


# Exemple d'utilisation
if __name__ == "__main__":
    # Avoirs en nuqud
    holdings = [
        {'metal': 'gold', 'weight': 100},
        {'metal': 'silver', 'weight': 300}
    ]

    # Calcul
    result = ZakatOnNuqud.calculate(
        nuqud_holdings=holdings,
        trade_profit_nuqud=500,
        agricultural_yield_nuqud=200,
        livestock_nuqud=100
    )

    print("=== CALCUL DE LA ZAKAT ===")
    print(f"Total Zakat due: {result['total_zakat']:.2f} g eq")

    for detail in result['details']:
        cat = detail.get('category', 'unknown')
        zakat = detail.get('zakat', 0)
        if zakat > 0:
            print(f"  {cat}: {zakat:.2f} g eq")

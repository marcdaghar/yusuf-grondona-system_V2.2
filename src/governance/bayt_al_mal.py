"""
Bayt al-Mal (بيت المال) – Trésorerie publique islamique
========================================================

Le Bayt al-Mal est la trésorerie publique islamique.
Il est responsable de :
1. La collecte de la Zakat (en nuqud uniquement)
2. La redistribution aux 8 catégories coraniques
3. La gestion des fonds publics (en cas de crise)

La Zakat est un pilier de l'Islam. Elle n'est pas une taxe optionnelle.
Elle est collectée par l'autorité politique (l'émir) et redistribuée
selon les catégories définies dans le Coran.

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import time
import math


class ZakatCategory(Enum):
    """
    Les 8 catégories de bénéficiaires de la Zakat (Coran 9:60)
    """
    FUQARA = "fuqara"           # Les pauvres
    MASAKIN = "masakin"         # Les nécessiteux
    AMILIN = "amilin"           # Collecteurs de Zakat
    MUALLAFATI = "muallafati"   # Nouveaux musulmans (réconciliation des cœurs)
    RIQAAB = "riqaab"           # Esclaves (affranchissement)
    GHARIMIN = "gharimin"       # Endettés
    FI_SABILILLAH = "fi_sabilillah"  # Dans le chemin d'Allah
    IBN_AL_SABIL = "ibn_al_sabil"    # Voyageurs en détresse

    @classmethod
    def get_all(cls) -> List['ZakatCategory']:
        """Retourne toutes les catégories"""
        return list(cls)

    @classmethod
    def get_names(cls) -> List[str]:
        """Retourne les noms des catégories"""
        return [c.value for c in cls]

    @classmethod
    def get_default_weights(cls) -> Dict['ZakatCategory', float]:
        """
        Distribution équitable par défaut
        """
        return {cat: 1.0 / len(cls) for cat in cls}


@dataclass
class ZakatDistribution:
    """
    Enregistrement d'une distribution de Zakat
    """
    timestamp: float = field(default_factory=time.time)
    total_amount: float = 0.0
    distribution: Dict[ZakatCategory, float] = field(default_factory=dict)
    beneficiaries: Dict[ZakatCategory, int] = field(default_factory=dict)
    emir_approval: bool = False

    def to_dict(self) -> Dict:
        """Convertit en dictionnaire"""
        return {
            'timestamp': self.timestamp,
            'total_amount': self.total_amount,
            'distribution': {k.value: v for k, v in self.distribution.items()},
            'beneficiaries': {k.value: v for k, v in self.beneficiaries.items()},
            'emir_approval': self.emir_approval
        }


class BaytAlMal:
    """
    Trésorerie publique islamique (Bayt al-Mal)
    """

    def __init__(self, emir_name: str, region: str = ""):
        """
        Args:
            emir_name: Nom de l'émir (autorité politique)
            region: Région de compétence
        """
        self.emir_name = emir_name
        self.region = region

        # Fonds en nuqud (or/argent) uniquement
        self.zakat_funds: float = 0.0  # en équivalent grammes d'or

        # Fonds d'urgence
        self.emergency_funds: float = 0.0

        # Historique des distributions
        self.distributions: List[ZakatDistribution] = []

        # Seuils de pauvreté
        self.poverty_line: float = 100.0  # en unités de nuqud
        self.extreme_poverty_line: float = 50.0

        # Paramètres de distribution
        self.default_weights = ZakatCategory.get_default_weights()

        # Statistiques
        self.total_collected: float = 0.0
        self.total_distributed: float = 0.0

    def collect_zakat(self,
                      nuqud_holdings: List[Dict],
                      trade_profit_nuqud: float = 0.0,
                      agricultural_yield_nuqud: float = 0.0,
                      livestock_nuqud: float = 0.0,
                      is_irrigated: bool = True) -> Dict:
        """
        Collecte la Zakat sur les avoirs en nuqud

        Args:
            nuqud_holdings: Liste des avoirs en nuqud
                Ex: [{'metal': 'gold', 'weight': 100}, {'metal': 'silver', 'weight': 500}]
            trade_profit_nuqud: Profits commerciaux en équivalent nuqud
            agricultural_yield_nuqud: Récoltes en équivalent nuqud
            livestock_nuqud: Bétail en équivalent nuqud
            is_irrigated: True si agriculture irriguée

        Returns:
            Dict avec le détail du calcul et le montant collecté
        """
        # Calcul de la Zakat due
        total_zakat = 0.0
        details = []

        # 1. Zakat sur l'or (2.5% si Nisab atteint)
        gold_weight = 0.0
        for holding in nuqud_holdings:
            if holding.get('metal', '').lower() == 'gold':
                gold_weight += holding.get('weight', 0.0)

        if gold_weight >= 85.0:  # Nisab or
            gold_zakat = gold_weight * 0.025
            total_zakat += gold_zakat
            details.append({
                'category': 'gold_savings',
                'weight': gold_weight,
                'rate': 0.025,
                'zakat': gold_zakat,
                'nisab_reached': True
            })

        # 2. Zakat sur l'argent (2.5% si Nisab atteint)
        silver_weight = 0.0
        for holding in nuqud_holdings:
            if holding.get('metal', '').lower() == 'silver':
                silver_weight += holding.get('weight', 0.0)

        if silver_weight >= 595.0:  # Nisab argent
            silver_zakat = silver_weight * 0.025
            total_zakat += silver_zakat
            details.append({
                'category': 'silver_savings',
                'weight': silver_weight,
                'rate': 0.025,
                'zakat': silver_zakat,
                'nisab_reached': True
            })

        # 3. Zakat sur les profits commerciaux (2.5%)
        if trade_profit_nuqud > 0:
            trade_zakat = trade_profit_nuqud * 0.025
            total_zakat += trade_zakat
            details.append({
                'category': 'trade_profit',
                'amount': trade_profit_nuqud,
                'rate': 0.025,
                'zakat': trade_zakat
            })

        # 4. Zakat sur l'agriculture (10% ou 5%)
        if agricultural_yield_nuqud > 0:
            rate = 0.05 if is_irrigated else 0.10
            agri_zakat = agricultural_yield_nuqud * rate
            total_zakat += agri_zakat
            details.append({
                'category': 'agriculture',
                'amount': agricultural_yield_nuqud,
                'rate': rate,
                'zakat': agri_zakat,
                'type': 'irrigated' if is_irrigated else 'rainfed'
            })

        # 5. Zakat sur le bétail (2.5%)
        if livestock_nuqud > 0:
            livestock_zakat = livestock_nuqud * 0.025
            total_zakat += livestock_zakat
            details.append({
                'category': 'livestock',
                'amount': livestock_nuqud,
                'rate': 0.025,
                'zakat': livestock_zakat
            })

        # Ajout aux fonds publics
        self.zakat_funds += total_zakat
        self.total_collected += total_zakat

        return {
            'total_zakat': total_zakat,
            'details': details,
            'gold_weight': gold_weight,
            'silver_weight': silver_weight,
            'gold_nisab_reached': gold_weight >= 85.0,
            'silver_nisab_reached': silver_weight >= 595.0,
            'funds_after_collection': self.zakat_funds
        }

    def distribute(self,
                   custom_weights: Optional[Dict[ZakatCategory, float]] = None,
                   emergency: bool = False) -> ZakatDistribution:
        """
        Distribue la Zakat selon les 8 catégories

        Args:
            custom_weights: Poids personnalisés pour chaque catégorie
            emergency: Si True, distribution d'urgence (priorité aux catégories vulnérables)

        Returns:
            ZakatDistribution: Enregistrement de la distribution
        """
        if self.zakat_funds <= 0:
            return ZakatDistribution(
                total_amount=0.0,
                distribution={},
                beneficiaries={},
                emir_approval=True
            )

        # Détermination des poids
        if custom_weights:
            # Normalisation des poids
            total = sum(custom_weights.values())
            weights = {cat: w / total for cat, w in custom_weights.items()}
        elif emergency:
            # Distribution d'urgence : priorité aux pauvres, nécessiteux et endettés
            weights = {
                ZakatCategory.FUQARA: 0.35,
                ZakatCategory.MASAKIN: 0.25,
                ZakatCategory.GHARIMIN: 0.20,
                ZakatCategory.IBN_AL_SABIL: 0.10,
                ZakatCategory.FI_SABILILLAH: 0.05,
                ZakatCategory.AMILIN: 0.03,
                ZakatCategory.MUALLAFATI: 0.01,
                ZakatCategory.RIQAAB: 0.01
            }
        else:
            weights = self.default_weights

        # Distribution
        distribution = {}
        beneficiaries = {}

        for category, weight in weights.items():
            if category in ZakatCategory.get_all():
                amount = self.zakat_funds * weight
                distribution[category] = amount

                # Estimation du nombre de bénéficiaires (simplifié)
                per_capita = self.poverty_line * 0.5 if category in [ZakatCategory.FUQARA, ZakatCategory.MASAKIN] else self.poverty_line * 0.3
                beneficiaries[category] = int(amount / per_capita) if per_capita > 0 else 0

        # Création de l'enregistrement
        zakat_dist = ZakatDistribution(
            total_amount=self.zakat_funds,
            distribution=distribution,
            beneficiaries=beneficiaries,
            emir_approval=True
        )

        # Mise à jour des fonds
        self.zakat_funds = 0.0
        self.total_distributed += zakat_dist.total_amount

        # Enregistrement
        self.distributions.append(zakat_dist)

        return zakat_dist

    def distribute_emergency(self) -> ZakatDistribution:
        """
        Distribution d'urgence (priorité aux plus vulnérables)
        """
        return self.distribute(emergency=True)

    def allocate_emergency_funds(self, amount: float) -> bool:
        """
        Alloue une partie des fonds à la réserve d'urgence
        """
        if amount <= self.zakat_funds:
            self.zakat_funds -= amount
            self.emergency_funds += amount
            return True
        return False

    def release_emergency_funds(self, amount: float) -> float:
        """
        Libère des fonds d'urgence
        """
        if amount <= self.emergency_funds:
            self.emergency_funds -= amount
            return amount
        released = self.emergency_funds
        self.emergency_funds = 0.0
        return released

    def get_beneficiary_need_score(self, individual: Dict) -> float:
        """
        Calcule le score de besoin d'un individu (0-1)
        """
        score = 0.0

        # Pauvreté
        wealth = individual.get('wealth', 0)
        if wealth < self.extreme_poverty_line:
            score += 0.4
        elif wealth < self.poverty_line:
            score += 0.25

        # Dette
        debt_ratio = individual.get('debt_ratio', 0)
        if debt_ratio > 0.5:
            score += 0.2
        elif debt_ratio > 0.3:
            score += 0.1

        # Situation familiale
        dependents = individual.get('dependents', 0)
        if dependents > 5:
            score += 0.15
        elif dependents > 3:
            score += 0.08

        # Santé
        health = individual.get('health', 1.0)
        if health < 0.3:
            score += 0.15
        elif health < 0.5:
            score += 0.07

        # Éducation
        education = individual.get('education', 0)
        if education < 0.2:
            score += 0.1

        return min(1.0, score)

    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques du Bayt al-Mal
        """
        return {
            'emir': self.emir_name,
            'region': self.region,
            'zakat_funds': self.zakat_funds,
            'emergency_funds': self.emergency_funds,
            'total_collected': self.total_collected,
            'total_distributed': self.total_distributed,
            'total_distributions': len(self.distributions),
            'last_distribution': self.distributions[-1].to_dict() if self.distributions else None,
            'poverty_line': self.poverty_line,
            'extreme_poverty_line': self.extreme_poverty_line
        }

    def get_distribution_history(self, limit: int = 10) -> List[Dict]:
        """
        Retourne l'historique des distributions
        """
        return [d.to_dict() for d in self.distributions[-limit:]]

    def get_category_summary(self) -> Dict:
        """
        Résumé des distributions par catégorie
        """
        summary = {cat.value: {'total': 0.0, 'count': 0} for cat in ZakatCategory}

        for dist in self.distributions:
            for cat, amount in dist.distribution.items():
                summary[cat.value]['total'] += amount
                summary[cat.value]['count'] += 1

        return summary


# Exemple d'utilisation
if __name__ == "__main__":
    # Création du Bayt al-Mal
    bayt = BaytAlMal(emir_name="Ahmed", region="Marseille")

    print("=== BAYT AL-MAL ===")
    print(f"Émir: {bayt.emir_name}")
    print(f"Région: {bayt.region}")

    # Collecte de la Zakat
    holdings = [
        {'metal': 'gold', 'weight': 100},
        {'metal': 'silver', 'weight': 300}
    ]

    result = bayt.collect_zakat(
        nuqud_holdings=holdings,
        trade_profit_nuqud=500.0,
        agricultural_yield_nuqud=200.0,
        livestock_nuqud=100.0
    )

    print(f"\nZakat collectée: {result['total_zakat']:.2f} g eq")
    print(f"Fonds disponibles: {bayt.zakat_funds:.2f}")

    # Distribution
    distribution = bayt.distribute()

    print(f"\nDistribution totale: {distribution.total_amount:.2f}")
    for cat, amount in distribution.distribution.items():
        print(f"  {cat.value}: {amount:.2f} ({distribution.beneficiaries.get(cat, 0)} bénéficiaires)")

    print(f"\nStatistiques: {bayt.get_statistics()}")

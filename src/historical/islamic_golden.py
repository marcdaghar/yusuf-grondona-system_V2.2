"""
Islamic Golden Age – Dinar/Dirham, bimétallisme islamique
=========================================================

L'âge d'or islamique (VIIe-XIIIe siècles) a développé un système
monétaire sophistiqué basé sur :
- Le dinar (or) et le dirham (argent) comme nuqud
- Le fulus (monnaie de cuivre) pour les petites transactions
- Des règles strictes du riba (al-fadl, al-nasia)
- La Zakat comme pilier de redistribution
- La hisba comme régulation du marché

Références :
- Ibn Khaldun (1377). Al-Muqaddimah.
- Abu Yusuf (VIIIe siècle). Kitab al-Kharaj.

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class IslamicCommodity:
    """
    Une commodité dans le système monétaire islamique
    """
    name: str
    name_ar: str
    weight_grams: float
    purity: float
    layer: str  # nuqud, fulus
    zakat_rate: float
    riba_rules: str  # strict, assoupli
    historical_context: str

    def pure_weight(self) -> float:
        """Poids en métal pur"""
        return self.weight_grams * self.purity

    def zakat_due(self) -> float:
        """Zakat due sur cette commodité"""
        return self.weight_grams * self.zakat_rate

    def is_nisab_reached(self) -> bool:
        """Vérifie si le Nisab est atteint"""
        if self.name == "Dinar":
            return self.weight_grams >= 85.0
        elif self.name == "Dirham":
            return self.weight_grams >= 595.0
        return False


# Commodités islamiques
ISLAMIC_COMMODITIES = {
    'dinar': IslamicCommodity(
        name="Dinar",
        name_ar="دينار",
        weight_grams=4.25,
        purity=0.917,  # 22 carats
        layer="nuqud",
        zakat_rate=0.025,
        riba_rules="strict (al-fadl, al-nasia interdits)",
        historical_context="Monnaie d'or, étalon de valeur, thaman primus"
    ),
    'dirham': IslamicCommodity(
        name="Dirham",
        name_ar="درهم",
        weight_grams=2.8,
        purity=1.0,  # Argent pur
        layer="nuqud",
        zakat_rate=0.025,
        riba_rules="strict (al-fadl, al-nasia interdits)",
        historical_context="Monnaie d'argent, transaction courante"
    ),
    'fulus_copper': IslamicCommodity(
        name="Fulus (cuivre)",
        name_ar="فلس نحاسي",
        weight_grams=1.0,
        purity=0.8,
        layer="fulus",
        zakat_rate=0.0,  # Pas de Zakat sur le fulus
        riba_rules="assoupli (petit surplus, délai autorisé)",
        historical_context="Monnaie de vélocité pour les petites transactions"
    )
}


class IslamicGoldenAnalysis:
    """
    Analyse du système monétaire de l'âge d'or islamique
    """

    def __init__(self):
        self.commodities = ISLAMIC_COMMODITIES

    def get_commodity(self, name: str) -> Optional[IslamicCommodity]:
        """Récupère une commodité par son nom"""
        for key, value in self.commodities.items():
            if key == name or value.name == name:
                return value
        return None

    def get_dinar_dirham_ratio(self) -> Dict:
        """
        Ratio légal dinar/dirham selon le rite malikite
        """
        # 200 dirhams = 20 dinars (rite malikite)
        return {
            'legal_ratio': {
                'dirhams_per_dinar': 10,
                'weight_ratio': (10 * 2.8) / (4.25 * 0.917),
                'maliki_reference': '200 dirhams = 20 dinars'
            },
            'historical_evidence': {
                'source': 'Rite malikite',
                'period': 'VIIIe-XIIIe siècles',
                'reference': 'Dinar = 4.25g or, Dirham = 2.8g argent'
            },
            'lesson': "Le ratio bimétallique était fixé par la loi, pas par le marché"
        }

    def get_riba_rules(self) -> Dict:
        """
        Règles du riba dans l'Islam
        """
        return {
            'riba_al_fadl': {
                'definition': "Surplus dans l'échange de biens de même espèce",
                'nuqud': "STRICTEMENT INTERDIT (or contre or, argent contre argent)",
                'fulus': "AUTORISÉ jusqu'à 5% pour faciliter les échanges",
                'reference': "Hadith : 'L'or pour l'or, l'argent pour l'argent, de même quantité...'"
            },
            'riba_al_nasia': {
                'definition': "Délai dans l'échange",
                'nuqud': "STRICTEMENT INTERDIT (pas de paiement différé en or/argent)",
                'fulus': "AUTORISÉ (paiement différé possible)",
                'reference': "Coran 2:278-279"
            },
            'application': {
                'nuqud': "Échange égal et immédiat OBLIGATOIRE",
                'fulus': "Échange flexible, temps et surplus modérés autorisés"
            }
        }

    def get_zakat_rules(self) -> Dict:
        """
        Règles de la Zakat sur les nuqud
        """
        return {
            'zakat_rate': "2.5% sur l'épargne en or/argent",
            'nisab_gold': "85g d'or",
            'nisab_silver': "595g d'argent",
            'payment': "Payable UNIQUEMENT en nuqud (or/argent)",
            'exemption': "Pas de Zakat sur le fulus (monnaie de vélocité)",
            'categories': [
                "Fuqara (pauvres)",
                "Masakin (nécessiteux)",
                "Amilin (collecteurs)",
                "Muallafati (nouveaux musulmans)",
                "Riqaab (affranchissement)",
                "Gharimin (endettés)",
                "Fi Sabilillah (cause d'Allah)",
                "Ibn Al-Sabil (voyageurs)"
            ],
            'reference': "Coran 9:60"
        }

    def get_hisba_rules(self) -> Dict:
        """
        Règles de la hisba (inspection du marché)
        """
        return {
            'definition': "Fonction d'inspection et de régulation du marché",
            'muhtassib': "Inspecteur du marché",
            'responsibilities': [
                "Vérifier les poids et mesures",
                "Contrôler la qualité des produits",
                "Certifier les produits halal",
                "Prévenir les fraudes",
                "Protéger le consommateur"
            ],
            'principles': [
                "La justice dans les transactions",
                "La transparence des prix",
                "La qualité des produits",
                "La protection du consommateur"
            ],
            'reference': "Tradition prophétique, pratique des premiers califes"
        }

    def get_timeline(self) -> List[Dict]:
        """
        Chronologie du système monétaire islamique
        """
        return [
            {
                'period': 'Prophète Muhammad (570-632)',
                'system': 'Introduction du dinar et du dirham',
                'key_event': 'Établissement des règles du riba (Coran)'
            },
            {
                'period': 'Califes bien guidés (632-661)',
                'system': 'Standardisation du dinar/dirham, Zakat obligatoire',
                'key_event': 'Collecte systématique de la Zakat'
            },
            {
                'period': 'Omeyyades (661-750)',
                'system': 'Monnaie frappée à Damas, hisba institutionnalisée',
                'key_event': 'Création du premier bureau du muhtassib'
            },
            {
                'period': 'Abbassides (750-1258)',
                'system': 'Âge d'or de l'économie islamique, fulus de cuivre',
                'key_event': 'Développement des lettres de crédit (sakk)'
            },
            {
                'period': 'Andalousie (756-1492)',
                'system': 'Bimétallisme andalou, commerce méditerranéen',
                'key_event': 'Marrakech, Cordoue, Fès comme centres économiques'
            }
        ]

    def get_summary(self) -> Dict:
        """Résumé de l'analyse islamique"""
        return {
            'commodities': [
                {
                    'name': c.name,
                    'arabic': c.name_ar,
                    'weight_grams': c.weight_grams,
                    'layer': c.layer,
                    'zakat_rate': f"{c.zakat_rate:.1%}",
                    'riba_rules': c.riba_rules
                }
                for c in self.commodities.values()
            ],
            'dinar_dirham_ratio': self.get_dinar_dirham_ratio(),
            'riba_rules': self.get_riba_rules(),
            'zakat_rules': self.get_zakat_rules(),
            'hisba_rules': self.get_hisba_rules(),
            'timeline': self.get_timeline(),
            'key_lessons': [
                "Le bimétallisme or/argent est une tradition islamique",
                "Le nuqud/fulus est une distinction coranique et juridique",
                "La Zakat est un pilier, pas une option",
                "La hisba est une régulation humaine du marché",
                "La logistique (routes, ports) est la colonne vertébrale du commerce"
            ]
        }


# Exemple d'utilisation
if __name__ == "__main__":
    analysis = IslamicGoldenAnalysis()

    print("=== ÂGE D'OR ISLAMIQUE – DINAR/DIRHAM ===")

    print("\n=== COMMODITÉS ISLAMIQUES ===")
    for name, commodity in analysis.commodities.items():
        print(f"\n{commodity.name} ({commodity.name_ar})")
        print(f"  Poids: {commodity.weight_grams}g (pur: {commodity.pure_weight():.2f}g)")
        print(f"  Couche: {commodity.layer}")
        print(f"  Taux Zakat: {commodity.zakat_rate:.1%}")
        print(f"  Règles du riba: {commodity.riba_rules}")

    print("\n=== RATIO DINAR/DIRHAM (rite malikite) ===")
    ratio = analysis.get_dinar_dirham_ratio()
    print(f"Ratio légal: {ratio['legal_ratio']}")
    print(f"Référence: {ratio['legal_ratio']['maliki_reference']}")

    print("\n=== RÈGLES DU RIBA ===")
    riba = analysis.get_riba_rules()
    print(f"Riba al-fadl: {riba['riba_al_fadl']['definition']}")
    print(f"  Nuqud: {riba['riba_al_fadl']['nuqud']}")
    print(f"  Fulus: {riba['riba_al_fadl']['fulus']}")

    print("\n=== RÈGLES DE LA ZAKAT ===")
    zakat = analysis.get_zakat_rules()
    print(f"Taux: {zakat['zakat_rate']}")
    print(f"Nisab or: {zakat['nisab_gold']}g")
    print(f"Nisab argent: {zakat['nisab_silver']}g")
    print(f"Payable en: {zakat['payment']}")

    print("\n=== LEÇONS CLÉS ===")
    for lesson in analysis.get_summary()['key_lessons']:
        print(f"  • {lesson}")

"""
Yusuf-Grondona Monetary System – Commodities Module
====================================================

Ce module contient les analyses des commodités historiques et leur
intégration dans le système monétaire :

- Gold/Silver : Métaux précieux, thaman primus inter pares
- Salt : Sel, Via Salaria, salarium romain
- Rice : Riz, koku japonais, mesure de richesse
- Basket : Panier Grondona complet

License: CC BY-SA 4.0 – Marc Daghar
"""

from .gold_silver import GoldSilverAnalysis, PRIMARY_METALS
from .salt import SaltCommodityAnalysis, SALT_TYPES
from .rice import RiceCommodityAnalysis, RICE_TYPES
from .basket import GrondonaBasket, BASKET_COMPOSITION

__all__ = [
    'GoldSilverAnalysis',
    'PRIMARY_METALS',
    'SaltCommodityAnalysis',
    'SALT_TYPES',
    'RiceCommodityAnalysis',
    'RICE_TYPES',
    'GrondonaBasket',
    'BASKET_COMPOSITION',
]

__version__ = '1.0.0'

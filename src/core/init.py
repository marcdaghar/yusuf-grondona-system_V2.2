"""
Yusuf-Grondona Monetary System – Core Module
============================================

Ce module contient le noyau économique du système :
- Nuqud : or/argent comme étalon et réserve de valeur
- Fulus : monnaie de circulation à vélocité
- Grondona CRD : Commodity Reserve Department avec prix plancher/plafond
- BRI Network : Réseau multi-zones pour transferts inter-zones
- Hisba : Inspection du marché
- Zakat : payable uniquement en nuqud
- Riba Rules : Règles Al-Fadl et Al-Nasia

License: CC BY-SA 4.0 – Marc Daghar
"""

from .nuqud import Nuqud, NuqudSystem, PRIMARY_NUQUD
from .fulus import Fulus, FulusCurrency, FulusSignalSystem
from .grondona_crd import GrondonaCRD, CommodityInBasket
from .bri_network import BRINetwork, ZoneBRI, LiquidityBridge
from .hisba import Muhtassib, MarketInspection
from .zakat_nuqud import ZakatOnNuqud
from .riba_rules import RibaController, AssetClass, RIBA_RULES

__all__ = [
    'Nuqud',
    'NuqudSystem',
    'PRIMARY_NUQUD',
    'Fulus',
    'FulusCurrency',
    'FulusSignalSystem',
    'GrondonaCRD',
    'CommodityInBasket',
    'BRINetwork',
    'ZoneBRI',
    'LiquidityBridge',
    'Muhtassib',
    'MarketInspection',
    'ZakatOnNuqud',
    'RibaController',
    'AssetClass',
    'RIBA_RULES',
]

__version__ = '1.0.0'

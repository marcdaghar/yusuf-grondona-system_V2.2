"""
Yusuf-Grondona Monetary System – Historical Module
==================================================

Ce module contient l'analyse des systèmes monétaires historiques
et leurs leçons pour le système Yusuf-Grondona :

- Ancient Egypt : Blé, taux d'intérêt négatif sur 4000 ans
- Roman Empire : Sel, Via Salaria, salarium
- Islamic Golden Age : Dinar/Dirham, bimétallisme islamique

License: CC BY-SA 4.0 – Marc Daghar
"""

from .egypt_ancient import EgyptAncientAnalysis, EGYPT_COMMODITIES
from .roman_empire import RomanEmpireAnalysis, ROMAN_COMMODITIES
from .islamic_golden import IslamicGoldenAnalysis, ISLAMIC_COMMODITIES

__all__ = [
    'EgyptAncientAnalysis',
    'EGYPT_COMMODITIES',
    'RomanEmpireAnalysis',
    'ROMAN_COMMODITIES',
    'IslamicGoldenAnalysis',
    'ISLAMIC_COMMODITIES',
]

__version__ = '1.0.0'

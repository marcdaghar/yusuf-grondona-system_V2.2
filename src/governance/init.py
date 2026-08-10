"""
Yusuf-Grondona Monetary System – Governance Module
==================================================

Ce module contient les composants de gouvernance :
- Bayt al-Mal : Trésorerie publique, collecte et distribution de la Zakat
- Émir : Autorité politique
- Shura : Consultation des guildes

License: CC BY-SA 4.0 – Marc Daghar
"""

from .bayt_al_mal import BaytAlMal, ZakatDistribution, ZakatCategory

__all__ = [
    'BaytAlMal',
    'ZakatDistribution',
    'ZakatCategory',
]

__version__ = '1.0.0'

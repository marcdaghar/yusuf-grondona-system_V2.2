"""
Yusuf-Grondona Monetary System – Carbon Credits Module
======================================================

Ce module contient la gestion des crédits carbone (BCC) pour le système.

License: CC BY-SA 4.0 – Marc Daghar
"""

from .offsetting_manager import CarbonOffsetManager, CarbonAccount

__all__ = [
    'CarbonOffsetManager',
    'CarbonAccount',
]

__version__ = '1.0.0'

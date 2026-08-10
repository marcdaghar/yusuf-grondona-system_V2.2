"""
Yusuf-Grondona Monetary System – zk-SNARKs Module
==================================================

Ce module contient les composants pour les preuves à divulgation nulle :
- transfer.zok : Circuit ZoKrates pour transactions confidentielles
- zk_proofs.py : Implémentation Python pour générer et vérifier les preuves

License: CC BY-SA 4.0 – Marc Daghar
"""

from .zk_proofs import ZKSnarkProof, PrivateTransactionLedger

__all__ = [
    'ZKSnarkProof',
    'PrivateTransactionLedger',
]

__version__ = '1.0.0'

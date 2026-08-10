"""
Yusuf-Grondona Monetary System – Simulation Module
==================================================

Ce module contient les composants de simulation :
- Agents : guildes, commerçants, consommateurs
- Market : souq main à main
- Run : moteur de simulation complet
- Blockchain : ledger SHA256 pour traçabilité
- Logistics : chocs logistiques
- Crisis : scénarios de crise
- Climate : chocs climatiques
- Stress : tests de résistance

License: CC BY-SA 4.0 – Marc Daghar
"""

from .agents import Guilde, Commercant, Consommateur, MuhtassibAgent
from .market_advanced import Souq, Product, Transaction
from .run_full import run_full_simulation, run_one_year
from .blockchain_sim import Blockchain, Block
from .logistics_shocks import LogisticsShock, ShockManager
from .crisis_scenarios import CrisisScenario, CrisisManager
from .climate_crisis import ClimateCrisisSimulator
from .stress_test import StressTest

__all__ = [
    'Guilde',
    'Commercant',
    'Consommateur',
    'MuhtassibAgent',
    'Souq',
    'Product',
    'Transaction',
    'run_full_simulation',
    'run_one_year',
    'Blockchain',
    'Block',
    'LogisticsShock',
    'ShockManager',
    'CrisisScenario',
    'CrisisManager',
    'ClimateCrisisSimulator',
    'StressTest',
]

__version__ = '1.0.0'

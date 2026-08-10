"""
Yusuf-Grondona Monetary System – AI Module
==========================================

Ce module contient les composants d'intelligence artificielle :
- Muhtassib AI : Assistant du muhtassib (détection d'anomalies)
- RL Policy Optimizer : Optimisation des politiques monétaires (PPO)
- ESG Forecast : Prédiction des scores ESG sur 5 ans
- Backtest RL : Backtest sur données historiques
- Crisis Predictor : Système d'alerte précoce

Tous les modèles sont des assistants, pas des décideurs souverains.
La décision finale revient toujours au muhtassib ou à l'émir.

License: CC BY-SA 4.0 – Marc Daghar
"""

from .muhtassib_ai import MuhtassibAI, AnomalyDetector
from .rl_policy_optimizer import MonetaryPolicyEnv, RLPolicyOptimizer
from .esg_forecast import ESGForecaster, forecast_esg
from .backtest_rl import RLBacktester, load_historical_data
from .crisis_predictor import CrisisPredictor, EarlyWarningSystem

__all__ = [
    'MuhtassibAI',
    'AnomalyDetector',
    'MonetaryPolicyEnv',
    'RLPolicyOptimizer',
    'ESGForecaster',
    'forecast_esg',
    'RLBacktester',
    'load_historical_data',
    'CrisisPredictor',
    'EarlyWarningSystem',
]

__version__ = '1.0.0'

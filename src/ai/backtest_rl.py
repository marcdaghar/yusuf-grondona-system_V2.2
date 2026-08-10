"""
Backtest RL – Test des politiques RL sur données historiques
============================================================

Simule rétrospectivement les politiques monétaires RL sur des données réelles
ou simulées pour évaluer leur performance.

License: CC BY-SA 4.0 – Marc Daghar
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import warnings
warnings.filterwarnings('ignore')

from stable_baselines3 import PPO
from .rl_policy_optimizer import MonetaryPolicyEnv, ZoneState


@dataclass
class BacktestResult:
    """Résultat d'un backtest"""
    year: int
    suggested_rate: float
    suggested_subsidy: float
    actual_esg: float
    actual_gdp: float
    actual_unemployment: float
    policy_esg: float = 0.0
    policy_gdp: float = 0.0


class RLBacktester:
    """
    Backtest des politiques RL
    """

    def __init__(self, zones: Dict[str, ZoneState],
                 historical_data: pd.DataFrame):
        """
        Args:
            zones: Zones BRI pour l'environnement RL
            historical_data: DataFrame avec colonnes ['year', 'esg_global', 'gdp_growth', 'unemployment']
        """
        self.zones = zones
        self.historical = historical_data
        self.results: List[BacktestResult] = []

    def run_backtest(self, start_year: int = 2018,
                     end_year: int = 2023,
                     train_timesteps: int = 5000) -> pd.DataFrame:
        """
        Exécute le backtest sur la période donnée
        """
        # Entraînement du modèle RL
        env = MonetaryPolicyEnv(self.zones)
        model = PPO("MlpPolicy", env, verbose=0)
        model.learn(total_timesteps=train_timesteps)

        self.results = []

        for year in range(start_year, end_year + 1):
            year_data = self.historical[self.historical['year'] == year]
            if year_data.empty:
                continue

            # État actuel
            state = np.array([
                year_data['esg_global'].iloc[0] / 100,
                year_data['gdp_growth'].iloc[0] / 10,
                year_data['unemployment'].iloc[0] / 0.2,
                0.5,  # logistics_entropy normalisé
                0.5,  # reserve_ratio
                0.05  # exchange_rate
            ], dtype=np.float32)

            # Prédiction de la politique
            action, _ = model.predict(state, deterministic=True)

            # Enregistrement du résultat
            result = BacktestResult(
                year=year,
                suggested_rate=float(action[0]),
                suggested_subsidy=float(action[1]),
                actual_esg=float(year_data['esg_global'].iloc[0]),
                actual_gdp=float(year_data['gdp_growth'].iloc[0]),
                actual_unemployment=float(year_data['unemployment'].iloc[0])
            )

            # Simulation de l'impact de la politique
            result.policy_esg = result.actual_esg + action[0] * 10
            result.policy_gdp = result.actual_gdp + action[1] * 2

            self.results.append(result)

        return self.to_dataframe()

    def to_dataframe(self) -> pd.DataFrame:
        """Convertit les résultats en DataFrame"""
        return pd.DataFrame([
            {
                'year': r.year,
                'suggested_rate': r.suggested_rate,
                'suggested_subsidy': r.suggested_subsidy,
                'actual_esg': r.actual_esg,
                'policy_esg': r.policy_esg,
                'actual_gdp': r.actual_gdp,
                'policy_gdp': r.policy_gdp,
                'actual_unemployment': r.actual_unemployment
            }
            for r in self.results
        ])

    def compute_sharpe_ratio(self) -> float:
        """
        Calcule le ratio de Sharpe des performances ESG
        """
        if not self.results:
            return 0.0

        returns = []
        for r in self.results:
            if r.policy_esg > 0:
                returns.append((r.policy_esg - r.actual_esg) / r.actual_esg)

        if len(returns) < 2 or np.std(returns) == 0:
            return 0.0

        return np.mean(returns) / np.std(returns) * np.sqrt(12)

    def compute_improvement(self) -> Dict:
        """
        Calcule l'amélioration moyenne apportée par la politique RL
        """
        if not self.results:
            return {'esg': 0, 'gdp': 0}

        esg_improvements = [r.policy_esg - r.actual_esg for r in self.results]
        gdp_improvements = [r.policy_gdp - r.actual_gdp for r in self.results]

        return {
            'esg_mean': np.mean(esg_improvements),
            'esg_std': np.std(esg_improvements),
            'gdp_mean': np.mean(gdp_improvements),
            'gdp_std': np.std(gdp_improvements)
        }


def load_historical_data() -> pd.DataFrame:
    """
    Charge des données historiques simulées
    """
    np.random.seed(42)

    years = np.arange(2010, 2026)
    n = len(years)

    # Simulation de données réalistes
    esg = 50 + 10 * np.sin(np.linspace(0, 2*np.pi, n)) + np.random.normal(0, 2, n)
    gdp = 0.02 + 0.03 * np.sin(np.linspace(0, 2*np.pi, n) + 0.5) + np.random.normal(0, 0.01, n)
    unemployment = 0.08 + 0.02 * np.sin(np.linspace(0, 2*np.pi, n) + 1) + np.random.normal(0, 0.005, n)

    # Choc COVID (2020)
    covid_idx = np.where(years == 2020)[0]
    if len(covid_idx) > 0:
        idx = covid_idx[0]
        esg[idx] -= 10
        gdp[idx] -= 0.08
        unemployment[idx] += 0.04

    return pd.DataFrame({
        'year': years,
        'esg_global': np.clip(esg, 0, 100),
        'gdp_growth': np.clip(gdp, -0.1, 0.1),
        'unemployment': np.clip(unemployment, 0.02, 0.2)
    })


# Exemple d'utilisation
if __name__ == "__main__":
    # Chargement des données
    data = load_historical_data()
    print("=== BACKTEST RL ===")
    print(f"Données: {len(data)} années")

    # Création des zones
    zones = {
        "Zone1": ZoneState("Zone1", 5000, 10000, 0.05, 0.02, 0.02, 0.08, 50, 1.0)
    }

    # Backtest
    backtester = RLBacktester(zones, data)
    results = backtester.run_backtest(start_year=2018, end_year=2023)

    print("\nRésultats du backtest:")
    print(results.to_string(index=False))

    # Métriques
    sharpe = backtester.compute_sharpe_ratio()
    improvement = backtester.compute_improvement()

    print(f"\nRatio de Sharpe: {sharpe:.2f}")
    print(f"Amélioration ESG moyenne: {improvement['esg_mean']:.1f} points")
    print(f"Amélioration PIB moyenne: {improvement['gdp_mean']:.1%}")

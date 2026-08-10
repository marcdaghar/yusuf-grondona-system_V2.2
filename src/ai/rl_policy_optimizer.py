"""
RL Policy Optimizer – Optimisation des politiques monétaires
============================================================

Utilise le Reinforcement Learning (PPO) pour optimiser :
- Le taux de change fulus/nuqud
- Les subventions sectorielles
- Les paramètres du CRD

L'IA assiste l'émir et le muhtassib, elle ne décide pas seule.

License: CC BY-SA 4.0 – Marc Daghar
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
import time


@dataclass
class ZoneState:
    """État d'une zone BRI pour l'environnement RL"""
    name: str
    nuqud_reserve: float
    fulus_supply: float
    exchange_rate: float
    gdp_growth: float
    inflation: float
    unemployment: float
    esg_score: float
    logistics_entropy: float


class MonetaryPolicyEnv(gym.Env):
    """
    Environnement RL pour l'optimisation des politiques monétaires

    Espace d'état :
    - ESG global (normalisé 0-1)
    - Croissance PIB (normalisé)
    - Chômage (normalisé)
    - Entropie logistique (normalisée)
    - Réserves nuqud / PIB
    - Taux de change actuel

    Espace d'action :
    - Taux de change (fulus/nuqud)
    - Subvention sectorielle (% PIB)
    - Intervention CRD (achat/vente)
    """

    def __init__(self, zones: Dict[str, ZoneState],
                 initial_state: Optional[Dict] = None,
                 max_steps: int = 52):
        super().__init__()

        self.zones = zones
        self.zone_names = list(zones.keys())
        self.n_zones = len(self.zone_names)
        self.max_steps = max_steps
        self.current_step = 0

        # Espace d'état : pour chaque zone + variables globales
        # [esg, gdp_growth, unemployment, logistics_entropy, reserve_ratio, exchange_rate]
        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(self.n_zones * 6,),
            dtype=np.float32
        )

        # Espace d'action : [taux_echange, subvention, intervention_CRD]
        self.action_space = spaces.Box(
            low=np.array([-0.1, -0.05, -1.0], dtype=np.float32),
            high=np.array([0.1, 0.05, 1.0], dtype=np.float32),
            dtype=np.float32
        )

        # État initial
        self.state = self._get_state()

    def _get_state(self) -> np.ndarray:
        """Construit le vecteur d'état"""
        state = []

        for name in self.zone_names:
            zone = self.zones[name]
            state.extend([
                zone.esg_score / 100.0,  # Normalisé 0-1
                zone.gdp_growth / 10.0,   # Normalisé -1 à 1
                zone.unemployment / 0.2,  # Normalisé 0-1
                zone.logistics_entropy / 2.0,  # Normalisé 0-1
                zone.nuqud_reserve / 10000.0,  # Normalisé
                zone.exchange_rate / 0.1  # Normalisé
            ])

        return np.array(state, dtype=np.float32)

    def _apply_action(self, action: np.ndarray) -> None:
        """Applique l'action à l'état"""
        # Décodage de l'action
        rate_change = action[0]
        subsidy = action[1]
        crd_action = action[2]

        # Application à toutes les zones
        for name in self.zone_names:
            zone = self.zones[name]

            # 1. Ajustement du taux de change
            old_rate = zone.exchange_rate
            zone.exchange_rate = max(0.001, min(0.5, old_rate * (1 + rate_change)))

            # 2. Subvention (augmentation de la masse monétaire)
            if subsidy > 0:
                zone.fulus_supply *= (1 + subsidy)

            # 3. Intervention CRD
            if crd_action > 0:
                # Achat de nuqud (augmentation des réserves)
                amount = crd_action * 100
                if zone.fulus_supply > amount:
                    zone.fulus_supply -= amount
                    zone.nuqud_reserve += amount * zone.exchange_rate
            elif crd_action < 0:
                # Vente de nuqud (diminution des réserves)
                amount = -crd_action * 100
                if zone.nuqud_reserve > amount:
                    zone.nuqud_reserve -= amount
                    zone.fulus_supply += amount / zone.exchange_rate

            # 4. Mise à jour des indicateurs économiques (simplifié)
            # L'ESG s'améliore avec les bonnes politiques
            zone.esg_score = min(100, zone.esg_score + np.random.normal(0, 1))

            # La croissance dépend de la subvention
            zone.gdp_growth = max(-0.1, min(0.1, zone.gdp_growth + subsidy * 0.5))

            # Le chômage diminue avec la croissance
            zone.unemployment = max(0.02, min(0.2, zone.unemployment - zone.gdp_growth * 0.5))

            # L'entropie logistique diminue avec les interventions CRD
            zone.logistics_entropy = max(0.01, min(2.0, zone.logistics_entropy - crd_action * 0.05))

    def _calculate_reward(self) -> float:
        """Calcule la récompense basée sur l'état du système"""
        rewards = []

        for name in self.zone_names:
            zone = self.zones[name]

            # Objectif 1 : ESG élevé (0-100)
            esg_reward = zone.esg_score / 100.0

            # Objectif 2 : Croissance positive
            growth_reward = max(0, zone.gdp_growth) * 5

            # Objectif 3 : Chômage bas
            unemployment_penalty = zone.unemployment * 2

            # Objectif 4 : Entropie logistique basse
            entropy_penalty = zone.logistics_entropy * 0.5

            # Objectif 5 : Réserves suffisantes
            reserve_ratio = zone.nuqud_reserve / 10000.0
            reserve_reward = min(1, reserve_ratio) * 0.5

            # Objectif 6 : Stabilité du taux de change
            rate_stability = 1 - abs(zone.exchange_rate - 0.05) / 0.05

            # Récompense composite
            reward = (esg_reward * 2.0 +
                      growth_reward * 1.5 -
                      unemployment_penalty * 1.0 -
                      entropy_penalty * 1.0 +
                      reserve_reward * 0.5 +
                      rate_stability * 0.5)

            rewards.append(reward)

        return sum(rewards) / len(rewards)

    def reset(self, seed: Optional[int] = None,
              options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """Réinitialise l'environnement"""
        self.current_step = 0

        # Réinitialisation des zones
        for name in self.zone_names:
            zone = self.zones[name]
            zone.nuqud_reserve = 5000.0
            zone.fulus_supply = 10000.0
            zone.exchange_rate = 0.05
            zone.gdp_growth = 0.02
            zone.inflation = 0.02
            zone.unemployment = 0.08
            zone.esg_score = 50.0
            zone.logistics_entropy = 1.0

        self.state = self._get_state()
        return self.state, {}

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Effectue un pas de simulation"""
        self.current_step += 1

        # Application de l'action
        self._apply_action(action)

        # Mise à jour de l'état
        self.state = self._get_state()

        # Calcul de la récompense
        reward = self._calculate_reward()

        # Vérification de la terminaison
        terminated = self.current_step >= self.max_steps
        truncated = False

        # Information supplémentaire
        info = {
            'step': self.current_step,
            'zones': {name: {
                'esg': zone.esg_score,
                'gdp': zone.gdp_growth,
                'unemployment': zone.unemployment,
                'exchange_rate': zone.exchange_rate
            } for name, zone in self.zones.items()}
        }

        return self.state, reward, terminated, truncated, info


class RLPolicyOptimizer:
    """
    Optimiseur de politiques monétaires par RL
    """

    def __init__(self, zones: Dict[str, ZoneState],
                 learning_rate: float = 0.001,
                 n_steps: int = 2048,
                 batch_size: int = 64,
                 n_epochs: int = 10):
        self.zones = zones
        self.learning_rate = learning_rate
        self.n_steps = n_steps
        self.batch_size = batch_size
        self.n_epochs = n_epochs

        self.env = None
        self.model = None
        self.trained = False

        self._create_env()

    def _create_env(self) -> None:
        """Crée l'environnement RL"""
        self.env = DummyVecEnv([lambda: MonetaryPolicyEnv(self.zones)])

    def train(self, total_timesteps: int = 10000,
              verbose: int = 1) -> None:
        """
        Entraîne le modèle PPO
        """
        print(f"🚀 Entraînement RL sur {total_timesteps} pas...")

        self.model = PPO(
            "MlpPolicy",
            self.env,
            learning_rate=self.learning_rate,
            n_steps=self.n_steps,
            batch_size=self.batch_size,
            n_epochs=self.n_epochs,
            verbose=verbose,
            tensorboard_log="./logs/rl/"
        )

        self.model.learn(total_timesteps=total_timesteps)
        self.trained = True

        print("✅ Entraînement terminé")

    def get_optimal_policy(self, state: Optional[np.ndarray] = None) -> Dict:
        """
        Retourne la politique optimale pour l'état actuel
        """
        if not self.trained:
            return {
                'exchange_rate_adjustment': 0.0,
                'subsidy': 0.0,
                'crd_intervention': 0.0,
                'message': "Modèle non entraîné"
            }

        if state is None:
            env = MonetaryPolicyEnv(self.zones)
            state, _ = env.reset()

        action, _ = self.model.predict(state, deterministic=True)

        return {
            'exchange_rate_adjustment': float(action[0]),
            'subsidy': float(action[1]),
            'crd_intervention': float(action[2]),
            'message': "Politique optimale calculée"
        }

    def simulate_policy(self, n_steps: int = 52,
                        initial_state: Optional[Dict] = None) -> Dict:
        """
        Simule l'application de la politique optimale
        """
        if not self.trained:
            return {'error': "Modèle non entraîné"}

        env = MonetaryPolicyEnv(self.zones)
        state, _ = env.reset()

        history = {
            'steps': [],
            'states': [],
            'actions': [],
            'rewards': []
        }

        for step in range(n_steps):
            action, _ = self.model.predict(state, deterministic=True)
            next_state, reward, terminated, _, info = env.step(action)

            history['steps'].append(step)
            history['states'].append(state.copy())
            history['actions'].append(action.copy())
            history['rewards'].append(reward)

            if terminated:
                break

            state = next_state

        return history

    def get_summary(self) -> Dict:
        """Résumé de l'optimiseur"""
        return {
            'trained': self.trained,
            'learning_rate': self.learning_rate,
            'zones': list(self.zones.keys()),
            'n_zones': len(self.zones)
        }


# Exemple d'utilisation
if __name__ == "__main__":
    # Création des zones
    zones = {
        "Chine": ZoneState(
            name="Chine",
            nuqud_reserve=20000,
            fulus_supply=100000,
            exchange_rate=0.05,
            gdp_growth=0.04,
            inflation=0.02,
            unemployment=0.05,
            esg_score=68,
            logistics_entropy=0.8
        ),
        "NUL": ZoneState(
            name="NUL",
            nuqud_reserve=5000,
            fulus_supply=20000,
            exchange_rate=0.05,
            gdp_growth=0.01,
            inflation=0.05,
            unemployment=0.12,
            esg_score=45,
            logistics_entropy=1.5
        )
    }

    # Création de l'optimiseur
    optimizer = RLPolicyOptimizer(zones)

    # Entraînement
    optimizer.train(total_timesteps=5000, verbose=0)

    # Politique optimale
    policy = optimizer.get_optimal_policy()
    print("=== POLITIQUE OPTIMALE ===")
    for key, value in policy.items():
        print(f"{key}: {value}")

    # Résumé
    print(f"\nRésumé: {optimizer.get_summary()}")

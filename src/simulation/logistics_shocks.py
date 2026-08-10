"""
Chocs logistiques
=================

Événements perturbant la logistique :
- Ports fermés
- Routes coupées
- Entrepôts endommagés
- Retards de livraison

License: CC BY-SA 4.0 – Marc Daghar
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time


@dataclass
class LogisticsShock:
    """
    Un événement perturbant la logistique
    """
    name: str
    severity: float = 0.3  # 0 = mineur, 1 = catastrophique
    duration_days: int = 30
    active: bool = False
    days_remaining: int = 0
    effects: Dict[str, Any] = field(default_factory=dict)

    def apply(self, economy: Optional[Any] = None) -> Dict:
        """
        Applique les effets du choc
        """
        if not self.active:
            return {}

        effects = {}

        if "port" in self.name.lower():
            effects["import_delay_multiplier"] = 1 + self.severity * 2
            effects["port_closed"] = self.severity > 0.8

        elif "route" in self.name.lower():
            effects["travel_time_multiplier"] = 1 + self.severity

        elif "warehouse" in self.name.lower():
            effects["degradation_increase"] = self.severity * 0.1
            effects["storage_capacity_reduction"] = self.severity * 0.3

        elif "fuel" in self.name.lower() or "énergie" in self.name.lower():
            effects["energy_price_multiplier"] = 1 + self.severity * 2
            effects["fuel_availability"] = max(0, 1 - self.severity * 0.5)

        elif "inondation" in self.name.lower() or "flood" in self.name.lower():
            effects["road_accessibility"] = max(0, 1 - self.severity * 0.7)
            effects["infrastructure_damage"] = self.severity * 0.5

        self.effects = effects
        return effects

    def update(self, days: int = 1) -> bool:
        """
        Met à jour la durée restante
        Retourne True si le choc est encore actif
        """
        if self.active:
            self.days_remaining -= days
            if self.days_remaining <= 0:
                self.active = False
                self.days_remaining = 0
        return self.active


class ShockManager:
    """
    Gestionnaire de chocs logistiques
    """

    def __init__(self):
        self.shocks: List[LogisticsShock] = []
        self.active_shocks: List[LogisticsShock] = []
        self.shock_history: List[Dict] = []

    def add_shock(self, shock: LogisticsShock) -> None:
        """Ajoute un choc potentiel"""
        self.shocks.append(shock)

    def activate_random_shock(self, probability: float = 0.2) -> Optional[LogisticsShock]:
        """
        Active un choc aléatoire avec une probabilité donnée
        """
        if random.random() < probability and self.shocks:
            # Choisir un choc inactif
            available = [s for s in self.shocks if not s.active]
            if available:
                shock = random.choice(available)
                shock.active = True
                shock.days_remaining = shock.duration_days
                self.active_shocks.append(shock)
                self.shock_history.append({
                    'name': shock.name,
                    'severity': shock.severity,
                    'activated_at': time.time(),
                    'duration_days': shock.duration_days
                })
                return shock
        return None

    def activate_specific_shock(self, shock_name: str) -> Optional[LogisticsShock]:
        """Active un choc spécifique par son nom"""
        for shock in self.shocks:
            if shock.name == shock_name and not shock.active:
                shock.active = True
                shock.days_remaining = shock.duration_days
                self.active_shocks.append(shock)
                self.shock_history.append({
                    'name': shock.name,
                    'severity': shock.severity,
                    'activated_at': time.time(),
                    'duration_days': shock.duration_days
                })
                return shock
        return None

    def update(self, days: int = 1, economy: Optional[Any] = None) -> Dict[str, Dict]:
        """
        Met à jour tous les chocs actifs
        Retourne les effets agrégés
        """
        aggregated_effects = {}
        self.active_shocks = []

        for shock in self.shocks:
            if shock.active:
                shock.update(days)
                if shock.active:
                    self.active_shocks.append(shock)
                    effects = shock.apply(economy)
                    aggregated_effects[shock.name] = effects

        return aggregated_effects

    def get_current_effects(self) -> Dict:
        """
        Agrège les effets de tous les chocs actifs
        """
        aggregated = {
            "travel_time_multiplier": 1.0,
            "import_delay_multiplier": 1.0,
            "degradation_increase": 0.0,
            "port_closed": False,
            "energy_price_multiplier": 1.0,
            "road_accessibility": 1.0
        }

        for shock in self.active_shocks:
            effects = shock.apply()
            for key, value in effects.items():
                if key in aggregated:
                    if isinstance(value, float) and isinstance(aggregated[key], float):
                        aggregated[key] *= value
                    elif isinstance(value, bool):
                        aggregated[key] = aggregated[key] or value
                else:
                    aggregated[key] = value

        return aggregated

    def get_statistics(self) -> Dict:
        """Statistiques des chocs"""
        total_activated = len(self.shock_history)
        return {
            'total_shocks': len(self.shocks),
            'active_shocks': len(self.active_shocks),
            'total_activated': total_activated,
            'history': self.shock_history[-10:] if self.shock_history else [],
            'current_effects': self.get_current_effects()
        }


# Exemple d'utilisation
if __name__ == "__main__":
    manager = ShockManager()

    # Ajout de chocs
    manager.add_shock(LogisticsShock("Port de Beyrouth fermé", severity=0.7, duration_days=45))
    manager.add_shock(LogisticsShock("Route nationale coupée", severity=0.4, duration_days=15))
    manager.add_shock(LogisticsShock("Pénurie de carburant", severity=0.5, duration_days=30))

    # Activation aléatoire
    shock = manager.activate_random_shock(probability=1.0)
    if shock:
        print(f"Choc activé: {shock.name}")

    # Mise à jour
    effects = manager.update(days=5)
    print(f"Effets: {effects}")

    # Statistiques
    print(f"Statistiques: {manager.get_statistics()}")

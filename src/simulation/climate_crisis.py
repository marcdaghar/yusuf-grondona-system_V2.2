"""
Crises climatiques
==================

Simule l'impact des crises climatiques sur le système monétaire
- Sécheresses
- Inondations
- Tempêtes
- Canicules
- Montée des eaux

Intègre les données COP et les scénarios du GIEC

License: CC BY-SA 4.0 – Marc Daghar
"""

import random
from typing import Dict, List, Optional, Any
from datetime import datetime
import time


class ClimateCrisisSimulator:
    """
    Simule l'impact des crises climatiques sur le système monétaire
    """

    def __init__(self):
        self.crisis_types = {
            "secheresse": {
                "food_supply_reduction": 0.3,
                "water_scarcity": 0.4,
                "crop_yield_reduction": 0.25,
                "duration_days": 90
            },
            "inondation": {
                "logistics_disruption": 0.5,
                "infrastructure_damage": 0.3,
                "displacement": 0.2,
                "duration_days": 45
            },
            "tempete": {
                "port_closed": True,
                "energy_grid_damage": 0.3,
                "transport_disruption": 0.5,
                "duration_days": 15
            },
            "canicule": {
                "energy_demand": 1.4,
                "agricultural_loss": 0.2,
                "health_impact": 0.3,
                "duration_days": 30
            },
            "montee_des_eaux": {
                "land_loss": 0.1,
                "refugee_inflow": 0.15,
                "coastal_damage": 0.3,
                "duration_days": 365
            }
        }

        self.history: List[Dict] = []

    def fetch_cop_data(self, year: int = 2024) -> Dict:
        """
        Récupère les données du rapport COP (simulé)
        """
        return {
            "year": year,
            "global_temp_rise": 1.2 + (year - 2020) * 0.02,  # °C
            "sea_level_rise": 0.18 + (year - 2020) * 0.005,  # m depuis 1990
            "extreme_events_frequency": 2.5 + (year - 2020) * 0.1,  # multiplicateur
            "affected_regions": ["Méditerranée", "Afrique du Nord", "Asie du Sud"],
            "co2_ppm": 420 + (year - 2020) * 2.5
        }

    def trigger_climate_shock(self, crisis_name: str,
                              severity_multiplier: float = 1.0) -> Dict:
        """
        Déclenche un choc climatique
        """
        if crisis_name not in self.crisis_types:
            return {"error": "Crise inconnue"}

        base_effects = self.crisis_types[crisis_name].copy()

        # Appliquer la sévérité
        for key in base_effects:
            if isinstance(base_effects[key], (int, float)):
                if key == "duration_days":
                    base_effects[key] = int(base_effects[key] * severity_multiplier)
                else:
                    base_effects[key] *= severity_multiplier

        base_effects["name"] = crisis_name
        base_effects["timestamp"] = time.time()
        base_effects["severity"] = severity_multiplier

        self.history.append(base_effects.copy())
        return base_effects

    def apply_to_economy(self, crisis_effects: Dict, economy_state: Dict) -> Dict:
        """
        Applique les effets de la crise à l'économie
        """
        new_state = economy_state.copy()

        if "food_supply_reduction" in crisis_effects:
            reduction = crisis_effects["food_supply_reduction"]
            new_state["food_supply"] = economy_state.get("food_supply", 1000) * (1 - reduction)
            new_state["price_bread"] = economy_state.get("price_bread", 1.0) * (1 + reduction * 2)

        if "logistics_disruption" in crisis_effects:
            new_state["delays_multiplier"] = 1 + crisis_effects["logistics_disruption"]

        if "port_closed" in crisis_effects:
            new_state["port_operational"] = False
            new_state["import_cost_multiplier"] = 2.0

        if "energy_demand" in crisis_effects:
            new_state["energy_price"] = economy_state.get("energy_price", 100) * crisis_effects["energy_demand"]

        if "agricultural_loss" in crisis_effects:
            new_state["agricultural_yield"] = economy_state.get("agricultural_yield", 1000) * (1 - crisis_effects["agricultural_loss"])

        if "refugee_inflow" in crisis_effects:
            new_state["population"] = economy_state.get("population", 100000) * (1 + crisis_effects["refugee_inflow"])
            new_state["zakat_emergency_multiplier"] = 1.5

        if "infrastructure_damage" in crisis_effects:
            new_state["infrastructure_index"] = economy_state.get("infrastructure_index", 1.0) * (1 - crisis_effects["infrastructure_damage"])

        if "crop_yield_reduction" in crisis_effects:
            new_state["crop_yield"] = economy_state.get("crop_yield", 1000) * (1 - crisis_effects["crop_yield_reduction"])

        return new_state

    def scenario_mediterranean_collapse(self) -> List[Dict]:
        """
        Scénario d'effondrement méditerranéen
        """
        timeline = []

        # Étape 1 : Sécheresse prolongée (jour 30)
        effects = self.trigger_climate_shock("secheresse", severity_multiplier=1.5)
        timeline.append({"day": 30, "effects": effects})

        # Étape 2 : Tempête (jour 120)
        effects = self.trigger_climate_shock("tempete", severity_multiplier=1.2)
        timeline.append({"day": 120, "effects": effects})

        # Étape 3 : Montée des eaux (jour 200)
        effects = self.trigger_climate_shock("montee_des_eaux", severity_multiplier=0.8)
        timeline.append({"day": 200, "effects": effects})

        # Étape 4 : Canicule (jour 250)
        effects = self.trigger_climate_shock("canicule", severity_multiplier=1.3)
        timeline.append({"day": 250, "effects": effects})

        return timeline

    def scenario_sahara_green(self) -> List[Dict]:
        """
        Scénario de reverdissement du Sahara (Blue Economy)
        """
        timeline = []

        # Investissements dans la Blue Economy
        effects = {
            "name": "investissement_blue_economy",
            "desalination_capacity": 200.0,  # millions m³/an
            "solar_potential": 2000.0,  # kWh/habitant
            "reforestation_area": 1000.0,  # km²
            "duration_days": 1825,  # 5 ans
            "timestamp": time.time(),
            "severity": 1.0,
            "type": "positive"
        }
        timeline.append({"day": 0, "effects": effects})

        return timeline

    def get_cop_scenario(self, scenario_name: str = "ssp2_45") -> Dict:
        """
        Récupère un scénario COP (SSP)
        """
        scenarios = {
            "ssp1_26": {
                "name": "Développement durable",
                "temp_rise_2100": 1.8,
                "emissions_2050": -50,
                "sea_level_rise_2100": 0.4
            },
            "ssp2_45": {
                "name": "Milieu de route",
                "temp_rise_2100": 2.7,
                "emissions_2050": 0,
                "sea_level_rise_2100": 0.6
            },
            "ssp3_70": {
                "name": "Rivalité régionale",
                "temp_rise_2100": 3.6,
                "emissions_2050": 50,
                "sea_level_rise_2100": 0.8
            },
            "ssp5_85": {
                "name": "Croissance rapide",
                "temp_rise_2100": 4.4,
                "emissions_2050": 100,
                "sea_level_rise_2100": 1.1
            }
        }

        return scenarios.get(scenario_name, scenarios["ssp2_45"])

    def get_statistics(self) -> Dict:
        """
        Statistiques des chocs climatiques
        """
        return {
            'total_shocks': len(self.history),
            'shocks': self.history[-10:] if self.history else [],
            'available_crises': list(self.crisis_types.keys())
        }


# Exemple d'utilisation
if __name__ == "__main__":
    climate = ClimateCrisisSimulator()

    # Scénario méditerranéen
    timeline = climate.scenario_mediterranean_collapse()
    print("=== SCÉNARIO MÉDITERRANÉEN ===")
    for event in timeline:
        print(f"Jour {event['day']}: {event['effects']['name']}")

    # Application à une économie simulée
    economy = {
        "food_supply": 5000,
        "price_bread": 1.0,
        "population": 500000,
        "energy_price": 100,
        "agricultural_yield": 1000
    }

    shock = climate.trigger_climate_shock("secheresse", severity_multiplier=1.2)
    new_economy = climate.apply_to_economy(shock, economy)

    print("\n=== IMPACT ÉCONOMIQUE ===")
    for key, value in new_economy.items():
        print(f"{key}: {value}")

"""
Scénarios de crise
==================

Scénarios :
- Invasion (rupture des chaînes d'approvisionnement, afflux de réfugiés)
- Famine (réduction des stocks alimentaires, hausse des prix)
- Panique financière (thésaurisation, fuite des capitaux)

Réponses :
- CRD : libération des stocks
- Zakat : redistribution d'urgence
- Hisba : renforcement des contrôles

License: CC BY-SA 4.0 – Marc Daghar
"""

from typing import Dict, List, Optional, Any
import time


class CrisisScenario:
    """
    Un scénario de crise
    """

    def __init__(self, name: str, severity: float = 0.5):
        self.name = name
        self.severity = severity  # 0-1
        self.active = False
        self.start_time = 0
        self.duration_days = 90  # Durée par défaut
        self.effects: Dict[str, Any] = {}

    def apply(self, economy: Optional[Any] = None) -> Dict:
        """
        Applique les effets de la crise
        """
        effects = {}

        if "invasion" in self.name.lower():
            effects["supply_chain_cut"] = self.severity
            effects["refugee_inflow"] = self.severity * 0.5
            effects["infrastructure_damage"] = self.severity * 0.3
            effects["price_shock"] = 1 + self.severity * 0.5

        elif "famine" in self.name.lower():
            effects["food_supply_reduction"] = self.severity
            effects["price_shock"] = 1 + self.severity
            effects["malnutrition_rate"] = self.severity * 0.3
            effects["social_unrest"] = self.severity * 0.4

        elif "financial_panic" in self.name.lower():
            effects["fulus_hoarding"] = self.severity
            effects["capital_flight"] = self.severity * 0.6
            effects["bank_runs"] = self.severity * 0.5
            effects["exchange_rate_shock"] = self.severity * 0.3

        elif "climat" in self.name.lower() or "climate" in self.name.lower():
            effects["crop_damage"] = self.severity * 0.6
            effects["water_scarcity"] = self.severity * 0.4
            effects["displacement"] = self.severity * 0.3

        self.effects = effects
        return effects

    def get_response_plan(self) -> List[str]:
        """Plan de réponse à la crise"""
        responses = []

        if self.name == "famine" or self.name == "crop_damage":
            responses.append("Libération des stocks CRD")
            responses.append("Distribution Zakat d'urgence")
            responses.append("Contrôle des prix par le muhtassib")

        elif "invasion" in self.name.lower():
            responses.append("Activation des réserves stratégiques")
            responses.append("Relocalisation des populations vulnérables")
            responses.append("Renforcement des inspections aux frontières")

        elif "financial_panic" in self.name.lower():
            responses.append("Suspension temporaire de la convertibilité")
            responses.append("Garantie des dépôts en nuqud")
            responses.append("Appel à la solidarité des guildes")

        elif "climat" in self.name.lower():
            responses.append("Déploiement de l'aide humanitaire")
            responses.append("Programmes de résilience")
            responses.append("Accélération de la transition énergétique")

        return responses


class CrisisManager:
    """
    Gestionnaire des crises
    """

    def __init__(self, crd: Optional[Any] = None, bayt_al_mal: Optional[Any] = None):
        self.crd = crd
        self.bayt_al_mal = bayt_al_mal
        self.active_crisis: Optional[CrisisScenario] = None
        self.crisis_history: List[Dict] = []
        self.response_history: List[Dict] = []

    def trigger_crisis(self, crisis: CrisisScenario) -> Dict:
        """
        Déclenche une crise
        """
        self.active_crisis = crisis
        crisis.active = True
        crisis.start_time = time.time()

        effects = crisis.apply()

        self.crisis_history.append({
            'name': crisis.name,
            'severity': crisis.severity,
            'start_time': crisis.start_time,
            'effects': effects
        })

        return effects

    def response_plan(self, effects: Dict) -> List[str]:
        """
        Exécute le plan de réponse
        """
        responses = []

        if self.active_crisis:
            # 1. CRD : libération des stocks
            if self.crd and "food_supply_reduction" in effects:
                release_qty = self.crd.release_food(effects["food_supply_reduction"] * 100)
                responses.append(f"CRD a libéré {release_qty} tonnes de céréales")

            # 2. Zakat : redistribution d'urgence
            if self.bayt_al_mal and self.bayt_al_mal.zakat_funds > 0:
                amount = self.bayt_al_mal.zakat_funds * 0.5
                # Distribution simplifiée
                self.bayt_al_mal.zakat_funds -= amount
                responses.append(f"Bayt al-mal a distribué {amount} nuqud aux sinistrés")

            # 3. Hisba : renforcement des contrôles
            responses.append("Muhtassib : renforcement des inspections")

        self.response_history.append({
            'crisis': self.active_crisis.name if self.active_crisis else "unknown",
            'responses': responses,
            'timestamp': time.time()
        })

        return responses

    def update(self, days: int = 1, economy: Optional[Any] = None) -> None:
        """
        Met à jour la crise en cours
        """
        if self.active_crisis:
            self.active_crisis.duration_days -= days
            if self.active_crisis.duration_days <= 0:
                self.active_crisis.active = False
                self.active_crisis = None

    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques des crises
        """
        return {
            'total_crises': len(self.crisis_history),
            'active_crisis': self.active_crisis.name if self.active_crisis else None,
            'crisis_history': self.crisis_history[-5:] if self.crisis_history else [],
            'response_history': self.response_history[-3:] if self.response_history else []
        }


# Exemple d'utilisation
if __name__ == "__main__":
    manager = CrisisManager()

    # Déclenchement d'une crise
    crisis = CrisisScenario("famine", severity=0.6)
    effects = manager.trigger_crisis(crisis)
    print(f"Crise déclenchée: {crisis.name}")
    print(f"Effets: {effects}")

    # Plan de réponse
    responses = manager.response_plan(effects)
    for r in responses:
        print(f"  → {r}")

    # Statistiques
    print(f"Statistiques: {manager.get_statistics()}")

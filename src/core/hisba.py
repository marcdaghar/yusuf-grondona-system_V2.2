"""
Hisba (حسبة) – Inspection du marché
===================================

La Hisba est la fonction d'inspection et de régulation du marché.
Elle garantit :
- La justesse des poids et mesures
- La conformité halal des produits
- La prévention des fraudes
- La protection du consommateur

Le muhtassib est l'inspecteur du marché. L'IA l'assiste,
mais la décision finale lui revient.

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time
import datetime


@dataclass
class MarketInspection:
    """
    Enregistrement d'une inspection du marché
    """
    market_name: str
    timestamp: float = field(default_factory=time.time)
    incidents: List[Dict] = field(default_factory=list)

    def check_scale(self, declared_kg: float, actual_kg: float,
                    tolerance: float = 0.02) -> bool:
        """
        Vérifie la justesse des poids
        """
        if actual_kg == 0:
            return False

        error = abs(declared_kg - actual_kg) / actual_kg
        if error > tolerance:
            self.incidents.append({
                "type": "scale_fraud",
                "declared": declared_kg,
                "actual": actual_kg,
                "error": error,
                "severity": "high" if error > 0.1 else "medium",
                "timestamp": time.time()
            })
            return False
        return True

    def verify_halal_certificate(self, product: str,
                                 certificate_present: bool,
                                 trusted_source: bool,
                                 expiry_date: Optional[str] = None) -> bool:
        """
        Vérifie le certificat halal
        """
        if not certificate_present:
            self.incidents.append({
                "type": "halal_certificate_missing",
                "product": product,
                "severity": "high",
                "timestamp": time.time()
            })
            return False

        if not trusted_source:
            self.incidents.append({
                "type": "halal_source_untrusted",
                "product": product,
                "severity": "medium",
                "timestamp": time.time()
            })
            return False

        # Vérification de l'expiration (optionnelle)
        if expiry_date:
            try:
                expiry = datetime.datetime.fromisoformat(expiry_date)
                if expiry < datetime.datetime.now():
                    self.incidents.append({
                        "type": "halal_certificate_expired",
                        "product": product,
                        "expiry_date": expiry_date,
                        "severity": "high",
                        "timestamp": time.time()
                    })
                    return False
            except ValueError:
                pass

        return True

    def check_price(self, price: float, reference_price: float,
                    max_deviation: float = 0.2) -> bool:
        """
        Vérifie que le prix n'est pas excessif
        """
        if reference_price == 0:
            return True

        deviation = abs(price - reference_price) / reference_price
        if deviation > max_deviation:
            self.incidents.append({
                "type": "price_anomaly",
                "price": price,
                "reference": reference_price,
                "deviation": deviation,
                "severity": "medium" if deviation > 0.5 else "low",
                "timestamp": time.time()
            })
            return False
        return True

    def check_quality(self, product: str, quality_grade: str,
                      declared_grade: str) -> bool:
        """
        Vérifie que la qualité déclarée correspond à la réalité
        """
        grade_order = ["low", "medium", "high", "premium"]

        if quality_grade not in grade_order or declared_grade not in grade_order:
            return True

        if grade_order.index(quality_grade) < grade_order.index(declared_grade):
            self.incidents.append({
                "type": "quality_misrepresentation",
                "product": product,
                "declared": declared_grade,
                "actual": quality_grade,
                "severity": "medium",
                "timestamp": time.time()
            })
            return False
        return True

    def report(self) -> Dict:
        """Génère un rapport de l'inspection"""
        return {
            "market": self.market_name,
            "incidents": self.incidents,
            "total_incidents": len(self.incidents),
            "high_severity": sum(1 for i in self.incidents if i.get("severity") == "high"),
            "timestamp": self.timestamp
        }


class Muhtassib:
    """
    Muhtassib – Inspecteur du marché
    """

    def __init__(self, name: str, jurisdiction: str,
                 reputation: float = 50.0):
        """
        Args:
            name: Nom du muhtassib
            jurisdiction: Zone de compétence
            reputation: Score de réputation (0-100)
        """
        self.name = name
        self.jurisdiction = jurisdiction
        self.reputation = reputation
        self.inspections: List[MarketInspection] = []
        self.decisions: List[Dict] = []

    def inspect(self, market_inspection: MarketInspection) -> Dict:
        """
        Effectue une inspection
        """
        self.inspections.append(market_inspection)

        # Mise à jour de la réputation en fonction des incidents
        report = market_inspection.report()
        if report["total_incidents"] == 0:
            self.reputation = min(100, self.reputation + 0.5)
        else:
            self.reputation = max(0, self.reputation - report["high_severity"] * 1.0)

        return report

    def make_decision(self, incident: Dict) -> Dict:
        """
        Prend une décision suite à un incident
        """
        decision = {
            "incident": incident,
            "muhtassib": self.name,
            "reputation": self.reputation,
            "timestamp": time.time()
        }

        # Décision basée sur la sévérité et la réputation
        severity = incident.get("severity", "medium")

        if severity == "high":
            if self.reputation > 80:
                decision["action"] = "BLOCK"  # Blocage immédiat
            else:
                decision["action"] = "FLAG"   # Signalement
            decision["sanction"] = "amende_500_fulus"

        elif severity == "medium":
            decision["action"] = "FLAG"
            decision["sanction"] = "avertissement"

        else:
            decision["action"] = "NOTE"
            decision["sanction"] = "observation"

        self.decisions.append(decision)
        return decision

    def summarize(self) -> Dict:
        """Résumé des activités du muhtassib"""
        all_incidents = []
        for insp in self.inspections:
            all_incidents.extend(insp.incidents)

        return {
            "muhtassib": self.name,
            "jurisdiction": self.jurisdiction,
            "reputation": self.reputation,
            "total_inspections": len(self.inspections),
            "total_incidents": len(all_incidents),
            "total_decisions": len(self.decisions),
            "latest_incidents": all_incidents[-5:] if all_incidents else [],
            "latest_decisions": self.decisions[-3:] if self.decisions else []
        }

    def verify_merchant(self, merchant_id: str, merchant_history: List[Dict]) -> Dict:
        """
        Vérifie un commerçant avant de lui permettre d'exercer
        """
        # Nombre de plaintes antérieures
        complaints = [h for h in merchant_history if h.get("type") == "complaint"]
        frauds = [h for h in merchant_history if h.get("type") == "fraud"]

        status = "APPROVED"
        warnings = []

        if len(frauds) > 3:
            status = "SUSPENDED"
            warnings.append("Multiple fraudes détectées")
        elif len(complaints) > 5:
            status = "MONITORED"
            warnings.append("Nombre élevé de plaintes")
        elif len(frauds) > 0:
            status = "MONITORED"
            warnings.append("Au moins une fraude détectée")

        return {
            "merchant": merchant_id,
            "status": status,
            "warnings": warnings,
            "reviewed_by": self.name,
            "timestamp": time.time()
        }


# Exemple d'utilisation
if __name__ == "__main__":
    # Création du muhtassib
    muhtassib = Muhtassib("Ahmed", "Marseille")

    # Inspection
    inspection = MarketInspection("Grand Souq de Marseille")

    # Tests
    inspection.check_scale(100, 98)  # Toléré
    inspection.check_scale(100, 85)  # Fraude

    inspection.verify_halal_certificate("Viande", True, True)
    inspection.verify_halal_certificate("Sans certificat", False, False)

    # Rapport
    report = muhtassib.inspect(inspection)
    print("=== RAPPORT DE HISSBA ===")
    print(f"Muhtassib: {muhtassib.name}")
    print(f"Réputation: {muhtassib.reputation:.1f}")
    print(f"Incidents: {report['total_incidents']}")

    # Décision
    if report["incidents"]:
        decision = muhtassib.make_decision(report["incidents"][0])
        print(f"Décision: {decision['action']} – {decision['sanction']}")

    print("\nRésumé:")
    print(muhtassib.summarize())

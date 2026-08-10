"""
Test de résistance du système
=============================

Compare les performances du système avec/sans CRD, avec/sans Zakat

License: CC BY-SA 4.0 – Marc Daghar
"""

import copy
from typing import Dict, List, Optional, Any

from .run_full import run_full_simulation, SimulationConfig


class StressTest:
    """
    Test de résistance du système Yusuf-Grondona
    """

    def __init__(self, base_config: Optional[SimulationConfig] = None):
        self.base_config = base_config or SimulationConfig()
        self.results: Dict[str, Dict] = {}

    def run_scenario(self, name: str, modifications: Dict) -> Dict:
        """
        Exécute un scénario de test
        """
        config = copy.deepcopy(self.base_config)

        # Application des modifications
        for key, value in modifications.items():
            if hasattr(config, key):
                setattr(config, key, value)

        results = run_full_simulation(config)
        self.results[name] = self._extract_metrics(results)

        return results

    def _extract_metrics(self, results: Dict) -> Dict:
        """
        Extrait les métriques clés des résultats
        """
        # Calcul des statistiques des prix
        price_stats = {}
        for product, history in results.get("price_history", {}).items():
            prices = [h["price"] for h in history]
            if prices:
                price_stats[product] = {
                    "mean": sum(prices) / len(prices),
                    "volatility": self._compute_volatility(prices),
                    "min": min(prices),
                    "max": max(prices)
                }

        return {
            "n_transactions": len(results.get("transactions", [])),
            "zakat_collected": results.get("zakat_collected", 0),
            "crd_releases": len(results.get("crd_releases", [])),
            "bri_transfers": len(results.get("bri_transfers", [])),
            "blockchain_blocks": results.get("blockchain_blocks", 0),
            "shocks_activated": len(results.get("shocks_activated", [])),
            "price_statistics": price_stats,
            "total_volume": sum(
                h["quantity"] for h in results.get("transactions", [])
            )
        }

    def _compute_volatility(self, prices: List[float]) -> float:
        """Calcule la volatilité des prix"""
        if len(prices) < 2:
            return 0.0

        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        return variance ** 0.5 / mean if mean > 0 else 0.0

    def compare_all(self) -> Dict:
        """
        Compare tous les scénarios
        """
        scenarios = {
            "Sans CRD, sans Zakat": {"use_crd": False, "use_zakat": False},
            "Sans CRD, avec Zakat": {"use_crd": False, "use_zakat": True},
            "Avec CRD, sans Zakat": {"use_crd": True, "use_zakat": False},
            "Avec CRD, avec Zakat": {"use_crd": True, "use_zakat": True},
            "CRD + Zakat + BRI": {"use_crd": True, "use_zakat": True, "use_bri": True},
            "Système complet": {"use_crd": True, "use_zakat": True, "use_bri": True, "use_blockchain": True},
        }

        for name, mods in scenarios.items():
            print(f"🔁 Lancement : {name}...")
            self.run_scenario(name, mods)

        return self.results

    def generate_report(self) -> str:
        """
        Génère un rapport des résultats
        """
        report = []
        report.append("=" * 70)
        report.append("🧪 TEST DE RÉSISTANCE – Yusuf-Grondona System")
        report.append("=" * 70)
        report.append("")

        for scenario, data in self.results.items():
            report.append(f"📊 {scenario}")
            report.append("-" * 50)
            report.append(f"   Transactions : {data['n_transactions']}")
            report.append(f"   Zakat collectée : {data['zakat_collected']:.2f}")
            report.append(f"   Interventions CRD : {data['crd_releases']}")
            report.append(f"   Transferts BRI : {data['bri_transfers']}")
            report.append(f"   Blocs blockchain : {data['blockchain_blocks']}")
            report.append(f"   Chocs activés : {data['shocks_activated']}")

            # Statistiques des prix
            for product, stats in data.get("price_statistics", {}).items():
                report.append(f"   Prix ({product}): {stats['mean']:.2f} ± {stats['volatility']:.2f}")
            report.append("")

        # Conclusion
        report.append("=" * 70)
        report.append("📌 CONCLUSION :")

        # Meilleur scénario
        if self.results:
            best = max(self.results.items(), key=lambda x: x[1]["n_transactions"])
            report.append(f"   Plus de transactions : {best[0]}")

            lowest_volatility = min(
                self.results.items(),
                key=lambda x: sum(s.get("volatility", 0) for s in x[1].get("price_statistics", {}).values())
            )
            report.append(f"   Plus faible volatilité : {lowest_volatility[0]}")

            # Scénario avec Zakat
            zakat_scenarios = [(n, d) for n, d in self.results.items() if "Zakat" in n]
            if zakat_scenarios:
                max_zakat = max(zakat_scenarios, key=lambda x: x[1]["zakat_collected"])
                report.append(f"   Plus de Zakat collectée : {max_zakat[0]}")

        report.append("=" * 70)

        return "\n".join(report)

    def export_results(self, filepath: str = "stress_test_results.json") -> None:
        """
        Exporte les résultats au format JSON
        """
        import json
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"✅ Résultats exportés dans {filepath}")


# Exemple d'utilisation
if __name__ == "__main__":
    print("🧪 TEST DE RÉSISTANCE DU SYSTÈME YUSUF-GRONDONA")
    print("=" * 60)

    # Configuration
    config = SimulationConfig(
        years=1,
        use_crd=True,
        use_zakat=True,
        use_bri=True,
        use_blockchain=True,
        use_shocks=True
    )

    # Exécution des tests
    stress = StressTest(config)
    stress.compare_all()

    # Rapport
    report = stress.generate_report()
    print(report)

    # Export
    stress.export_results()

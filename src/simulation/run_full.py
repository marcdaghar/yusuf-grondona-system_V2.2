"""
Simulation complète du système Yusuf-Grondona
============================================

Intègre :
- Agents (guildes, commerçants, consommateurs, muhtassib)
- Marché (souq) avec appariement main à main
- CRD Grondona (prix plancher/plafond)
- Zakat (collectée par l'émir)
- BRI Network (transferts inter-zones)
- Blockchain (traçabilité SHA256)
- Chocs logistiques et crises

License: CC BY-SA 4.0 – Marc Daghar
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .agents import Guilde, Commercant, Consommateur, MuhtassibAgent
from .market_advanced import Souq, Product
from .blockchain_sim import Blockchain
from .logistics_shocks import ShockManager, LogisticsShock
from .crisis_scenarios import CrisisManager, CrisisScenario
from .climate_crisis import ClimateCrisisSimulator

from src.core.bri_network import BRINetwork, ZoneBRI, create_default_network
from src.core.grondona_crd import GrondonaCRD, CommodityInBasket
from src.core.zakat_nuqud import ZakatOnNuqud, ZakatCategory
from src.core.hisba import Muhtassib


@dataclass
class SimulationConfig:
    """Configuration de la simulation"""
    years: int = 1
    use_crd: bool = True
    use_zakat: bool = True
    use_bri: bool = True
    use_blockchain: bool = True
    use_shocks: bool = True
    use_climate: bool = True

    # Paramètres économiques
    initial_guilde_fulus: float = 1000.0
    initial_commercant_fulus: float = 2000.0
    initial_consommateur_fulus: float = 500.0

    # Paramètres CRD
    floor_prices: Dict[str, float] = field(default_factory=lambda: {
        "pain": 0.8, "riz": 1.0, "viande": 4.0, "blé": 180.0
    })
    ceiling_prices: Dict[str, float] = field(default_factory=lambda: {
        "pain": 1.5, "riz": 2.0, "viande": 7.0, "blé": 220.0
    })

    # Paramètres Zakat
    zakat_rate: float = 0.025
    nisab_gold: float = 85.0
    nisab_silver: float = 595.0


def run_full_simulation(config: Optional[SimulationConfig] = None) -> Dict:
    """
    Exécute la simulation complète
    """
    if config is None:
        config = SimulationConfig()

    print("=" * 60)
    print("🚀 SIMULATION YUSUF-GRONDONA")
    print("=" * 60)

    # ---- Initialisation ----

    # 1. CRD Grondona
    commodities = []
    for name, floor in config.floor_prices.items():
        ceiling = config.ceiling_prices.get(name, floor * 1.5)
        commodities.append(CommodityInBasket(
            name=name,
            floor_price=floor,
            ceiling_price=ceiling,
            current_price=(floor + ceiling) / 2
        ))

    crd = GrondonaCRD(commodities, initial_currency_supply=10000) if config.use_crd else None

    # 2. Agents
    guilde = Guilde("Boulangerie Centrale", "Marseille", production_capacity=1000)
    commercant = Commercant("Épicerie Al-Nour", "Marseille", fulus=config.initial_commercant_fulus)
    consommateur = Consommateur("Claire", fulus=config.initial_consommateur_fulus)
    muhtassib = MuhtassibAgent("Ahmed", "Marseille")

    # 3. Marché
    souq = Souq("Grand Souq", "Marseille", crd=crd, muhtassib=muhtassib)

    # 4. BRI Network
    bri_network = create_default_network() if config.use_bri else None

    # 5. Blockchain
    blockchain = Blockchain() if config.use_blockchain else None

    # 6. Chocs logistiques
    shock_manager = ShockManager() if config.use_shocks else None
    if shock_manager:
        shock_manager.add_shock(LogisticsShock("Port fermé", severity=0.7, duration_days=30))
        shock_manager.add_shock(LogisticsShock("Route coupée", severity=0.4, duration_days=15))

    # 7. Crises
    crisis_manager = CrisisManager(crd, None) if config.use_shocks else None

    # 8. Climat
    climate = ClimateCrisisSimulator() if config.use_climate else None

    # ---- Variables de suivi ----
    results = {
        "years": config.years,
        "transactions": [],
        "zakat_collected": 0.0,
        "crd_releases": [],
        "shocks_activated": [],
        "crises_triggered": [],
        "bri_transfers": [],
        "blockchain_blocks": 0,
        "price_history": {},
        "volume_history": {},
    }

    # ---- Boucle temporelle ----
    for year in range(1, config.years + 1):
        print(f"\n📅 Année {year}")

        for day in range(1, 366):
            # Activation des chocs (tous les 30 jours)
            if shock_manager and day % 30 == 0:
                shock = shock_manager.activate_random_shock(probability=0.2)
                if shock:
                    results["shocks_activated"].append({
                        "year": year,
                        "day": day,
                        "name": shock.name,
                        "severity": shock.severity
                    })

            # Déclenchement d'une crise (à mi-année)
            if crisis_manager and year == 1 and day == 180:
                crisis = CrisisScenario("famine", severity=0.6)
                effects = crisis_manager.trigger_crisis(crisis)
                results["crises_triggered"].append({
                    "year": year,
                    "name": "famine",
                    "effects": effects
                })

            # Production
            guilde.produce("pain", 200)

            # Offres et demandes
            guilde.offer_to_souq(souq, "pain", 100, 1.2)
            commercant.buy_from_souq(souq, "pain", 50, 1.5)

            # Appariement
            transactions = souq.match(muhtassib)

            for tx in transactions:
                results["transactions"].append({
                    "year": year,
                    "day": day,
                    "product": tx.product,
                    "quantity": tx.quantity,
                    "price": tx.price_per_unit,
                    "total": tx.total_price,
                    "inspected": tx.inspected,
                    "inspector": tx.inspector
                })

                # Blockchain
                if blockchain:
                    blockchain.add_transaction({
                        "type": "sale",
                        "product": tx.product,
                        "quantity": tx.quantity,
                        "price": tx.price_per_unit,
                        "buyer": str(tx.buyer),
                        "seller": str(tx.seller),
                        "timestamp": tx.timestamp
                    })

            # CRD (intervention mensuelle)
            if crd and day % 30 == 0:
                # Simuler une intervention
                crd.release_food(10.0, "pain")
                results["crd_releases"].append({
                    "year": year,
                    "day": day,
                    "amount": 10.0,
                    "commodity": "pain"
                })

        # ---- Fin d'année ----

        # Zakat
        if config.use_zakat:
            zakat_result = ZakatOnNuqud.calculate(
                nuqud_holdings=[],
                trade_profit_nuqud=5000.0
            )
            zakat_amount = zakat_result["total_zakat"]
            results["zakat_collected"] += zakat_amount

            if blockchain:
                blockchain.add_transaction({
                    "type": "zakat",
                    "amount": zakat_amount,
                    "currency": "nuqud",
                    "year": year
                })

        # Minage des blocs blockchain
        if blockchain:
            blockchain.mine_pending_transactions()
            results["blockchain_blocks"] = len(blockchain.chain)

        # Transfert BRI (annuel)
        if bri_network:
            transfer_result = bri_network.transfer("Chine", "NUL", 100.0)
            if transfer_result.get("success"):
                results["bri_transfers"].append({
                    "year": year,
                    "from": "Chine",
                    "to": "NUL",
                    "amount": 100.0,
                    "result": transfer_result
                })

        # Enregistrement des prix
        for product in souq.price_history:
            if product not in results["price_history"]:
                results["price_history"][product] = []
            avg_price = souq.get_average_price(product)
            results["price_history"][product].append({
                "year": year,
                "price": avg_price
            })

    # ---- Bilan ----
    print("\n📊 RÉSULTATS DE LA SIMULATION")
    print("-" * 40)
    print(f"Transactions: {len(results['transactions'])}")
    print(f"Zakat collectée: {results['zakat_collected']:.2f} g eq")
    print(f"Blocs minés: {results['blockchain_blocks']}")
    print(f"Transferts BRI: {len(results['bri_transfers'])}")
    print(f"Chocs activés: {len(results['shocks_activated'])}")

    # Statistiques du marché
    stats = souq.get_statistics()
    print(f"\n📈 Statistiques du marché:")
    print(f"  Prix moyens: {stats['average_prices']}")
    print(f"  Volumes totaux: {stats['total_volumes']}")

    return results


def run_one_year() -> Dict:
    """Exécute une simulation d'un an avec les paramètres par défaut"""
    config = SimulationConfig(years=1)
    return run_full_simulation(config)


# Exemple d'utilisation
if __name__ == "__main__":
    results = run_one_year()

    # Sauvegarde des résultats
    with open("results_simulation.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n✅ Résultats sauvegardés dans results_simulation.json")

"""
Tests d'intégration
===================

Tests d'intégration entre les différents modules.

License: CC BY-SA 4.0 – Marc Daghar
"""

import pytest
import sys
import os
import json
import tempfile
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.bri_network import BRINetwork, ZoneBRI
from src.core.grondona_crd import GrondonaCRD, CommodityInBasket
from src.simulation.run_full import run_full_simulation, SimulationConfig
from src.simulation.market_advanced import Souq
from src.simulation.agents import Guilde, Commercant, Consommateur, MuhtassibAgent
from src.governance.bayt_al_mal import BaytAlMal
from src.core.zakat_nuqud import ZakatOnNuqud
from database.db_manager import init_db, save_simulation, get_simulation_history
from api.main import app

client = TestClient(app)


# ============================================================
# Tests de simulation
# ============================================================

class TestSimulation:
    def test_simulation_run(self):
        """Test d'exécution de la simulation"""
        config = SimulationConfig(
            years=1,
            use_crd=True,
            use_zakat=True,
            use_bri=True,
            use_blockchain=True,
            use_shocks=False
        )
        
        results = run_full_simulation(config)
        
        assert "transactions" in results
        assert "zakat_collected" in results
        assert "bri_transfers" in results
        assert "blockchain_blocks" in results

    def test_simulation_without_crd(self):
        """Test de simulation sans CRD"""
        config = SimulationConfig(
            years=1,
            use_crd=False,
            use_zakat=True,
            use_bri=False,
            use_blockchain=False
        )
        
        results = run_full_simulation(config)
        
        assert len(results["crd_releases"]) == 0


# ============================================================
# Tests d'intégration BRI + CRD
# ============================================================

class TestBRIWithCRD:
    def test_bri_transfer_with_crd(self):
        """Test de transfert BRI avec CRD"""
        network = BRINetwork()
        zone_a = ZoneBRI("ZoneA", "CityA", 2000)
        zone_b = ZoneBRI("ZoneB", "CityB", 500)
        network.add_zone(zone_a)
        network.add_zone(zone_b)
        
        from src.core.bri_network import LiquidityBridge
        bridge = LiquidityBridge("ZoneA", "ZoneB")
        network.bridges.append(bridge)
        
        # CRD
        commodities = [
            CommodityInBasket("Wheat", 180, 220, 200)
        ]
        crd = GrondonaCRD(commodities)
        
        # Transfert
        result = network.transfer("ZoneA", "ZoneB", 100)
        assert "error" not in result
        
        # Vérification des réserves
        assert zone_a.nuqud_reserve_grams == 1900
        assert zone_b.nuqud_reserve_grams == 600


# ============================================================
# Tests d'intégration Marché + Zakat
# ============================================================

class TestMarketWithZakat:
    def test_market_transaction_with_zakat(self):
        """Test de transaction avec Zakat"""
        # Création des acteurs
        guilde = Guilde("Boulangerie", "Test", production_capacity=1000)
        commercant = Commercant("Épicerie", "Test")
        muhtassib = MuhtassibAgent("Ahmed", "Test")
        
        # Marché
        souq = Souq("Test Souq", "Test")
        
        # Production et offre
        guilde.produce("pain", 200)
        guilde.offer_to_souq(souq, "pain", 100, 2.0)
        commercant.buy_from_souq(souq, "pain", 50, 2.5)
        
        # Appariement
        transactions = souq.match(muhtassib)
        assert len(transactions) > 0
        
        # Zakat
        zakat_result = ZakatOnNuqud.calculate(
            nuqud_holdings=[],
            trade_profit_nuqud=500.0
        )
        assert zakat_result["total_zakat"] > 0


# ============================================================
# Tests d'intégration Base de données
# ============================================================

class TestDatabase:
    def test_db_init(self):
        """Test d'initialisation de la base de données"""
        init_db()
        
        import sqlite3
        conn = sqlite3.connect("yusuf_grondona.db")
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert "simulations" in tables
        assert "bri_transfers" in tables
        assert "zakat_payments" in tables
        conn.close()

    def test_db_save_simulation(self):
        """Test de sauvegarde d'une simulation"""
        config = {"years": 1, "test": True}
        results = {"transactions": [], "zakat_collected": 100.0}
        
        sim_id = save_simulation(config, results)
        assert sim_id > 0

    def test_db_history(self):
        """Test de récupération de l'historique"""
        history = get_simulation_history(limit=5)
        assert isinstance(history, list)

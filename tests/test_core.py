"""
Tests du noyau (core/)
======================

Tests unitaires pour les modules core/ :
- nuqud.py
- fulus.py
- grondona_crd.py
- bri_network.py
- hisba.py
- zakat_nuqud.py
- riba_rules.py

License: CC BY-SA 4.0 – Marc Daghar
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.nuqud import Nuqud, NuqudSystem, PRIMARY_NUQUD
from src.core.fulus import Fulus, FulusCurrency, FulusSignalSystem
from src.core.grondona_crd import GrondonaCRD, CommodityInBasket
from src.core.bri_network import BRINetwork, ZoneBRI, LiquidityBridge
from src.core.hisba import Muhtassib, MarketInspection
from src.core.zakat_nuqud import ZakatOnNuqud, ZakatCategory
from src.core.riba_rules import RibaController, AssetClass, RIBA_RULES


# ============================================================
# Tests Nuqud
# ============================================================

class TestNuqud:
    def test_nuqud_creation(self):
        """Test de création d'un nuqud"""
        n = Nuqud("gold", 10.0)
        assert n.metal_type == "gold"
        assert n.weight_grams == 10.0
        assert n.owner is None

    def test_nuqud_value_conversion(self):
        """Test de conversion de valeur"""
        gold = Nuqud("gold", 10.0)
        silver = Nuqud("silver", 100.0)
        
        assert gold.value_in_grams_of_silver() == 100.0  # 10 * 10
        assert silver.value_in_grams_of_silver() == 100.0

    def test_nisab_check(self):
        """Test de vérification du Nisab"""
        gold_below = Nuqud("gold", 50.0)
        gold_above = Nuqud("gold", 100.0)
        silver_below = Nuqud("silver", 500.0)
        silver_above = Nuqud("silver", 600.0)
        
        assert gold_below.is_above_nisab() is False
        assert gold_above.is_above_nisab() is True
        assert silver_below.is_above_nisab() is False
        assert silver_above.is_above_nisab() is True


    def test_zakat_calculation(self):
        """Test de calcul de Zakat sur nuqud"""
        gold = Nuqud("gold", 100.0)
        silver = Nuqud("silver", 600.0)
        
        assert gold.zakat_due() == 2.5  # 100 * 0.025
        assert silver.zakat_due() == 15.0  # 600 * 0.025

    def test_nuqud_system(self):
        """Test du système nuqud"""
        system = NuqudSystem()
        
        # Stockage de valeur
        result = system.store_value("Gold", 1000.0)
        assert result["status"] == "value_stored"
        assert system.get_reserve("Gold") == 1000.0
        
        # Retrait de valeur
        result = system.withdraw_value("Gold", 500.0)
        assert result["status"] == "value_withdrawn"
        assert system.get_reserve("Gold") == 500.0


# ============================================================
# Tests Fulus
# ============================================================

class TestFulus:
    def test_fulus_creation(self):
        """Test de création d'un fulus"""
        f = Fulus(100.5, "test_guilde")
        assert f.amount == 100.5
        assert f.issued_by == "test_guilde"
        assert f.velocity_target == 10.0

    def test_fulus_currency(self):
        """Test de la monnaie fulus"""
        currency = FulusCurrency("Test", "TST")
        
        # Émission
        result = currency.issue(1000, "test")
        assert result["status"] == "issued"
        assert currency.circulation_supply == 1000
        
        # Destruction
        result = currency.destroy(300)
        assert result["status"] == "destroyed"
        assert currency.circulation_supply == 700

    def test_velocity(self):
        """Test de la vélocité"""
        currency = FulusCurrency("Test", "TST")
        currency.issue(1000, "test")
        
        v = currency.velocity(5000)
        assert v == 5.0  # 5000 / 1000
        
        efficiency = currency.velocity_efficiency(5000)
        assert efficiency["velocity_actual"] == 5.0
        assert efficiency["efficiency"] == 0.5  # 5/10

    def test_riba_validation(self):
        """Test de validation des règles du riba pour fulus"""
        currency = FulusCurrency("Test", "TST")
        
        # Surplus autorisé
        valid, msg = currency.riba_validation(100, 0.03, False)
        assert valid is True
        
        # Surplus excessif
        valid, msg = currency.riba_validation(100, 0.10, False)
        assert valid is False


# ============================================================
# Tests Grondona CRD
# ============================================================

class TestGrondonaCRD:
    def test_crd_creation(self):
        """Test de création du CRD"""
        commodities = [
            CommodityInBasket("Wheat", 180, 220, 200),
            CommodityInBasket("Copper", 8000, 12000, 9500)
        ]
        crd = GrondonaCRD(commodities, initial_currency_supply=10000)
        
        assert crd.currency_supply == 10000
        assert len(crd.commodities) == 2

    def test_crd_buy(self):
        """Test d'achat par le CRD (prix sous le plancher)"""
        commodities = [
            CommodityInBasket("Wheat", 180, 220, 200, stockpile=0)
        ]
        crd = GrondonaCRD(commodities, initial_currency_supply=10000)
        
        prices = {"Wheat": 170}  # Sous le plancher
        operations = crd.check_market_prices(prices)
        
        assert len(operations) == 1
        assert operations[0]["action"] == "BUY"
        assert operations[0]["commodity"] == "Wheat"
        assert operations[0]["quantity"] > 0
        assert crd.currency_supply > 10000

    def test_crd_sell(self):
        """Test de vente par le CRD (prix au-dessus du plafond)"""
        commodities = [
            CommodityInBasket("Wheat", 180, 220, 200, stockpile=1000)
        ]
        crd = GrondonaCRD(commodities, initial_currency_supply=10000)
        
        prices = {"Wheat": 240}  # Au-dessus du plafond
        operations = crd.check_market_prices(prices)
        
        assert len(operations) == 1
        assert operations[0]["action"] == "SELL"
        assert operations[0]["commodity"] == "Wheat"
        assert operations[0]["quantity"] > 0
        assert crd.currency_supply < 10000

    def test_crd_release_food(self):
        """Test de libération de stocks"""
        commodities = [
            CommodityInBasket("Wheat", 180, 220, 200, stockpile=1000)
        ]
        crd = GrondonaCRD(commodities)
        
        release = crd.release_food(100, "Wheat")
        assert release == 100
        assert crd.commodities["Wheat"].stockpile == 900


# ============================================================
# Tests BRI Network
# ============================================================

class TestBRINetwork:
    def test_bri_network_creation(self):
        """Test de création du réseau BRI"""
        network = BRINetwork()
        zone = ZoneBRI("TestZone", "TestCity", 1000, 0, 10.0)
        network.add_zone(zone)
        
        assert "TestZone" in network.zones
        assert network.zones["TestZone"].nuqud_reserve_grams == 1000

    def test_bri_transfer(self):
        """Test de transfert inter-zones"""
        network = BRINetwork()
        
        zone_a = ZoneBRI("ZoneA", "CityA", 2000)
        zone_b = ZoneBRI("ZoneB", "CityB", 500)
        network.add_zone(zone_a)
        network.add_zone(zone_b)
        
        bridge = LiquidityBridge("ZoneA", "ZoneB", min_transfer_nuqud=10)
        network.bridges.append(bridge)
        
        result = network.transfer("ZoneA", "ZoneB", 100)
        
        assert "error" not in result
        assert result["success"] is True
        assert result["gross"] == 100
        assert result["net"] < 100  # Avec frais


# ============================================================
# Tests Hisba
# ============================================================

class TestHisba:
    def test_market_inspection(self):
        """Test d'inspection du marché"""
        inspection = MarketInspection("Test Market")
        
        # Test de balance correcte
        result = inspection.check_scale(100, 99)
        assert result is True
        assert len(inspection.incidents) == 0
        
        # Test de balance frauduleuse
        result = inspection.check_scale(100, 85)
        assert result is False
        assert len(inspection.incidents) == 1
        assert inspection.incidents[0]["type"] == "scale_fraud"

    def test_halal_certification(self):
        """Test de certification halal"""
        inspection = MarketInspection("Test Market")
        
        # Certificat présent et valide
        result = inspection.verify_halal_certificate("Viande", True, True)
        assert result is True
        
        # Certificat manquant
        result = inspection.verify_halal_certificate("Viande", False, False)
        assert result is False
        assert len(inspection.incidents) == 1

    def test_muhtassib(self):
        """Test du muhtassib"""
        muhtassib = Muhtassib("Test", "Zone")
        inspection = MarketInspection("Test Market")
        
        inspection.check_scale(100, 85)
        report = muhtassib.inspect(inspection)
        
        assert report["total_incidents"] == 1
        assert muhtassib.reputation < 50


# ============================================================
# Tests Zakat
# ============================================================

class TestZakat:
    def test_zakat_calculation(self):
        """Test de calcul de Zakat"""
        holdings = [
            {"metal": "gold", "weight": 100},
            {"metal": "silver", "weight": 300}
        ]
        
        result = ZakatOnNuqud.calculate(
            nuqud_holdings=holdings,
            trade_profit_nuqud=500,
            agricultural_yield_nuqud=200,
            livestock_nuqud=100
        )
        
        assert result["total_zakat"] > 0
        assert result["gold_weight"] == 100
        assert result["silver_weight"] == 300

    def test_zakat_categories(self):
        """Test des catégories de Zakat"""
        categories = ZakatCategory.get_all()
        assert len(categories) == 8
        
        names = ZakatCategory.get_names()
        assert "fuqara" in names
        assert "masakin" in names


# ============================================================
# Tests Riba Rules
# ============================================================

class TestRibaRules:
    def test_riba_controller(self):
        """Test du contrôleur de riba"""
        controller = RibaController()
        
        # Nuqud : échange inégal
        valid, msg = controller.check_exchange(
            AssetClass.NUQUD,
            10.0, 12.0,  # Inégal
            True,  # Même espèce
            False  # Pas de délai
        )
        assert valid is False
        assert "riba_al_fadl" in msg
        
        # Nuqud : avec délai
        valid, msg = controller.check_exchange(
            AssetClass.NUQUD,
            10.0, 10.0,
            True,
            True  # Délai
        )
        assert valid is False
        assert "riba_al_nasia" in msg
        
        # Fulus : surplus modéré
        valid, msg = controller.check_exchange(
            AssetClass.FULUS,
            100.0, 103.0,  # 3% de surplus
            True,
            True  # Délai autorisé
        )
        assert valid is True

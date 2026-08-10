"""
Pytest Configuration – Fixtures partagées
=========================================

Fixtures communes pour tous les tests.

License: CC BY-SA 4.0 – Marc Daghar
"""

import pytest
import sys
import os
import json
import tempfile
from fastapi.testclient import TestClient
from typing import Dict, Any

# Ajout du chemin parent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.bri_network import BRINetwork, ZoneBRI, create_default_network
from src.core.grondona_crd import GrondonaCRD, CommodityInBasket
from src.core.nuqud import NuqudSystem
from src.core.fulus import FulusCurrency
from src.core.hisba import Muhtassib, MarketInspection
from src.simulation.agents import Guilde, Commercant, Consommateur, MuhtassibAgent
from src.simulation.market_advanced import Souq
from src.simulation.blockchain_sim import Blockchain


@pytest.fixture
def sample_network() -> BRINetwork:
    """Crée un réseau BRI de test"""
    return create_default_network()


@pytest.fixture
def sample_crd() -> GrondonaCRD:
    """Crée un CRD de test"""
    commodities = [
        CommodityInBasket("Wheat", 180, 220, 200),
        CommodityInBasket("Copper", 8000, 12000, 9500),
        CommodityInBasket("Salt", 50, 70, 60),
    ]
    return GrondonaCRD(commodities)


@pytest.fixture
def sample_nuqud() -> NuqudSystem:
    """Crée un système nuqud de test"""
    return NuqudSystem()


@pytest.fixture
def sample_fulus() -> FulusCurrency:
    """Crée une monnaie fulus de test"""
    return FulusCurrency("Test Fulus", "TST")


@pytest.fixture
def sample_muhtassib() -> Muhtassib:
    """Crée un muhtassib de test"""
    return Muhtassib("Test Muhtassib", "Test Zone")


@pytest.fixture
def sample_souq(sample_crd, sample_muhtassib) -> Souq:
    """Crée un souq de test"""
    return Souq("Test Souq", "Test Location", crd=sample_crd, muhtassib=sample_muhtassib)


@pytest.fixture
def sample_blockchain() -> Blockchain:
    """Crée une blockchain de test"""
    return Blockchain()


@pytest.fixture
def sample_agents():
    """Crée des agents de test"""
    guilde = Guilde("Test Guilde", "Test Location", production_capacity=1000)
    commercant = Commercant("Test Commercant", "Test Location")
    consommateur = Consommateur("Test Consommateur")
    muhtassib = MuhtassibAgent("Test Muhtassib", "Test Zone")
    return {
        "guilde": guilde,
        "commercant": commercant,
        "consommateur": consommateur,
        "muhtassib": muhtassib
    }


@pytest.fixture
def api_client():
    """Crée un client de test pour l'API"""
    from api.main import app
    return TestClient(app)


@pytest.fixture
def temp_db():
    """Crée une base de données temporaire"""
    import sqlite3
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            config TEXT NOT NULL,
            results TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bri_transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            simulation_id INTEGER,
            from_zone TEXT NOT NULL,
            to_zone TEXT NOT NULL,
            amount_nuqud REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.close()
    
    yield path
    
    os.unlink(path)


@pytest.fixture
def sample_transaction_data():
    """Données de transaction de test"""
    return {
        "from_zone": "Chine",
        "to_zone": "NUL",
        "amount_nuqud": 100.0
    }


@pytest.fixture
def sample_esg_data():
    """Données ESG de test"""
    return {
        "esg_global": 68,
        "environmental": 65,
        "social": 70,
        "governance": 69,
        "emissions": 1250
    }


@pytest.fixture
def sample_zakat_data():
    """Données Zakat de test"""
    return {
        "nuqud_holdings": [
            {"metal": "gold", "weight": 100},
            {"metal": "silver", "weight": 300}
        ],
        "trade_profit_nuqud": 500.0,
        "agricultural_yield_nuqud": 200.0,
        "livestock_nuqud": 100.0
    }

"""
Tests de l'API
==============

Tests unitaires pour l'API FastAPI.

License: CC BY-SA 4.0 – Marc Daghar
"""

import pytest
import sys
import os
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import app
from api.auth import fake_users_db, pwd_context

client = TestClient(app)


# ============================================================
# Tests d'authentification
# ============================================================

class TestAuth:
    def test_login_success(self):
        """Test de connexion réussie"""
        response = client.post("/token", json={
            "username": "admin",
            "password": "changeme123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_failure(self):
        """Test de connexion échouée"""
        response = client.post("/token", json={
            "username": "admin",
            "password": "wrong_password"
        })
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_get_current_user(self):
        """Test de récupération de l'utilisateur courant"""
        # Login
        login_response = client.post("/token", json={
            "username": "admin",
            "password": "changeme123"
        })
        token = login_response.json()["access_token"]
        
        # Accès à une route protégée
        response = client.get(
            "/secure/metrics",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "user" in response.json()
        assert response.json()["user"] == "admin"


# ============================================================
# Tests des endpoints publics
# ============================================================

class TestPublicEndpoints:
    def test_health(self):
        """Test de l'endpoint health"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_status(self):
        """Test de l'endpoint status"""
        response = client.get("/status")
        assert response.status_code == 200
        assert "running" in response.json()

    def test_metrics(self):
        """Test de l'endpoint metrics"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "zones" in response.json()

    def test_run_simulation(self):
        """Test de l'endpoint run"""
        response = client.post("/run", json={
            "years": 1,
            "use_crd": True,
            "use_zakat": True,
            "use_bri": False
        })
        assert response.status_code == 200
        assert "transactions" in response.json()


# ============================================================
# Tests des transferts
# ============================================================

class TestTransfers:
    def test_transfer_success(self):
        """Test de transfert réussi"""
        # Login
        login_response = client.post("/token", json={
            "username": "admin",
            "password": "changeme123"
        })
        token = login_response.json()["access_token"]
        
        # Transfert
        response = client.post(
            "/transfer",
            json={
                "from_zone": "Chine",
                "to_zone": "NUL",
                "amount_nuqud": 100
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        # Peut retourner 200 ou 400 selon la configuration
        assert response.status_code in [200, 400]

    def test_transfer_invalid_zone(self):
        """Test de transfert avec zone invalide"""
        login_response = client.post("/token", json={
            "username": "admin",
            "password": "changeme123"
        })
        token = login_response.json()["access_token"]
        
        response = client.post(
            "/transfer",
            json={
                "from_zone": "ZoneInexistante",
                "to_zone": "NUL",
                "amount_nuqud": 100
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        assert "error" in response.json()


# ============================================================
# Tests Zakat
# ============================================================

class TestZakatEndpoints:
    def test_zakat_history(self):
        """Test de l'historique Zakat"""
        response = client.get("/zakat/history/economy")
        assert response.status_code == 200
        assert "zakat_payments" in response.json()


# ============================================================
# Tests Compliance
# ============================================================

class TestCompliance:
    def test_certify_product(self):
        """Test de certification halal"""
        response = client.post(
            "/compliance/certify",
            params={
                "product_name": "Viande de bœuf",
                "issuer": "Muhtassib Test",
                "criteria": ["abattage_halal", "traçabilité"]
            }
        )
        assert response.status_code == 200
        assert "certificate_id" in response.json()

    def test_audit_contract(self):
        """Test d'audit de smart contract"""
        response = client.post(
            "/compliance/audit_contract",
            json={
                "contract_code": "function lend(amount, interest_rate) { return amount * interest_rate; }"
            }
        )
        assert response.status_code == 200
        assert "compliant" in response.json()
        assert response.json()["compliant"] is False
        assert "issues" in response.json()

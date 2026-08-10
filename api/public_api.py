"""
API Publique – Pour les partenaires BRI
=======================================

Endpoints accessibles aux partenaires BRI (Chine, Russie, Turquie, etc.)
Authentification par clé API.

License: CC BY-SA 4.0 – Marc Daghar
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import time
import secrets

from .auth import get_current_partner, verify_api_key

# ---- Configuration ----
app = FastAPI(
    title="Yusuf-Grondona Public API",
    description="API pour les partenaires BRI (Chine, Russie, Turquie, etc.)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Modèles ----
class ExchangeRateRequest(BaseModel):
    from_zone: str
    to_zone: str
    amount_fulus: float

class TransactionRecord(BaseModel):
    partner_id: str
    tx_type: str
    amount: float
    currency: str = "fulus"
    reference: Optional[str] = None

# ---- Endpoints publics ----
@app.get("/api/v1/health")
async def health_check():
    """Vérification de la disponibilité"""
    return {"status": "healthy", "timestamp": time.time(), "version": "1.0.0"}

@app.post("/api/v1/exchange_rate")
async def get_exchange_rate(req: ExchangeRateRequest, partner: Dict = Depends(get_current_partner)):
    """Taux de change entre zones BRI"""
    # Simulation des taux de change
    rates = {
        ("Chine", "France"): 1.15,
        ("France", "Chine"): 0.87,
        ("Russie", "France"): 1.08,
        ("France", "Russie"): 0.93,
        ("Turquie", "France"): 1.42,
        ("France", "Turquie"): 0.70,
        ("Chine", "Russie"): 1.05,
        ("Russie", "Chine"): 0.95,
        ("NUL", "France"): 1.25,
        ("France", "NUL"): 0.80,
    }

    rate = rates.get((req.from_zone, req.to_zone), 1.0)
    converted = req.amount_fulus * rate

    return {
        "from": req.from_zone,
        "to": req.to_zone,
        "amount": req.amount_fulus,
        "converted": converted,
        "rate": rate,
        "timestamp": time.time(),
        "partner": partner.get("username")
    }

@app.get("/api/v1/esg/{partner_id}")
async def get_esg_score(partner_id: str, year: int = 2026, partner: Dict = Depends(get_current_partner)):
    """Score ESG d'un partenaire BRI"""
    # Données simulées
    esg_data = {
        "Chine": {"environmental": 68, "social": 72, "governance": 65, "global": 68},
        "Russie": {"environmental": 62, "social": 58, "governance": 55, "global": 58},
        "Turquie": {"environmental": 55, "social": 60, "governance": 52, "global": 56},
        "France": {"environmental": 75, "social": 70, "governance": 72, "global": 72},
        "NUL": {"environmental": 45, "social": 40, "governance": 35, "global": 40},
    }

    if partner_id not in esg_data:
        raise HTTPException(status_code=404, detail="Partner not found")

    return {
        "partner": partner_id,
        "year": year,
        "esg": esg_data[partner_id],
        "last_update": time.time()
    }

@app.get("/api/v1/crd/prices")
async def get_crd_prices(partner: Dict = Depends(get_current_partner)):
    """Prix plancher/plafond Grondona"""
    return {
        "wheat": {"floor": 180, "ceiling": 220, "current": 195},
        "copper": {"floor": 8000, "ceiling": 12000, "current": 9500},
        "salt": {"floor": 50, "ceiling": 70, "current": 58},
        "rice": {"floor": 300, "ceiling": 400, "current": 350},
        "timestamp": time.time()
    }

@app.post("/api/v1/transactions/record")
async def record_transaction(tx: TransactionRecord, partner: Dict = Depends(get_current_partner)):
    """Enregistrement d'une transaction BRI"""
    # Génération d'un ID de transaction
    tx_id = f"BRI_{int(time.time())}_{partner.get('username', 'unknown')}"

    return {
        "status": "recorded",
        "tx_id": tx_id,
        "partner": partner.get("username"),
        "timestamp": time.time()
    }

@app.get("/api/v1/zakat/rate")
async def get_zakat_rate(partner: Dict = Depends(get_current_partner)):
    """Taux de Zakat en vigueur"""
    return {
        "zakat_rate": 0.025,
        "nisab_gold_grams": 85.0,
        "nisab_silver_grams": 595.0,
        "currency": "nuqud (or/argent)"
    }

# ---- Lancement ----
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

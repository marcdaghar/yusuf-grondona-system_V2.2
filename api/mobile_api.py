"""
API Mobile – Pour l'application muhtassib
=========================================

Endpoints pour l'application mobile React Native.

License: CC BY-SA 4.0 – Marc Daghar
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
import time
import uuid
import json
from datetime import datetime

from .auth import get_current_muhtassib

# ---- Configuration ----
app = FastAPI(
    title="Yusuf-Grondona Mobile API",
    description="API pour l'application mobile du muhtassib",
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
class Inspection(BaseModel):
    muhtassib_id: str
    merchant: str
    merchant_id: Optional[str] = None
    weight_kg: float
    halal_certified: bool = False
    halal_valid: bool = False
    price: Optional[float] = None
    product: Optional[str] = None
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class MerchantVerification(BaseModel):
    merchant_id: str
    merchant_name: str

# ---- Stockage temporaire ----
inspections_db: List[Dict] = []
merchants_db: Dict[str, Dict] = {}

# ---- Endpoints ----
@app.post("/api/mobile/inspect")
async def submit_inspection(inspection: Inspection, muhtassib: Dict = Depends(get_current_muhtassib)):
    """Soumet une inspection"""
    # Vérification que le muhtassib correspond
    if inspection.muhtassib_id != muhtassib.get("username"):
        # Dans une vraie API, on vérifierait par ID
        pass

    # Calcul de la conformité
    compliant = True
    issues = []

    if inspection.weight_kg <= 0:
        compliant = False
        issues.append("poids_invalide")

    if inspection.halal_certified and not inspection.halal_valid:
        compliant = False
        issues.append("certificat_halal_invalide")

    # Création de l'inspection
    inspection_record = {
        "id": str(uuid.uuid4()),
        "muhtassib_id": inspection.muhtassib_id,
        "merchant": inspection.merchant,
        "merchant_id": inspection.merchant_id,
        "weight_kg": inspection.weight_kg,
        "halal_certified": inspection.halal_certified,
        "halal_valid": inspection.halal_valid,
        "price": inspection.price,
        "product": inspection.product,
        "notes": inspection.notes,
        "latitude": inspection.latitude,
        "longitude": inspection.longitude,
        "compliant": compliant,
        "issues": issues,
        "timestamp": time.time(),
        "datetime": datetime.now().isoformat()
    }

    inspections_db.append(inspection_record)

    # Calcul du gain de réputation
    reputation_gain = 5 if compliant else -10

    return {
        "status": "recorded",
        "inspection_id": inspection_record["id"],
        "compliant": compliant,
        "issues": issues,
        "reputation_change": reputation_gain
    }

@app.get("/api/mobile/tasks")
async def get_tasks(muhtassib_id: Optional[str] = None, muhtassib: Dict = Depends(get_current_muhtassib)):
    """Liste des inspections à réaliser"""
    # Simulation de tâches
    tasks = [
        {
            "id": "task_001",
            "merchant": "Boulangerie des Oliviers",
            "scheduled_date": "2026-05-10",
            "priority": "high",
            "address": "123 Rue des Oliviers, Marseille",
            "notes": "Contrôle de poids et certificat halal"
        },
        {
            "id": "task_002",
            "merchant": "Épicerie Al-Nour",
            "scheduled_date": "2026-05-12",
            "priority": "medium",
            "address": "45 Rue de la Paix, Marseille",
            "notes": "Vérification des prix et de la fraîcheur"
        },
        {
            "id": "task_003",
            "merchant": "Boucherie Halal",
            "scheduled_date": "2026-05-15",
            "priority": "low",
            "address": "78 Rue du Port, Marseille",
            "notes": "Certificat halal et conditions de stockage"
        }
    ]

    return tasks

@app.get("/api/mobile/reputation/{muhtassib_id}")
async def get_reputation(muhtassib_id: str, muhtassib: Dict = Depends(get_current_muhtassib)):
    """Récupère la réputation d'un muhtassib"""
    # Simulation
    return {
        "muhtassib_id": muhtassib_id,
        "reputation": 125,
        "level": "Senior Muhtassib",
        "inspections": len(inspections_db),
        "compliance_rate": 0.92
    }

@app.get("/api/mobile/history")
async def get_inspection_history(muhtassib: Dict = Depends(get_current_muhtassib)):
    """Historique des inspections du muhtassib"""
    return {
        "total": len(inspections_db),
        "inspections": inspections_db[-20:]  # 20 dernières
    }

@app.post("/api/mobile/verify_merchant")
async def verify_merchant(merchant: MerchantVerification, muhtassib: Dict = Depends(get_current_muhtassib)):
    """Vérification d'un commerçant"""
    # Simulation
    if merchant.merchant_id not in merchants_db:
        merchants_db[merchant.merchant_id] = {
            "id": merchant.merchant_id,
            "name": merchant.merchant_name,
            "status": "approved",
            "verified_at": time.time()
        }

    return {
        "merchant_id": merchant.merchant_id,
        "status": merchants_db[merchant.merchant_id]["status"],
        "verified": True
    }

# ---- Lancement ----
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)

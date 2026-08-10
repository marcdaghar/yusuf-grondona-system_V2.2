"""
Certificate Monitor – Monitoring des certificats
================================================

Surveille les certificats des partenaires BRI et envoie des alertes
avant leur expiration.

License: CC BY-SA 4.0 – Marc Daghar
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
import time
import json
from datetime import datetime, timedelta

from .auth import get_current_admin

# ---- Configuration ----
app = FastAPI(
    title="Yusuf-Grondona Certificate Monitor",
    description="Monitoring des certificats BRI",
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
class CertificateData(BaseModel):
    partner_id: str
    partner_name: str
    level: str  # "gold", "silver", "bronze"
    expires_at: datetime
    issued_at: datetime

class CertificateRenewal(BaseModel):
    partner_id: str
    new_expiry: Optional[datetime] = None

# ---- Stockage ----
CERTIFICATES_DB: Dict[str, Dict] = {}

# Données initiales
CERTIFICATES_DB["china_bri"] = {
    "partner_name": "Chine",
    "level": "gold",
    "expires_at": datetime(2026, 12, 31),
    "issued_at": datetime(2026, 1, 1),
    "endpoints": ["exchange", "esg", "crd", "transactions"]
}

CERTIFICATES_DB["russia_bri"] = {
    "partner_name": "Russie",
    "level": "gold",
    "expires_at": datetime(2026, 10, 15),
    "issued_at": datetime(2026, 1, 15),
    "endpoints": ["exchange", "esg", "crd"]
}

CERTIFICATES_DB["turkey_bri"] = {
    "partner_name": "Turquie",
    "level": "silver",
    "expires_at": datetime(2026, 5, 20),
    "issued_at": datetime(2026, 2, 20),
    "endpoints": ["exchange", "esg"]
}

# ---- Endpoints ----
@app.get("/api/certificates")
async def get_all_certificates(admin: Dict = Depends(get_current_admin)):
    """Liste tous les certificats"""
    return {
        "total": len(CERTIFICATES_DB),
        "certificates": [
            {
                "partner_id": pid,
                **data
            }
            for pid, data in CERTIFICATES_DB.items()
        ]
    }

@app.get("/api/certificates/{partner_id}")
async def get_certificate(partner_id: str):
    """Récupère un certificat par ID"""
    if partner_id not in CERTIFICATES_DB:
        raise HTTPException(status_code=404, detail="Certificate not found")

    return {
        "partner_id": partner_id,
        **CERTIFICATES_DB[partner_id]
    }

@app.post("/api/certificates")
async def create_certificate(cert: CertificateData, admin: Dict = Depends(get_current_admin)):
    """Crée un nouveau certificat"""
    if cert.partner_id in CERTIFICATES_DB:
        raise HTTPException(status_code=409, detail="Certificate already exists")

    CERTIFICATES_DB[cert.partner_id] = {
        "partner_name": cert.partner_name,
        "level": cert.level,
        "expires_at": cert.expires_at,
        "issued_at": cert.issued_at,
        "endpoints": ["exchange", "esg", "crd", "transactions"]
    }

    return {
        "status": "created",
        "partner_id": cert.partner_id,
        "expires_at": cert.expires_at.isoformat()
    }

@app.put("/api/certificates/renew/{partner_id}")
async def renew_certificate(
    partner_id: str,
    renewal: CertificateRenewal,
    admin: Dict = Depends(get_current_admin)
):
    """Renouvelle un certificat"""
    if partner_id not in CERTIFICATES_DB:
        raise HTTPException(status_code=404, detail="Certificate not found")

    new_expiry = renewal.new_expiry or datetime.now() + timedelta(days=365)
    CERTIFICATES_DB[partner_id]["expires_at"] = new_expiry

    return {
        "status": "renewed",
        "partner_id": partner_id,
        "new_expiry": new_expiry.isoformat()
    }

@app.get("/api/certificates/monitor/expiring")
async def get_expiring_certificates(days_threshold: int = 30):
    """Liste les certificats qui expirent bientôt"""
    now = datetime.now()
    threshold = now + timedelta(days=days_threshold)

    expiring = []
    for pid, data in CERTIFICATES_DB.items():
        expires = data["expires_at"]
        days_left = (expires - now).days

        if expires < threshold:
            expiring.append({
                "partner_id": pid,
                "partner_name": data["partner_name"],
                "expires_at": expires.isoformat(),
                "days_left": days_left,
                "severity": "critical" if days_left <= 7 else "warning"
            })

    return {
        "total_expiring": len(expiring),
        "expiring": expiring
    }

@app.delete("/api/certificates/{partner_id}")
async def revoke_certificate(partner_id: str, admin: Dict = Depends(get_current_admin)):
    """Révoque un certificat"""
    if partner_id not in CERTIFICATES_DB:
        raise HTTPException(status_code=404, detail="Certificate not found")

    del CERTIFICATES_DB[partner_id]

    return {
        "status": "revoked",
        "partner_id": partner_id
    }

# ---- Fonctions internes ----
def send_expiry_alert(partner_id: str, days_left: int):
    """Envoie une alerte d'expiration (simulé)"""
    print(f"🔔 ALERTE: Le certificat de {partner_id} expire dans {days_left} jours")

# ---- Background task ----
async def check_expiring_certificates(background_tasks: BackgroundTasks):
    """Vérifie les certificats proches de l'expiration"""
    now = datetime.now()

    for pid, data in CERTIFICATES_DB.items():
        days_left = (data["expires_at"] - now).days

        if days_left <= 30:
            background_tasks.add_task(send_expiry_alert, pid, days_left)

@app.get("/api/certificates/monitor/check")
async def trigger_expiry_check(background_tasks: BackgroundTasks):
    """Déclenche une vérification des certificats"""
    await check_expiring_certificates(background_tasks)
    return {"status": "check_scheduled"}

# ---- Lancement ----
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)

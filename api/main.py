"""
API principale – Yusuf-Grondona BRI System
==========================================

Endpoints :
- /status : État du système
- /run : Lancement d'une simulation
- /transfer : Transfert inter-zones BRI
- /metrics : Métriques économiques globales
- /zakat/history/{payer} : Historique des paiements de Zakat
- /compliance/certify : Certification halal
- /compliance/audit_contract : Audit de smart contract

License: CC BY-SA 4.0 – Marc Daghar
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
import time
import json

# Import des modules internes
from src.core.bri_network import BRINetwork, ZoneBRI, create_default_network
from src.core.grondona_crd import GrondonaCRD, CommodityInBasket
from src.core.hisba import Muhtassib, MarketInspection
from src.core.zakat_nuqud import ZakatOnNuqud
from src.simulation.run_full import run_full_simulation, SimulationConfig
from src.simulation.blockchain_sim import Blockchain
from src.simulation.logistics_shocks import ShockManager, LogisticsShock
from src.simulation.crisis_scenarios import CrisisManager, CrisisScenario
from src.compliance.halal_certifier import HalalCompliance

from .auth import get_current_user, authenticate_user, create_access_token

# ---- Configuration de l'application ----
app = FastAPI(
    title="Yusuf-Grondona BRI API",
    description="""
    ## Système monétaire bimétallique avec logistique réelle

    - Nuqud (or/argent) comme réserve
    - Fulus comme monnaie de circulation
    - CRD (Grondona) pour stabiliser les prix
    - BRI Network pour transferts inter-zones
    - Zakat politique collectée par l'émir
    """,
    version="2.0.0",
    contact={
        "name": "Yusuf-Grondona Community",
        "url": "https://github.com/barberoussedine/yusuf-grondona-system",
    },
    license_info={
        "name": "CC BY-SA 4.0",
        "url": "https://creativecommons.org/licenses/by-sa/4.0/",
    },
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Modèles de données ----
class SimulationRunRequest(BaseModel):
    years: int = 1
    use_crd: bool = True
    use_zakat: bool = True
    use_bri: bool = True
    use_blockchain: bool = True
    use_shocks: bool = True
    use_climate: bool = False

class TransferRequest(BaseModel):
    from_zone: str
    to_zone: str
    amount_nuqud: float

class LoginRequest(BaseModel):
    username: str
    password: str

class CertifyRequest(BaseModel):
    product_name: str
    issuer: str
    criteria: List[str]

class AuditContractRequest(BaseModel):
    contract_code: str

# ---- État global ----
simulation_state = {
    "running": False,
    "network": None,
    "blockchain": None,
    "crd": None,
    "results": {},
    "last_run": None
}

# ---- Initialisation ----
def initialize_system():
    """Initialise le système par défaut"""
    # Réseau BRI
    network = create_default_network()
    simulation_state["network"] = network

    # Blockchain
    simulation_state["blockchain"] = Blockchain()

    # CRD
    commodities = [
        CommodityInBasket("Wheat", 180, 220, 200),
        CommodityInBasket("Copper", 8000, 12000, 9500),
        CommodityInBasket("Salt", 50, 70, 60),
        CommodityInBasket("Rice", 300, 400, 350)
    ]
    simulation_state["crd"] = GrondonaCRD(commodities)

initialize_system()

# ---- Health Check ----
@app.get("/health")
async def health_check():
    """Vérification de la santé du service"""
    return {"status": "healthy", "timestamp": time.time()}

# ---- Endpoints d'authentification ----
@app.post("/token")
async def login(req: LoginRequest):
    """Authentification et récupération d'un token JWT"""
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ---- Endpoints publics ----
@app.get("/status")
async def get_status():
    """État actuel de la simulation"""
    return {
        "running": simulation_state["running"],
        "current_year": simulation_state["results"].get("years", 0),
        "last_run": simulation_state["last_run"],
        "network_ready": simulation_state["network"] is not None
    }

@app.post("/run")
async def run_simulation(req: SimulationRunRequest, background_tasks: BackgroundTasks):
    """Exécute une simulation sur N années"""
    if simulation_state["running"]:
        raise HTTPException(status_code=409, detail="Simulation déjà en cours")

    simulation_state["running"] = True

    try:
        config = SimulationConfig(
            years=req.years,
            use_crd=req.use_crd,
            use_zakat=req.use_zakat,
            use_bri=req.use_bri,
            use_blockchain=req.use_blockchain,
            use_shocks=req.use_shocks,
            use_climate=req.use_climate
        )

        results = run_full_simulation(config)
        simulation_state["results"] = results
        simulation_state["last_run"] = time.time()

        # Ajout des métriques BRI
        network = simulation_state["network"]
        if network and req.use_bri:
            results["bri_summary"] = network.global_summary()

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        simulation_state["running"] = False

@app.post("/transfer")
async def transfer_nuqud(req: TransferRequest):
    """Effectue un transfert inter-zone via le réseau BRI"""
    network = simulation_state["network"]
    if not network:
        raise HTTPException(status_code=500, detail="Réseau BRI non initialisé")

    result = network.transfer(req.from_zone, req.to_zone, req.amount_nuqud)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

@app.get("/metrics")
async def get_metrics():
    """Retourne les indicateurs économiques globaux"""
    network = simulation_state["network"]
    crd = simulation_state["crd"]

    if not network:
        raise HTTPException(status_code=500, detail="Réseau BRI non initialisé")

    summary = network.global_summary()

    # Calcul des métriques globales
    total_reserves = sum(z["nuqud_reserve_grams"] for z in summary.values())
    total_fulus = sum(z["fulus_supply"] for z in summary.values())

    response = {
        "global_reserves_nuqud_g": total_reserves,
        "global_fulus_supply": total_fulus,
        "zones": summary,
        "timestamp": time.time()
    }

    if crd:
        response["crd_status"] = crd.get_status()

    return response

@app.get("/zakat/history/{payer}")
async def get_zakat_history(payer: str):
    """Historique des paiements de Zakat"""
    blockchain = simulation_state["blockchain"]
    if not blockchain:
        return {"error": "Blockchain non initialisée"}

    history = blockchain.get_zakat_history(payer)
    return {"payer": payer, "zakat_payments": history}

# ---- Endpoints de conformité ----
@app.post("/compliance/certify")
async def certify_product(req: CertifyRequest):
    """Certification halal d'un produit"""
    halal = HalalCompliance()
    cert = halal.certify_product(req.product_name, req.issuer, req.criteria)
    return {
        "certificate_id": cert.id,
        "product_name": cert.product_name,
        "issuer": cert.issuer,
        "valid_until": cert.expiry_date.isoformat(),
        "criteria": cert.criteria
    }

@app.post("/compliance/audit_contract")
async def audit_contract(req: AuditContractRequest):
    """Audit d'un smart contract pour détection de violations usuraires"""
    halal = HalalCompliance()
    result = halal.audit_smart_contract(req.contract_code)
    return result

# ---- Endpoint admin ----
@app.post("/admin/reset")
async def reset_system():
    """Réinitialise le système (admin uniquement)"""
    initialize_system()
    return {"status": "reset", "message": "Système réinitialisé"}

# ---- Lancement ----
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

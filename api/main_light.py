"""
API allégée – Version sans dépendances lourdes
=============================================

Cette version ne nécessite pas :
- Machine Learning (scikit-learn, tensorflow, stable-baselines3)
- Blockchain (web3)
- IoT (paho-mqtt)

Pour un déploiement rapide ou sur des ressources limitées.

License: CC BY-SA 4.0 – Marc Daghar
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
import time

# Import des modules légers
from src.core.bri_network import BRINetwork, ZoneBRI, create_default_network
from src.core.grondona_crd import GrondonaCRD, CommodityInBasket
from src.core.zakat_nuqud import ZakatOnNuqud
from src.simulation.agents import Guilde, Commercant, Consommateur, MuhtassibAgent
from src.simulation.market_advanced import Souq

# ---- Configuration ----
app = FastAPI(
    title="Yusuf-Grondona BRI API (Light)",
    description="Version allégée – sans ML, sans blockchain, sans IoT",
    version="1.0-light"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Modèles ----
class TransferRequest(BaseModel):
    from_zone: str
    to_zone: str
    amount_nuqud: float

class SimulationRunRequest(BaseModel):
    years: int = 1
    use_crd: bool = True
    use_zakat: bool = True
    use_bri: bool = True

# ---- État global ----
simulation_state = {
    "running": False,
    "network": None,
    "crd": None,
    "results": {}
}

# ---- Initialisation ----
def initialize():
    net = create_default_network()
    simulation_state["network"] = net

    commodities = [
        CommodityInBasket("Wheat", 180, 220, 200),
        CommodityInBasket("Copper", 8000, 12000, 9500)
    ]
    simulation_state["crd"] = GrondonaCRD(commodities)

initialize()

# ---- Endpoints ----
@app.get("/status")
async def status():
    return {"running": simulation_state["running"], "ready": True}

@app.get("/metrics")
async def metrics():
    net = simulation_state["network"]
    if not net:
        raise HTTPException(status_code=500, detail="Réseau BRI non initialisé")
    return net.global_summary()

@app.post("/run")
async def run_simulation(req: SimulationRunRequest):
    if simulation_state["running"]:
        raise HTTPException(status_code=409, detail="Simulation déjà en cours")

    simulation_state["running"] = True
    simulation_state["results"] = {
        "years": req.years,
        "message": f"Simulation allégée de {req.years} an(s)",
        "timestamp": time.time()
    }
    simulation_state["running"] = False
    return simulation_state["results"]

@app.post("/transfer")
async def transfer_nuqud(req: TransferRequest):
    net = simulation_state["network"]
    result = net.transfer(req.from_zone, req.to_zone, req.amount_nuqud)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/zakat")
async def calculate_zakat():
    """Calcul simple de Zakat sur un montant donné"""
    return {
        "zakat_rate": 0.025,
        "example": "100g d'or → 2.5g de Zakat"
    }

# ---- Lancement ----
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

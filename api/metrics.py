"""
Métriques Prometheus
====================

Endpoint /metrics pour Prometheus.

License: CC BY-SA 4.0 – Marc Daghar
"""

from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import time
import uvicorn

app = FastAPI(title="Yusuf-Grondona Metrics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Métriques ----
# Gauges (valeurs courantes)
nuqud_reserve_gauge = Gauge('yusuf_nuqud_reserve_grams', 'Réserve nuqud en grammes', ['zone'])
fulus_supply_gauge = Gauge('yusuf_fulus_supply', 'Masse fulus en circulation', ['zone'])
esg_gauge = Gauge('yusuf_esg_global', 'Score ESG global')
logistics_entropy_gauge = Gauge('yusuf_logistics_entropy', 'Entropie logistique')
exchange_rate_gauge = Gauge('yusuf_exchange_rate', 'Taux de change fulus/nuqud', ['zone'])

# Counters (cumulatifs)
transaction_counter = Counter('yusuf_transactions_total', 'Total des transactions')
zakat_counter = Counter('yusuf_zakat_collected_total', 'Zakat totale collectée')
bri_transfer_counter = Counter('yusuf_bri_transfers_total', 'Transferts BRI totaux', ['from_zone', 'to_zone'])

# Histograms (distribution)
transaction_duration = Histogram('yusuf_transaction_duration_seconds', 'Durée des transactions', buckets=[0.1, 0.5, 1, 2, 5, 10])

# ---- Endpoint ----
@app.get("/metrics")
async def get_metrics():
    """Endpoint Prometheus"""
    # Mise à jour des métriques (à appeler périodiquement)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ---- Fonctions d'update ----
def update_metrics_from_system(network, crd, results):
    """Met à jour les métriques à partir de l'état du système"""
    if network:
        summary = network.global_summary()
        for zone, data in summary.items():
            nuqud_reserve_gauge.labels(zone=zone).set(data.get('nuqud_reserve_grams', 0))
            fulus_supply_gauge.labels(zone=zone).set(data.get('fulus_supply', 0))
            exchange_rate_gauge.labels(zone=zone).set(data.get('exchange_rate', 1.0))

    if results:
        # ESG (simulé)
        esg_value = 65 + (time.time() % 10)  # Simulation
        esg_gauge.set(esg_value)

        # Entropie logistique
        entropy = 0.5 + (time.time() % 5) / 10
        logistics_entropy_gauge.set(entropy)

        # Transactions
        n_transactions = len(results.get('transactions', []))
        transaction_counter.inc(n_transactions)

        # Zakat
        zakat = results.get('zakat_collected', 0)
        zakat_counter.inc(zakat)

        # Transferts BRI
        for tx in results.get('bri_transfers', []):
            bri_transfer_counter.labels(
                from_zone=tx.get('from', 'unknown'),
                to_zone=tx.get('to', 'unknown')
            ).inc()

# ---- Lancement ----
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

"""
Webhooks – Notifications pour partenaires BRI
=============================================

Gestion des webhooks pour les partenaires BRI.
Notification en temps réel des événements.

License: CC BY-SA 4.0 – Marc Daghar
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Optional, Any
import uvicorn
import time
import json
import hashlib
import hmac
import httpx
import asyncio

from .auth import get_current_partner

# ---- Configuration ----
app = FastAPI(
    title="Yusuf-Grondona Webhook Gateway",
    description="Webhooks pour partenaires BRI",
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
class WebhookSubscription(BaseModel):
    partner_id: str
    url: HttpUrl
    events: List[str]  # ["exchange_rate_change", "esg_update", "crd_price_change", "audit_alert"]
    secret: str

class WebhookPayload(BaseModel):
    event_type: str
    timestamp: float
    data: Dict[str, Any]

# ---- Stockage ----
subscriptions: Dict[str, List[WebhookSubscription]] = {}

# ---- Endpoints ----
@app.post("/api/webhooks/subscribe")
async def subscribe_webhook(subscription: WebhookSubscription, partner: Dict = Depends(get_current_partner)):
    """Un partenaire BRI s'abonne à des notifications"""
    if subscription.partner_id != partner.get("username"):
        raise HTTPException(status_code=403, detail="Partner ID mismatch")

    if subscription.partner_id not in subscriptions:
        subscriptions[subscription.partner_id] = []

    subscriptions[subscription.partner_id].append(subscription)

    return {
        "status": "subscribed",
        "partner": subscription.partner_id,
        "events": subscription.events,
        "url": str(subscription.url)
    }

@app.delete("/api/webhooks/unsubscribe")
async def unsubscribe_webhook(
    partner_id: str,
    url: HttpUrl,
    partner: Dict = Depends(get_current_partner)
):
    """Se désabonner"""
    if partner_id != partner.get("username"):
        raise HTTPException(status_code=403, detail="Partner ID mismatch")

    if partner_id in subscriptions:
        subscriptions[partner_id] = [
            s for s in subscriptions[partner_id] if str(s.url) != str(url)
        ]

    return {"status": "unsubscribed", "partner": partner_id}

@app.get("/api/webhooks/subscriptions")
async def get_subscriptions(partner: Dict = Depends(get_current_partner)):
    """Liste des abonnements d'un partenaire"""
    partner_id = partner.get("username")
    subs = subscriptions.get(partner_id, [])

    return {
        "partner": partner_id,
        "subscriptions": [
            {
                "url": str(s.url),
                "events": s.events
            }
            for s in subs
        ]
    }

# ---- Fonctions internes ----
async def send_webhook(subscription: WebhookSubscription, payload: WebhookPayload) -> bool:
    """Envoie une notification à un webhook avec signature HMAC"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        payload_dict = payload.dict()

        # Signature HMAC-SHA256
        signature = hmac.new(
            subscription.secret.encode(),
            json.dumps(payload_dict, sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Partner-Id": subscription.partner_id,
            "X-Event-Type": payload.event_type
        }

        try:
            response = await client.post(str(subscription.url), json=payload_dict, headers=headers)
            return response.status_code == 200
        except:
            return False

async def broadcast_event(event_type: str, data: Dict[str, Any], target_partners: Optional[List[str]] = None):
    """Diffuse un événement à tous les partenaires concernés"""
    tasks = []

    for partner_id, subs in subscriptions.items():
        if target_partners and partner_id not in target_partners:
            continue

        for sub in subs:
            if event_type in sub.events:
                payload = WebhookPayload(
                    event_type=event_type,
                    timestamp=time.time(),
                    data=data
                )
                tasks.append(send_webhook(sub, payload))

    if tasks:
        results = await asyncio.gather(*tasks)
        return {
            "event": event_type,
            "sent": len(tasks),
            "success": sum(1 for r in results if r)
        }

    return {"event": event_type, "sent": 0, "success": 0}

# ---- Endpoint de test ----
@app.post("/api/webhooks/test")
async def test_webhook(event_type: str, data: Dict, partners: Optional[List[str]] = None):
    """Déclenche un webhook de test"""
    result = await broadcast_event(event_type, data, partners)
    return result

# ---- Lancement ----
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

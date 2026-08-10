"""
WebSocket Manager – Communication temps réel
============================================

Gestion des connexions WebSocket pour le temps réel.

License: CC BY-SA 4.0 – Marc Daghar
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Set, Any
import json
import uvicorn
import time

from .auth import get_current_user

# ---- Configuration ----
app = FastAPI(
    title="Yusuf-Grondona WebSocket",
    description="WebSocket pour temps réel",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Manager ----
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.channels: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, channel: str = "broadcast"):
        await websocket.accept()
        self.active_connections[client_id] = websocket

        if channel not in self.channels:
            self.channels[channel] = set()
        self.channels[channel].add(client_id)

    def disconnect(self, client_id: str, channel: str = "broadcast"):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        if channel in self.channels:
            self.channels[channel].discard(client_id)

    async def send_personal(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except:
                pass

    async def broadcast(self, message: dict, channel: str = "broadcast"):
        if channel not in self.channels:
            return

        for client_id in self.channels[channel]:
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_text(json.dumps(message))
                except:
                    pass

    async def broadcast_except(self, message: dict, exclude: str, channel: str = "broadcast"):
        if channel not in self.channels:
            return

        for client_id in self.channels[channel]:
            if client_id != exclude and client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_text(json.dumps(message))
                except:
                    pass

manager = ConnectionManager()

# ---- WebSocket endpoint ----
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    channel = "broadcast"

    try:
        await manager.connect(websocket, client_id, channel)

        # Envoyer un message de bienvenue
        await manager.send_personal(client_id, {
            "type": "welcome",
            "client_id": client_id,
            "connected_at": time.time()
        })

        # Annoncer la connexion
        await manager.broadcast_except({
            "type": "connection",
            "client_id": client_id,
            "status": "connected"
        }, client_id, channel)

        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                msg_type = message.get("type", "unknown")

                # Traitement des messages
                if msg_type == "ping":
                    await manager.send_personal(client_id, {
                        "type": "pong",
                        "timestamp": time.time()
                    })

                elif msg_type == "get_metrics":
                    # Simulation de métriques
                    await manager.send_personal(client_id, {
                        "type": "metrics",
                        "data": {
                            "esg_global": 65 + (time.time() % 10),
                            "transactions": 100,
                            "timestamp": time.time()
                        }
                    })

                elif msg_type == "transfer":
                    # format: {"type": "transfer", "from": "Chine", "to": "NUL", "amount": 100}
                    from_zone = message.get("from")
                    to_zone = message.get("to")
                    amount = message.get("amount", 0)

                    # Simulation de transfert
                    result = {
                        "success": True,
                        "from": from_zone,
                        "to": to_zone,
                        "amount": amount,
                        "net": amount * 0.99,
                        "fee": amount * 0.01
                    }

                    # Réponse au client
                    await manager.send_personal(client_id, {
                        "type": "transfer_result",
                        "data": result
                    })

                    # Broadcast aux autres
                    await manager.broadcast({
                        "type": "transfer",
                        "from": from_zone,
                        "to": to_zone,
                        "amount": amount
                    }, channel)

                elif msg_type == "subscribe":
                    new_channel = message.get("channel")
                    if new_channel:
                        # Changement de canal
                        old_channel = channel

                        # Retirer de l'ancien canal
                        if old_channel in manager.channels:
                            manager.channels[old_channel].discard(client_id)

                        # Ajouter au nouveau
                        channel = new_channel
                        if channel not in manager.channels:
                            manager.channels[channel] = set()
                        manager.channels[channel].add(client_id)

                        await manager.send_personal(client_id, {
                            "type": "subscribed",
                            "channel": channel
                        })

            except json.JSONDecodeError:
                await manager.send_personal(client_id, {
                    "type": "error",
                    "message": "Invalid JSON"
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id, channel)

        # Annoncer la déconnexion
        await manager.broadcast_except({
            "type": "disconnect",
            "client_id": client_id,
            "status": "disconnected"
        }, client_id, channel)

# ---- Lancement ----
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)

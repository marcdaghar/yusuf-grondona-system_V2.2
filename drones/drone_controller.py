"""
Drone Controller – Surveillance des corridors BRI
==================================================

Gestion des drones pour la surveillance des corridors BRI :
- Suivi des expéditions
- Détection des anomalies (vol, perte)
- Communication WebSocket temps réel
- Cartographie interactive

License: CC BY-SA 4.0 – Marc Daghar
"""

import json
import time
import random
import asyncio
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    import websockets
except ImportError:
    print("⚠️  websockets non installé. Installez: pip install websockets")
    websockets = None

try:
    import folium
    from streamlit_folium import folium_static
except ImportError:
    print("⚠️  folium/streamlit_folium non installé pour la cartographie")
    folium = None


class DroneStatus(Enum):
    """Statut d'un drone"""
    IDLE = "idle"
    FLYING = "flying"
    TRACKING = "tracking"
    RETURNING = "returning"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"
    ALERT = "alert"


@dataclass
class Drone:
    """
    Représentation d'un drone de surveillance
    """
    id: str
    lat: float
    lon: float
    altitude: float = 100.0
    battery: float = 100.0
    status: DroneStatus = DroneStatus.IDLE
    mission: str = "surveillance"
    current_shipment: Optional[str] = None
    speed_kmh: float = 50.0
    last_update: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        """Convertit en dictionnaire"""
        return {
            "id": self.id,
            "lat": self.lat,
            "lon": self.lon,
            "altitude": self.altitude,
            "battery": self.battery,
            "status": self.status.value,
            "mission": self.mission,
            "current_shipment": self.current_shipment,
            "speed_kmh": self.speed_kmh,
            "last_update": self.last_update
        }

    def update_position(self, lat: float, lon: float, altitude: Optional[float] = None):
        """Met à jour la position du drone"""
        self.lat = lat
        self.lon = lon
        if altitude is not None:
            self.altitude = altitude
        self.last_update = time.time()

    def consume_battery(self, amount: float = 0.5):
        """Consomme de la batterie"""
        self.battery = max(0, self.battery - amount)
        if self.battery < 20:
            self.status = DroneStatus.RETURNING

    def charge_battery(self):
        """Recharge la batterie"""
        self.battery = min(100, self.battery + 10)
        if self.battery > 80:
            self.status = DroneStatus.IDLE


class DroneFleetManager:
    """
    Gestionnaire de flotte de drones
    """

    def __init__(self):
        self.drones: Dict[str, Drone] = {}
        self.shipments: Dict[str, Dict] = {}
        self.anomalies: List[Dict] = []

        # Corridors BRI (points clés)
        self.corridor_points = self._define_corridors()

        self.history: List[Dict] = []

    def _define_corridors(self) -> Dict[str, List[Tuple[float, float]]]:
        """Définit les corridors BRI"""
        return {
            "maritime": [
                (31.2, 121.5),  # Shanghai
                (18.9, 72.8),   # Mumbai
                (12.9, 50.9),   # Djibouti
                (29.9, 32.5),   # Port Saïd
                (43.3, 5.4),    # Marseille
            ],
            "ferroviaire": [
                (39.9, 116.4),  # Pékin
                (50.1, 80.2),   # Kazakhstan
                (55.8, 37.6),   # Moscou
                (52.5, 13.4),   # Berlin
                (48.9, 2.3),    # Paris
            ],
            "mediterraneen": [
                (43.3, 5.4),    # Marseille
                (41.9, 12.5),   # Rome
                (40.4, 3.7),    # Madrid
                (38.7, 9.2),    # Lisbonne
                (33.9, 35.5),   # Beyrouth
            ]
        }

    def add_drone(
        self,
        drone_id: str,
        lat: float,
        lon: float,
        mission: str = "surveillance"
    ) -> Drone:
        """Ajoute un drone à la flotte"""
        drone = Drone(
            id=drone_id,
            lat=lat,
            lon=lon,
            mission=mission
        )
        self.drones[drone_id] = drone
        return drone

    def remove_drone(self, drone_id: str) -> bool:
        """Retire un drone de la flotte"""
        if drone_id in self.drones:
            del self.drones[drone_id]
            return True
        return False

    def update_drone_position(self, drone_id: str, lat: float, lon: float) -> bool:
        """Met à jour la position d'un drone"""
        if drone_id in self.drones:
            self.drones[drone_id].update_position(lat, lon)
            self.drones[drone_id].consume_battery(0.3)
            return True
        return False

    def assign_shipment(self, drone_id: str, shipment_id: str) -> bool:
        """Affecte un drone à une expédition"""
        if drone_id in self.drones:
            drone = self.drones[drone_id]
            if drone.status not in [DroneStatus.IDLE, DroneStatus.CHARGING]:
                return False

            drone.status = DroneStatus.TRACKING
            drone.current_shipment = shipment_id
            self.shipments[shipment_id] = {
                "drone_id": drone_id,
                "started_at": time.time(),
                "status": "tracking"
            }
            return True
        return False

    def release_shipment(self, drone_id: str) -> bool:
        """Libère un drone d'une expédition"""
        if drone_id in self.drones:
            drone = self.drones[drone_id]
            if drone.current_shipment:
                drone.status = DroneStatus.IDLE
                drone.current_shipment = None
                return True
        return False

    def detect_anomaly(
        self,
        drone_id: str,
        expected_weight: float,
        detected_weight: float,
        tolerance: float = 0.1
    ) -> Optional[Dict]:
        """
        Détecte une anomalie (vol, rupture de chaîne logistique)

        Args:
            drone_id: ID du drone
            expected_weight: Poids attendu
            detected_weight: Poids détecté
            tolerance: Tolérance (10% par défaut)

        Returns:
            Dict: Description de l'anomalie ou None
        """
        if drone_id not in self.drones:
            return None

        drone = self.drones[drone_id]

        if abs(expected_weight - detected_weight) / expected_weight > tolerance:
            anomaly = {
                "drone_id": drone_id,
                "shipment": drone.current_shipment,
                "anomaly_type": "weight_mismatch",
                "expected_weight": expected_weight,
                "detected_weight": detected_weight,
                "severity": "critical" if abs(expected_weight - detected_weight) / expected_weight > 0.3 else "warning",
                "timestamp": time.time()
            }
            self.anomalies.append(anomaly)
            drone.status = DroneStatus.ALERT
            return anomaly

        return None

    def get_drone_status(self, drone_id: str) -> Optional[Dict]:
        """Récupère le statut d'un drone"""
        if drone_id in self.drones:
            return self.drones[drone_id].to_dict()
        return None

    def get_fleet_status(self) -> Dict:
        """Récupère le statut de toute la flotte"""
        return {
            "total": len(self.drones),
            "active": sum(1 for d in self.drones.values() if d.status in [DroneStatus.FLYING, DroneStatus.TRACKING]),
            "idle": sum(1 for d in self.drones.values() if d.status == DroneStatus.IDLE),
            "alert": sum(1 for d in self.drones.values() if d.status == DroneStatus.ALERT),
            "drones": [d.to_dict() for d in self.drones.values()]
        }

    def get_anomalies(self, limit: int = 10) -> List[Dict]:
        """Récupère les anomalies récentes"""
        return self.anomalies[-limit:]

    def get_corridor_map(self) -> Any:
        """Génère une carte Folium des corridors"""
        if folium is None:
            return None

        m = folium.Map(location=[45, 60], zoom_start=3)

        # Ajout des corridors
        for corridor_name, points in self.corridor_points.items():
            folium.PolyLine(
                points,
                color="blue" if corridor_name == "maritime" else "green" if corridor_name == "ferroviaire" else "orange",
                weight=3,
                opacity=0.7,
                popup=corridor_name
            ).add_to(m)

        # Ajout des drones
        for drone in self.drones.values():
            color = "green" if drone.battery > 50 else "orange" if drone.battery > 20 else "red"
            folium.Marker(
                [drone.lat, drone.lon],
                popup=f"{drone.id}<br>Mission: {drone.mission}<br>Batterie: {drone.battery:.0f}%<br>Statut: {drone.status.value}",
                icon=folium.Icon(color=color, icon="drone")
            ).add_to(m)

        return m


class DroneWebSocketServer:
    """
    Serveur WebSocket pour communication temps réel avec les drones
    """

    def __init__(self, fleet_manager: DroneFleetManager, host: str = "0.0.0.0", port: int = 8765):
        if websockets is None:
            raise ImportError("websockets est requis. Installez: pip install websockets")

        self.fleet = fleet_manager
        self.host = host
        self.port = port
        self.clients = set()
        self.running = False

    async def register(self, websocket):
        """Enregistre un client"""
        self.clients.add(websocket)
        try:
            async for message in websocket:
                await self.process_command(message, websocket)
        finally:
            self.clients.remove(websocket)

    async def process_command(self, message: str, websocket):
        """Traite une commande reçue"""
        try:
            data = json.loads(message)
            command = data.get("command")

            if command == "update_position":
                drone_id = data.get("drone_id")
                lat = data.get("lat")
                lon = data.get("lon")
                if drone_id and lat is not None and lon is not None:
                    self.fleet.update_drone_position(drone_id, lat, lon)
                    await self.broadcast_fleet_status()

            elif command == "get_status":
                await websocket.send(json.dumps({
                    "type": "fleet_status",
                    "data": self.fleet.get_fleet_status()
                }))

            elif command == "get_corridor":
                await websocket.send(json.dumps({
                    "type": "corridor_data",
                    "data": self.fleet.corridor_points
                }))

            elif command == "anomaly_report":
                drone_id = data.get("drone_id")
                expected = data.get("expected_weight")
                detected = data.get("detected_weight")
                if drone_id and expected and detected:
                    anomaly = self.fleet.detect_anomaly(drone_id, expected, detected)
                    if anomaly:
                        await self.broadcast_anomaly(anomaly)

            elif command == "ping":
                await websocket.send(json.dumps({"type": "pong", "timestamp": time.time()}))

        except json.JSONDecodeError:
            await websocket.send(json.dumps({"type": "error", "message": "Invalid JSON"}))

    async def broadcast_fleet_status(self):
        """Diffuse le statut de la flotte à tous les clients"""
        if not self.clients:
            return

        message = json.dumps({
            "type": "fleet_status",
            "data": self.fleet.get_fleet_status()
        })

        await asyncio.gather(*[client.send(message) for client in self.clients])

    async def broadcast_anomaly(self, anomaly: Dict):
        """Diffuse une anomalie à tous les clients"""
        if not self.clients:
            return

        message = json.dumps({
            "type": "anomaly_alert",
            "data": anomaly
        })

        await asyncio.gather(*[client.send(message) for client in self.clients])

    async def start(self):
        """Démarre le serveur WebSocket"""
        self.running = True
        async with websockets.serve(self.register, self.host, self.port):
            print(f"🚁 Serveur WebSocket démarré sur ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

    def run(self):
        """Exécute le serveur dans un thread séparé"""
        asyncio.run(self.start())


# ---- Fonction de démonstration ----
def demo_drone_controller():
    """Démonstration du contrôleur de drones"""
    print("=== CONTRÔLEUR DE DRONES ===\n")

    # Création de la flotte
    fleet = DroneFleetManager()

    # Ajout de drones
    fleet.add_drone("DR-001", 31.2, 121.5, "maritime")  # Shanghai
    fleet.add_drone("DR-002", 55.8, 37.6, "ferroviaire")  # Moscou
    fleet.add_drone("DR-003", 29.9, 32.5, "maritime")  # Port Saïd
    fleet.add_drone("DR-004", 43.3, 5.4, "maritime")  # Marseille

    print(f"Flotte: {len(fleet.drones)} drones")

    # Simulation de mouvement
    for drone in fleet.drones.values():
        drone.update_position(
            drone.lat + random.uniform(-0.5, 0.5),
            drone.lon + random.uniform(-0.5, 0.5)
        )

    # Statut de la flotte
    status = fleet.get_fleet_status()
    print(f"\nStatut: {status['active']} actifs, {status['idle']} en attente")

    # Détection d'anomalie
    anomaly = fleet.detect_anomaly("DR-001", 1000, 650)
    if anomaly:
        print(f"\n🚨 Anomalie détectée: {anomaly['anomaly_type']}")

    # Liste des anomalies
    print(f"\nAnomalies: {len(fleet.get_anomalies())}")

    # Carte (si disponible)
    if folium:
        print("\n🗺️ Carte générée (disponible dans le dashboard)")


if __name__ == "__main__":
    demo_drone_controller()

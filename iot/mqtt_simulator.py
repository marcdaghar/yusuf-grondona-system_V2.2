"""
MQTT Simulator – Simulation de capteurs IoT
===========================================

Simule des capteurs dans plusieurs entrepôts et envoie les données
via MQTT vers un broker (test.mosquitto.org par défaut).

License: CC BY-SA 4.0 – Marc Daghar
"""

import json
import time
import random
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("⚠️  paho-mqtt non installé. Installez: pip install paho-mqtt")
    mqtt = None


@dataclass
class WarehouseData:
    """Données d'un capteur d'entrepôt"""
    warehouse_id: str
    temperature_celsius: float
    humidity_percent: float
    stock_quantity_tons: float
    co2_ppm: float
    timestamp: float = field(default_factory=time.time)

    def to_json(self) -> str:
        """Convertit en JSON"""
        return json.dumps({
            "warehouse_id": self.warehouse_id,
            "timestamp": self.timestamp,
            "temperature_celsius": self.temperature_celsius,
            "humidity_percent": self.humidity_percent,
            "stock_quantity_tons": self.stock_quantity_tons,
            "co2_ppm": self.co2_ppm
        })


class WarehouseMQTTSimulator:
    """
    Simulateur de capteurs IoT pour entrepôts

    Args:
        broker: Adresse du broker MQTT
        port: Port du broker MQTT
        topic_prefix: Préfixe du topic
        interval: Intervalle entre les envois (secondes)
    """

    def __init__(
        self,
        broker: str = "test.mosquitto.org",
        port: int = 1883,
        topic_prefix: str = "yusuf/warehouse",
        interval: int = 10
    ):
        if mqtt is None:
            raise ImportError("paho-mqtt est requis. Installez: pip install paho-mqtt")

        self.broker = broker
        self.port = port
        self.topic_prefix = topic_prefix
        self.interval = interval
        self.client = None
        self.running = False
        self.warehouses: List[str] = []
        self.last_data: Dict[str, WarehouseData] = {}

    def connect(self) -> bool:
        """Se connecte au broker MQTT"""
        try:
            self.client = mqtt.Client()
            self.client.connect(self.broker, self.port, 60)
            print(f"✅ Connecté à MQTT: {self.broker}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion MQTT: {e}")
            return False

    def publish_data(self, warehouse_id: str, data: WarehouseData) -> bool:
        """Publie les données d'un entrepôt"""
        if not self.client:
            return False

        topic = f"{self.topic_prefix}/{warehouse_id}"
        try:
            result = self.client.publish(topic, data.to_json())
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.last_data[warehouse_id] = data
                return True
            return False
        except Exception as e:
            print(f"❌ Erreur de publication: {e}")
            return False

    def generate_warehouse_data(self, warehouse_id: str) -> WarehouseData:
        """Génère des données aléatoires pour un entrepôt"""
        return WarehouseData(
            warehouse_id=warehouse_id,
            temperature_celsius=round(random.uniform(15, 30), 1),
            humidity_percent=round(random.uniform(40, 80), 1),
            stock_quantity_tons=round(random.uniform(100, 1000), 0),
            co2_ppm=round(random.uniform(400, 800), 0)
        )

    def start_simulation(self, warehouses: List[str]) -> bool:
        """
        Démarre la simulation pour une liste d'entrepôts

        Args:
            warehouses: Liste des IDs des entrepôts

        Returns:
            bool: True si la simulation a démarré
        """
        if not self.connect():
            return False

        self.warehouses = warehouses
        self.running = True

        def simulate():
            while self.running:
                for wh in warehouses:
                    data = self.generate_warehouse_data(wh)
                    self.publish_data(wh, data)
                time.sleep(self.interval)

        thread = threading.Thread(target=simulate, daemon=True)
        thread.start()

        print(f"🚀 Simulation démarrée pour {len(warehouses)} entrepôts")
        print(f"   Topic: {self.topic_prefix}/+")
        print(f"   Intervalle: {self.interval}s")

        return True

    def stop_simulation(self):
        """Arrête la simulation"""
        self.running = False
        if self.client:
            self.client.disconnect()
            self.client = None
        print("🛑 Simulation arrêtée")

    def get_last_data(self) -> Dict[str, WarehouseData]:
        """Récupère les dernières données de chaque entrepôt"""
        return self.last_data.copy()


class MQTTListener:
    """
    Écoute les données MQTT et les stocke pour le dashboard

    Args:
        broker: Adresse du broker MQTT
        port: Port du broker MQTT
        topic_prefix: Préfixe du topic
    """

    def __init__(
        self,
        broker: str = "test.mosquitto.org",
        port: int = 1883,
        topic_prefix: str = "yusuf/warehouse"
    ):
        if mqtt is None:
            raise ImportError("paho-mqtt est requis. Installez: pip install paho-mqtt")

        self.broker = broker
        self.port = port
        self.topic_prefix = topic_prefix
        self.client = None
        self.last_data: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        self.running = False

    def on_message(self, client, userdata, msg):
        """Callback lors de la réception d'un message"""
        try:
            payload = json.loads(msg.payload.decode())
            warehouse = msg.topic.split('/')[-1]
            self.last_data[warehouse] = payload
            self.history.append({
                "warehouse": warehouse,
                "data": payload,
                "received_at": time.time()
            })

            # Limiter l'historique
            if len(self.history) > 1000:
                self.history = self.history[-500:]

        except Exception as e:
            print(f"❌ Erreur de traitement: {e}")

    def start_listening(self) -> bool:
        """Commence à écouter les messages MQTT"""
        try:
            self.client = mqtt.Client()
            self.client.on_message = self.on_message
            self.client.connect(self.broker, self.port, 60)
            self.client.subscribe(f"{self.topic_prefix}/#")
            self.client.loop_start()
            self.running = True

            print(f"👂 Écoute MQTT démarrée: {self.broker}:{self.port}")
            print(f"   Topics: {self.topic_prefix}/#")
            return True

        except Exception as e:
            print(f"❌ Erreur d'écoute MQTT: {e}")
            return False

    def stop_listening(self):
        """Arrête l'écoute MQTT"""
        self.running = False
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.client = None
        print("🛑 Écoute MQTT arrêtée")

    def get_last_data(self) -> Dict[str, Dict]:
        """Récupère les dernières données de chaque entrepôt"""
        return self.last_data.copy()

    def get_history(self, limit: int = 50) -> List[Dict]:
        """Récupère l'historique des données"""
        return self.history[-limit:]

    def get_warehouse_data(self, warehouse_id: str) -> Optional[Dict]:
        """Récupère les dernières données d'un entrepôt spécifique"""
        return self.last_data.get(warehouse_id)


# ---- Fonction de démonstration ----
def demo_mqtt():
    """Démonstration du simulateur MQTT"""
    print("=== SIMULATEUR MQTT ===\n")

    # Création du simulateur
    simulator = WarehouseMQTTSimulator(
        broker="test.mosquitto.org",
        port=1883,
        interval=5
    )

    # Démarrage
    warehouses = ["Entrepôt_Nord", "Entrepôt_Sud", "Entrepôt_Centre", "Port_de_Beyrouth"]
    simulator.start_simulation(warehouses)

    # Écoute en parallèle (simulée)
    print("\n🔍 En attente des données...")

    try:
        for i in range(10):
            time.sleep(5)
            data = simulator.get_last_data()
            if data:
                print(f"\n📊 Données reçues ({i+1}):")
                for wh, d in data.items():
                    print(f"  {wh}: {d.temperature_celsius:.1f}°C, {d.humidity_percent:.0f}%")
    except KeyboardInterrupt:
        pass

    simulator.stop_simulation()


if __name__ == "__main__":
    demo_mqtt()

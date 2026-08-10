"""
Raspberry Pi Sensors – Capteurs réels
=====================================

Script pour Raspberry Pi avec capteur DHT22 (température/humidité).
Envoie les données via MQTT vers un broker.

Installation sur Raspberry Pi:
    sudo apt-get update
    sudo apt-get install python3-pip python3-dev
    pip3 install Adafruit_DHT paho-mqtt

License: CC BY-SA 4.0 – Marc Daghar
"""

import os
import sys
import time
import json
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

try:
    import Adafruit_DHT
except ImportError:
    print("⚠️  Adafruit_DHT non installé. Installez: pip install Adafruit_DHT")
    Adafruit_DHT = None

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("⚠️  paho-mqtt non installé. Installez: pip install paho-mqtt")
    mqtt = None

# ---- Configuration ----
DHT_SENSOR = Adafruit_DHT.DHT22 if Adafruit_DHT else None
DHT_PIN = 4  # GPIO pin (par défaut)

MQTT_BROKER = os.getenv("MQTT_BROKER", "test.mosquitto.org")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "yusuf/warehouse/raspberry")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "raspberry_pi_001")

WAREHOUSE_ID = os.getenv("WAREHOUSE_ID", "Entrepôt_Sud")
SENSOR_INTERVAL = int(os.getenv("SENSOR_INTERVAL", "30"))  # secondes

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SensorData:
    """Données du capteur"""
    temperature_celsius: float
    humidity_percent: float
    timestamp: float = field(default_factory=time.time)
    warehouse_id: str = WAREHOUSE_ID
    device: str = "raspberry_pi"

    def to_json(self) -> str:
        """Convertit en JSON"""
        return json.dumps({
            "device": self.device,
            "warehouse_id": self.warehouse_id,
            "timestamp": self.timestamp,
            "temperature_celsius": self.temperature_celsius,
            "humidity_percent": self.humidity_percent
        })


class RaspberrySensor:
    """
    Gestionnaire du capteur Raspberry Pi

    Args:
        sensor_type: Type de capteur (DHT22, DHT11)
        pin: GPIO pin
        broker: Adresse du broker MQTT
        port: Port du broker
        topic: Topic MQTT
        interval: Intervalle entre les lectures (secondes)
    """

    def __init__(
        self,
        sensor_type: str = "DHT22",
        pin: int = DHT_PIN,
        broker: str = MQTT_BROKER,
        port: int = MQTT_PORT,
        topic: str = MQTT_TOPIC,
        interval: int = SENSOR_INTERVAL
    ):
        if Adafruit_DHT is None:
            raise ImportError("Adafruit_DHT est requis. Installez: pip install Adafruit_DHT")

        if mqtt is None:
            raise ImportError("paho-mqtt est requis. Installez: pip install paho-mqtt")

        self.sensor_type = sensor_type
        self.pin = pin
        self.broker = broker
        self.port = port
        self.topic = topic
        self.interval = interval

        self.client = None
        self.running = False

        # Mapping des types de capteurs
        self.sensor_map = {
            "DHT11": Adafruit_DHT.DHT11,
            "DHT22": Adafruit_DHT.DHT22,
            "AM2302": Adafruit_DHT.AM2302
        }

        self.sensor = self.sensor_map.get(sensor_type, Adafruit_DHT.DHT22)

    def connect_mqtt(self) -> bool:
        """Connecte au broker MQTT"""
        try:
            self.client = mqtt.Client(client_id=MQTT_CLIENT_ID)
            self.client.connect(self.broker, self.port, 60)
            logger.info(f"✅ Connecté à MQTT: {self.broker}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur de connexion MQTT: {e}")
            return False

    def read_sensor(self) -> Optional[SensorData]:
        """
        Lit les données du capteur

        Returns:
            SensorData ou None si erreur
        """
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)

        if humidity is not None and temperature is not None:
            logger.debug(f"📊 Lecture: {temperature:.1f}°C, {humidity:.1f}%")
            return SensorData(
                temperature_celsius=round(temperature, 1),
                humidity_percent=round(humidity, 1)
            )
        else:
            logger.warning("⚠️ Erreur de lecture du capteur")
            return None

    def publish_data(self, data: SensorData) -> bool:
        """Publie les données via MQTT"""
        if not self.client:
            return False

        try:
            result = self.client.publish(self.topic, data.to_json())
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"❌ Erreur de publication: {e}")
            return False

    def run(self):
        """Boucle principale"""
        if not self.connect_mqtt():
            logger.error("Impossible de se connecter au broker MQTT")
            return

        self.running = True
        logger.info(f"🚀 Capteur {self.sensor_type} démarré (GPIO {self.pin})")
        logger.info(f"   Topic: {self.topic}")
        logger.info(f"   Intervalle: {self.interval}s")
        logger.info("   Appuyez sur Ctrl+C pour arrêter")

        try:
            while self.running:
                data = self.read_sensor()
                if data:
                    if self.publish_data(data):
                        logger.info(f"📤 Envoyé: {data.temperature_celsius:.1f}°C, {data.humidity_percent:.1f}%")
                    else:
                        logger.warning("⚠️ Échec de l'envoi MQTT")
                else:
                    logger.warning("⚠️ Échec de lecture du capteur")

                time.sleep(self.interval)

        except KeyboardInterrupt:
            logger.info("\n🛑 Arrêt demandé par l'utilisateur")

        finally:
            self.stop()

    def stop(self):
        """Arrête le capteur"""
        self.running = False
        if self.client:
            self.client.disconnect()
            self.client = None
        logger.info("🛑 Capteur arrêté")


def run_raspberry_sensor():
    """
    Fonction principale pour exécuter le capteur Raspberry Pi
    Utilise les variables d'environnement pour la configuration
    """
    sensor = RaspberrySensor(
        sensor_type=os.getenv("DHT_SENSOR_TYPE", "DHT22"),
        pin=int(os.getenv("DHT_PIN", "4")),
        broker=os.getenv("MQTT_BROKER", "test.mosquitto.org"),
        port=int(os.getenv("MQTT_PORT", "1883")),
        topic=os.getenv("MQTT_TOPIC", "yusuf/warehouse/raspberry"),
        interval=int(os.getenv("SENSOR_INTERVAL", "30"))
    )

    sensor.run()


# ---- Script principal ----
if __name__ == "__main__":
    print("=" * 50)
    print("🖥️  RASPBERRY PI – CAPTEUR DHT22")
    print("=" * 50)

    # Vérification des dépendances
    if Adafruit_DHT is None:
        print("❌ Adafruit_DHT non installé")
        print("   sudo apt-get install python3-pip python3-dev")
        print("   pip3 install Adafruit_DHT")
        sys.exit(1)

    if mqtt is None:
        print("❌ paho-mqtt non installé")
        print("   pip3 install paho-mqtt")
        sys.exit(1)

    # Vérification du GPIO
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DHT_PIN, GPIO.IN)
        GPIO.cleanup()
        print(f"✅ GPIO {DHT_PIN} disponible")
    except ImportError:
        print("⚠️  RPi.GPIO non disponible (peut-être pas sur un Raspberry Pi)")
    except Exception as e:
        print(f"⚠️  Erreur GPIO: {e}")

    print(f"\n📡 Capteur: DHT22 sur GPIO {DHT_PIN}")
    print(f"📤 MQTT: {MQTT_BROKER}:{MQTT_PORT} → {MQTT_TOPIC}")
    print(f"⏱️  Intervalle: {SENSOR_INTERVAL}s")
    print("\n" + "=" * 50)

    # Lancement
    run_raspberry_sensor()

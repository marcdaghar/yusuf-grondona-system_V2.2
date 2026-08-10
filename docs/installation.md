# Guide d'installation

## 📋 Prérequis

- **Python** : 3.10 ou supérieur
- **RAM** : 4 Go minimum (8 Go recommandé)
- **Stockage** : 2 Go minimum
- **Système** : Linux, macOS ou Windows (WSL2 recommandé)

### Dépendances optionnelles

- **Docker** : pour le déploiement conteneurisé
- **Raspberry Pi** : pour les capteurs IoT
- **Node.js** : pour le SDK JavaScript

## 🐍 Installation Python

### 1. Cloner le dépôt

```bash
git clone https://github.com/barberoussedine/yusuf-grondona-system.git
cd yusuf-grondona-system
2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows
3. Installer les dépendances
# Dépendances minimales
pip install -r requirements.txt

# Dépendances complètes (ML, blockchain, IoT)
pip install -r requirements_full.txt
4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API et configurations
5. Initialiser la base de données
python -c "from database.db_manager import init_db; init_db()"
🐳 Installation Docker
1. Construire l'image
docker build -t yusuf-grondona .
2. Lancer avec Docker Compose
# Production complète
docker compose -f deploy/docker-compose.prod.yml up -d

# Version VPS (allégée)
docker compose -f deploy/docker-compose.vps.yml up -d

# Monitoring
docker compose -f deploy/docker-compose.monitoring.yml up -d
3. Vérifier les services
docker compose ps
curl http://localhost:8000/health
🖥️ Installation sur Raspberry Pi
1. Préparer le Raspberry Pi
sudo apt update
sudo apt install python3-pip python3-dev
2. Installer les dépendances IoT
pip install Adafruit_DHT paho-mqtt
3. Configurer le capteur
# Éditer .env
DHT_SENSOR_TYPE=DHT22
DHT_PIN=4
MQTT_BROKER=test.mosquitto.org
4. Lancer le capteur
python iot/raspberry_sensors.py
📱 Installation de l'application mobile
1. Préparer l'environnement React Native
npm install -g react-native-cli
2. Installer les dépendances
cd mobile/muhtassib_app
npm install
3. Lancer sur Android
npx react-native run-android
4. Lancer sur iOS (Mac uniquement)
npx react-native run-ios
🔧 Vérification de l'installation
1. Tester l'API
curl http://localhost:8000/health
# Réponse attendue: {"status":"healthy","timestamp":...}
2. Tester le dashboard
Ouvrir http://localhost:8501 dans un navigateur
3. Tester la simulation
python simulation/run_full.py --years 1 --output test.json
🐛 Dépannage
Erreur : "Module not found"
pip install -r requirements_full.txt
Erreur : "Port already in use"
# Changer le port
uvicorn api.main:app --port 8001
Erreur : "Database locked"
# Supprimer le fichier de verrouillage
rm data/yusuf_grondona.db-journal

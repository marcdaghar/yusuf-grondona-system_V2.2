# Architecture technique

## 🏗️ Vue d'ensemble
┌─────────────────────────────────────────────────────────────────────────────┐ │                         YUSUF-GRONDONA SYSTEM                               │ ├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤ │  Frontend       │  Backend        │  Blockchain     │  IoT & Drones         │ │  Dashboard      │  API FastAPI    │  Smart Contracts│  Capteurs MQTT        │ │  Streamlit      │  Auth JWT       │  DAO / MultiSig │  Raspberry Pi         │ │  Mobile App     │  WebSocket      │  ZakatTracker   │  Drone Controller     │ └─────────────────┴─────────────────┴─────────────────┴───────────────────────┘ │ ▼ ┌─────────────────────────────────────────────────────────────────────────────┐ │                         CORE ECONOMIC MODEL                                 │ │  Nuqud (or/argent)  |  Fulus (vélocité)  |  CRD Grondona  |  Hisba         │ │  Zakat  |  BRI Network  |  Simulation  |  Stress Tests                      │ └─────────────────────────────────────────────────────────────────────────────┘

## 📦 Modules principaux

### 1. Core (`src/core/`)

| Module | Description |
|--------|-------------|
| `nuqud.py` | Or/argent comme étalon et réserve de valeur |
| `fulus.py` | Monnaie de vélocité |
| `grondona_crd.py` | Commodity Reserve Department |
| `bri_network.py` | Réseau multi-zones |
| `hisba.py` | Inspection du marché |
| `zakat_nuqud.py` | Zakat payable en nuqud |
| `riba_rules.py` | Règles Al-Fadl / Al-Nasia |

### 2. Simulation (`src/simulation/`)

| Module | Description |
|--------|-------------|
| `agents.py` | Guildes, commerçants, consommateurs |
| `market_advanced.py` | Souq main à main |
| `run_full.py` | Moteur de simulation |
| `blockchain_sim.py` | Ledger SHA256 |
| `logistics_shocks.py` | Chocs logistiques |
| `crisis_scenarios.py` | Scénarios de crise |
| `climate_crisis.py` | Chocs climatiques |
| `stress_test.py` | Tests de résistance |

### 3. Blockchain (`blockchain/`)

| Module | Description |
|--------|-------------|
| `contracts/dao_governance.sol` | DAO YGDAO |
| `contracts/MultiSigCRD.sol` | MultiSig 3/5 |
| `contracts/CarbonCreditToken.sol` | BCC |
| `contracts/ReputationToken.sol` | MREP |
| `contracts/ZakatTracker.sol` | Traçabilité Zakat |
| `contracts/RewardToken.sol` | YGR |
| `contracts/CitizenToken.sol` | CPT |
| `zk/transfer.zok` | Circuit ZoKrates |
| `ethereum_connector.py` | Connexion Web3 |
| `chainlink_oracle_consumer.py` | Oracles Chainlink |
| `bsn_bridge.py` | Interopérabilité BSN |

### 4. API (`api/`)

| Endpoint | Description |
|----------|-------------|
| `/status` | État du système |
| `/run` | Lancement simulation |
| `/transfer` | Transfert inter-zones |
| `/metrics` | Métriques économiques |
| `/token` | Authentification JWT |
| `/compliance/certify` | Certification halal |
| `/api/v1/*` | API publique BRI |

### 5. Dashboard (`dashboard/`)

| Module | Description |
|--------|-------------|
| `complete_system.py` | Point d'entrée unifié |
| `ultimate_platform_v5.py` | Plateforme ultime |
| `bri_world_map.py` | Carte BRI 3D |
| `esg_metrics.py` | Indicateurs ESG |
| `dao_governance.py` | Gouvernance DAO |
| `iot_integration.py` | IoT temps réel |

## 🔄 Flux de données
[Agents] → [Souq] → [Transactions] → [Blockchain] ↓          ↓           ↓              ↓ [Production] [CRD]    [Zakat]        [Traçabilité] ↓          ↓           ↓              ↓ [Logistique] [Hisba]   [BRI]        [Audit]

## 🏗️ Diagramme de déploiement
┌─────────────────────────────────────────────────────────────────────────────┐ │                              VPS / Serveur                                  │ │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │ │  │   Nginx     │  │   API       │  │  Dashboard  │  │  PostgreSQL │       │ │  │  (Reverse)  │  │  (FastAPI)  │  │ (Streamlit) │  │             │       │ │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │ │                              │                                              │ │                              ▼                                              │ │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                        │ │  │  Prometheus │  │   Grafana   │  │  MQTT       │                        │ │  │             │  │             │  │  Broker     │                        │ │  └─────────────┘  └─────────────┘  └─────────────┘                        │ └─────────────────────────────────────────────────────────────────────────────┘

## 🔒 Sécurité

- **Authentification** : JWT + API Key
- **Chiffrement** : HTTPS (Let's Encrypt)
- **Blockchain** : MultiSig 3/5 pour décisions critiques
- **Audit** : Traçabilité complète des transactions
- **Sanctions** : Circuit breaker pour Λ > 0.9

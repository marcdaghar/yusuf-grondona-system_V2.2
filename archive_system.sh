#!/bin/bash
# ============================================================
# archive_system.sh – Figer l'état complet du système Yusuf‑Grondona
# Sortie : yusuf_grondona_$(date +%Y%m%d_%H%M%S).tar.gz + manifeste + sommes
# ============================================================

set -e

# ---- Couleurs ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ---- Configuration ----
BASE_NAME="yusuf_grondona"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="${BASE_NAME}_${TIMESTAMP}.tar.gz"
MANIFEST="MANIFEST_${TIMESTAMP}.txt"
CHECKSUMS="SHA256SUMS_${TIMESTAMP}.txt"
TEMP_DIR="/tmp/${BASE_NAME}_archive"

# ---- Initialisation ----
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║             FIGEMENT DU SYSTÈME YUSUF-GRONDONA              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📦 Archive cible : ${YELLOW}${ARCHIVE_NAME}${NC}"
echo -e "📁 Version : ${BLUE}$(cat VERSION 2>/dev/null || echo 'inconnue')${NC}"
echo ""

# ---- Vérification des prérequis ----
command -v tar >/dev/null 2>&1 || { echo -e "${RED}❌ tar est requis${NC}"; exit 1; }
command -v sha256sum >/dev/null 2>&1 || { echo -e "${RED}❌ sha256sum est requis${NC}"; exit 1; }
command -v rsync >/dev/null 2>&1 || { echo -e "${YELLOW}⚠️ rsync non trouvé, utilisation de cp${NC}"; RSYNC="cp -r"; } || RSYNC="rsync -av"

# ---- Création du répertoire temporaire ----
echo -e "${BLUE}📁 Création du répertoire temporaire...${NC}"
rm -rf "${TEMP_DIR}"
mkdir -p "${TEMP_DIR}/${BASE_NAME}"

# ---- Copie des sources ----
echo -e "${BLUE}📂 Copie des sources...${NC}"

# Dossiers à inclure (structure principale)
INCLUDE_DIRS=(
    "src"
    "api"
    "blockchain"
    "dashboard"
    "simulation"
    "core"
    "governance"
    "ai"
    "iot"
    "drones"
    "carbon"
    "monitoring"
    "deploy"
    "tests"
    "docs"
    "notebooks"
    "data"
    "scripts"
    "sdk"
    "mobile"
    "explorer"
    "audit"
    "prediction"
    "compliance"
    "tools"
    "config"
)

# Fichiers à inclure à la racine
INCLUDE_FILES=(
    "README.md"
    "LICENSE"
    "CONTRIBUTING.md"
    ".zenodo.json"
    "VERSION"
    "requirements.txt"
    "requirements_full.txt"
    "mkdocs.yml"
    ".env.example"
    ".gitignore"
    "archive_system.sh"
    "setup.py"
    "pyproject.toml"
)

# Copie des dossiers
for dir in "${INCLUDE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        mkdir -p "${TEMP_DIR}/${BASE_NAME}/$(dirname $dir)" 2>/dev/null || true
        $RSYNC "$dir" "${TEMP_DIR}/${BASE_NAME}/" 2>/dev/null || echo -e "${YELLOW}⚠️ Dossier $dir non trouvé${NC}"
        echo -e "   ✅ $dir/"
    else
        echo -e "${YELLOW}⚠️ Dossier $dir non trouvé, ignoré${NC}"
    fi
done

# Copie des fichiers
for file in "${INCLUDE_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "${TEMP_DIR}/${BASE_NAME}/" 2>/dev/null || true
        echo -e "   ✅ $file"
    else
        echo -e "${YELLOW}⚠️ Fichier $file non trouvé, ignoré${NC}"
    fi
done

# ---- Génération du manifeste ----
echo -e "${BLUE}📋 Génération du manifeste...${NC}"
cat > "${TEMP_DIR}/${MANIFEST}" <<EOF
# ============================================================
# MANIFEST – Yusuf‑Grondona System
# ============================================================
# Archive: ${ARCHIVE_NAME}
# Date: $(date -Iseconds)
# Version: $(cat VERSION 2>/dev/null || echo 'inconnue')
# Licence: CC BY-SA 4.0 – Marc Daghar
# ============================================================

## Modules inclus

$(echo "# --- Structure des dossiers ---")
for dir in "${INCLUDE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "- $dir/"
        find "$dir" -type f -name "*.py" -o -name "*.sol" -o -name "*.md" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.sh" -o -name "*.js" -o -name "*.html" -o -name "*.css" -o -name "*.txt" | head -20 | sed 's/^/  /'
    fi
done

echo ""
echo "## Fichiers racine"
for file in "${INCLUDE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "- $file"
    fi
done

echo ""
echo "## Métadonnées"
echo "- Nombre total de fichiers : $(find "${TEMP_DIR}/${BASE_NAME}" -type f | wc -l)"
echo "- Taille totale : $(du -sh "${TEMP_DIR}/${BASE_NAME}" 2>/dev/null | cut -f1)"
echo "- Auteur : Marc Daghar"
echo "- Licence : CC BY-SA 4.0"

echo ""
echo "## Notes"
echo "Cet état correspond à la version stable du système Yusuf‑Grondona."
echo "Toute distribution doit conserver la licence CC BY-SA 4.0 et la mention 'Marc Daghar'."
echo ""

echo "## Contenu des modules principaux"
echo ""

# Description des modules
echo "### core/"
echo "- nuqud.py : Or/argent – étalon + réserve"
echo "- fulus.py : Monnaie de vélocité"
echo "- grondona_crd.py : CRD avec stockpiles"
echo "- bri_network.py : Réseau BRI multi-zones"
echo "- hisba.py : Inspection du marché"
echo "- zakat_nuqud.py : Zakat payable uniquement en nuqud"
echo "- riba_rules.py : Règles Al-Fadl / Al-Nasia"
echo ""

echo "### simulation/"
echo "- agents.py : Guildes, commerçants, consommateurs"
echo "- market_advanced.py : Souq main à main"
echo "- run_full.py : Moteur de simulation"
echo "- blockchain_sim.py : Ledger SHA256"
echo "- logistics_shocks.py : Chocs logistiques"
echo "- crisis_scenarios.py : Scénarios de crise"
echo ""

echo "### blockchain/"
echo "- contracts/ : Smart contracts (DAO, MultiSig, Carbon, Reputation, Zakat)"
echo "- deploy/ : Scripts de déploiement"
echo "- zk/ : Circuits ZoKrates"
echo "- ethereum_connector.py : Connexion Ethereum"
echo "- chainlink_oracle_consumer.py : Oracles Chainlink"
echo "- fulus_explorer.py : Explorateur de blocs"
echo ""

echo "### dashboard/"
echo "- complete_system.py : Point d'entrée unifié"
echo "- ultimate_platform_v5.py : Plateforme ultime"
echo "- streamlit_app_with_alerts.py : Dashboard principal"
echo "- bri_world_map.py : Carte BRI 3D"
echo "- esg_metrics.py : Indicateurs ESG"
echo "- dao_governance.py : Gouvernance DAO"
echo "- iot_integration.py : IoT temps réel"
echo "- pdf_generator.py : Export PDF"
echo ""

echo "### api/"
echo "- main.py : API principale"
echo "- public_api.py : API pour partenaires BRI"
echo "- mobile_api.py : API pour application mobile"
echo "- ar_inspection.py : Réalité augmentée"
echo "- webhooks.py : Webhooks pour partenaires"
echo "- websocket_manager.py : Temps réel"
echo ""

echo "### ai/"
echo "- muhtassib_ai.py : Assistant du muhtassib"
echo "- rl_policy_optimizer.py : PPO pour politique monétaire"
echo "- esg_forecast.py : Prédiction ESG 5 ans"
echo "- backtest_rl.py : Backtest sur données historiques"
echo "- crisis_predictor.py : Early warning system"
echo ""

echo "### iot/"
echo "- mqtt_simulator.py : Simulation MQTT"
echo "- raspberry_sensors.py : Capteurs DHT22 → MQTT"
echo ""

echo "### drones/"
echo "- drone_controller.py : Surveillance drones + WebSocket"
echo ""

echo "### carbon/"
echo "- offsetting_manager.py : Crédits carbone BCC"
echo ""

echo "### mobile/"
echo "- muhtassib_app/App.js : Application React Native"
echo ""

echo "### sdk/"
echo "- python/yusuf_sdk.py : SDK Python"
echo "- js/yusuf-sdk.js : SDK JavaScript"
echo ""

echo "### monitoring/"
echo "- prometheus.yml : Configuration Prometheus"
echo "- alert_rules.yml : Règles d'alertes"
echo "- alertmanager.yml : Configuration Alertmanager"
echo "- grafana_dashboard.json : Dashboard Grafana"
echo ""

echo "### deploy/"
echo "- docker-compose.prod.yml : Production"
echo "- docker-compose.vps.yml : VPS"
echo "- docker-compose.monitoring.yml : Monitoring"
echo "- Dockerfile.prod : API"
echo "- Dockerfile.multiarch : Multi-arch"
echo "- deploy_vps.sh : Script de déploiement"
echo "- setup_ssl.sh : HTTPS"
echo ""

echo "### docs/"
echo "- index.md : Documentation principale"
echo "- whitepaper_fiducial.md : White paper"
echo "- faq.md : Foire aux questions"
echo "- user_guide_nontech.md : Guide utilisateur"
echo "- bri_nuqud_geopolitics.md : Géopolitique BRI"
echo ""

echo "## Dépendances principales"
echo ""
echo "### Requirements minimaux (requirements.txt)"
cat requirements.txt 2>/dev/null || echo "  (non trouvé)"
echo ""
echo "### Requirements complets (requirements_full.txt)"
cat requirements_full.txt 2>/dev/null || echo "  (non trouvé)"
echo ""
echo "## Sommes SHA256"
echo "Voir le fichier ${CHECKSUMS}"
EOF

# ---- Création des sommes de contrôle SHA256 ----
echo -e "${BLUE}🔐 Génération des sommes SHA256...${NC}"
cd "${TEMP_DIR}"
find "${BASE_NAME}" -type f -exec sha256sum {} \; | sort > "${CHECKSUMS}"
cd - > /dev/null

# ---- Archivage final ----
echo -e "${BLUE}📦 Création de l'archive...${NC}"
tar -czf "${ARCHIVE_NAME}" -C "${TEMP_DIR}" "${BASE_NAME}" "${MANIFEST}" "${CHECKSUMS}"

# ---- Nettoyage ----
rm -rf "${TEMP_DIR}"

# ---- Résultat ----
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ FIGEMENT TERMINÉ                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📦 Archive : ${YELLOW}${ARCHIVE_NAME}${NC}"
echo -e "📋 Manifeste inclus : ${YELLOW}${MANIFEST}${NC}"
echo -e "🔐 Sommes SHA256 : ${YELLOW}${CHECKSUMS}${NC}"

# ---- Taille ----
SIZE=$(du -h "${ARCHIVE_NAME}" | cut -f1)
echo -e "📊 Taille : ${GREEN}${SIZE}${NC}"

# ---- Vérification ----
echo ""
echo -e "${BLUE}🔍 Vérification de l'intégrité :${NC}"
echo "  tar -tzf ${ARCHIVE_NAME} > /dev/null"
echo "  sha256sum -c ${CHECKSUMS}"

# ---- Somme de l'archive ----
echo ""
echo -e "${BLUE}🔐 Somme SHA256 de l'archive :${NC}"
sha256sum "${ARCHIVE_NAME}"

echo ""
echo -e "${GREEN}✅ Archive prête à être publiée sur Zenodo ou GitHub Releases${NC}"

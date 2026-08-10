#!/bin/bash
# ============================================================
# deploy_production.sh – Déploiement Production Complet
# Yusuf-Grondona System
# ============================================================
#
# Script de déploiement complet en production.
#
# Usage:
#   chmod +x deploy_production.sh
#   ./deploy_production.sh
#
# License: CC BY-SA 4.0 – Marc Daghar
# ============================================================

set -e

# ---- Couleurs ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            DÉPLOIEMENT PRODUCTION COMPLET                  ║${NC}"
echo -e "${GREEN}║                   Yusuf-Grondona System                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ---- Vérification ----
if [ ! -f .env ]; then
    echo -e "${RED}❌ Fichier .env manquant. Copiez .env.example et configurez-le.${NC}"
    exit 1
fi

# ---- SSL ----
echo -e "${BLUE}🔐 Configuration SSL...${NC}"
if [ -f setup_ssl.sh ]; then
    ./setup_ssl.sh
else
    echo -e "${YELLOW}⚠️  setup_ssl.sh non trouvé. SSL non configuré.${NC}"
fi

# ---- Monitoring ----
echo ""
echo -e "${BLUE}📊 Lancement du monitoring...${NC}"
docker compose -f deploy/docker-compose.monitoring.yml up -d

# ---- Production ----
echo ""
echo -e "${BLUE}🚀 Lancement des services de production...${NC}"
docker compose -f deploy/docker-compose.prod.yml up -d --build

# ---- Vérification ----
echo ""
echo -e "${BLUE}🔍 Vérification des services...${NC}"
sleep 10

for service in api dashboard postgres nginx; do
    if docker inspect --format='{{.State.Status}}' "yusuf-$service" 2>/dev/null | grep -q "running"; then
        echo -e "${GREEN}✅ $service${NC}"
    else
        echo -e "${RED}❌ $service${NC}"
    fi
done

# ---- Informations ----
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                ✅ DÉPLOIEMENT TERMINÉ                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📊 Accès :"
echo -e "  API        : https://api.yusuf-grondona.com/docs"
echo -e "  Dashboard  : https://admin.yusuf-grondona.com"
echo -e "  Grafana    : https://grafana.yusuf-grondona.com"
echo ""
echo -e "📋 Logs :"
echo -e "  docker compose -f deploy/docker-compose.prod.yml logs -f"

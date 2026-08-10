#!/bin/bash
# ============================================================
# deploy_vps.sh – Déploiement sur VPS
# Yusuf-Grondona System
# ============================================================
#
# Script de déploiement automatique sur un VPS Ubuntu 22.04.
#
# Usage:
#   chmod +x deploy_vps.sh
#   ./deploy_vps.sh
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
echo -e "${GREEN}║              DÉPLOIEMENT SUR VPS                           ║${NC}"
echo -e "${GREEN}║                   Yusuf-Grondona System                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ---- Vérification des prérequis ----
echo -e "${BLUE}📋 Vérification des prérequis...${NC}"

# Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker non installé. Installation...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Docker installé${NC}"
else
    echo -e "${GREEN}✅ Docker présent${NC}"
fi

# Docker Compose V2
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose non installé. Installation...${NC}"
    sudo apt update
    sudo apt install -y docker-compose-plugin
    echo -e "${GREEN}✅ Docker Compose installé${NC}"
else
    echo -e "${GREEN}✅ Docker Compose présent${NC}"
fi

# Git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠️  Git non installé. Installation...${NC}"
    sudo apt update
    sudo apt install -y git
    echo -e "${GREEN}✅ Git installé${NC}"
else
    echo -e "${GREEN}✅ Git présent${NC}"
fi

# ---- Configuration ----
echo ""
echo -e "${BLUE}📁 Configuration du projet...${NC}"

# Répertoires
mkdir -p data logs ssl

# Variables d'environnement
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Fichier .env manquant. Création...${NC}"
    cat > .env <<EOF
# Yusuf-Grondona System
JWT_SECRET_KEY=$(openssl rand -base64 32)
DB_PASSWORD=$(openssl rand -base64 12)
GRAFANA_PASSWORD=$(openssl rand -base64 12)
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/demo
CORS_ORIGINS=*
EOF
    echo -e "${GREEN}✅ .env créé${NC}"
else
    echo -e "${GREEN}✅ .env présent${NC}"
fi

# ---- Lancement des services ----
echo ""
echo -e "${BLUE}🐳 Lancement des services...${NC}"

# Arrêt des services existants
docker compose -f deploy/docker-compose.vps.yml down 2>/dev/null || true

# Build et lancement
docker compose -f deploy/docker-compose.vps.yml up -d --build

# ---- Vérification ----
echo ""
echo -e "${BLUE}🔍 Vérification des services...${NC}"
sleep 5

# API
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ API opérationnelle sur http://localhost:8000${NC}"
else
    echo -e "${RED}❌ API non répondante${NC}"
fi

# Dashboard
if curl -s http://localhost:8501 > /dev/null; then
    echo -e "${GREEN}✅ Dashboard opérationnel sur http://localhost:8501${NC}"
else
    echo -e "${RED}❌ Dashboard non répondant${NC}"
fi

# ---- Informations ----
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ DÉPLOIEMENT TERMINÉ                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📊 Accès :"
echo -e "  API        : http://$(curl -s ifconfig.me 2>/dev/null || echo 'localhost'):8000/docs"
echo -e "  Dashboard  : http://$(curl -s ifconfig.me 2>/dev/null || echo 'localhost'):8501"
echo -e "  Grafana    : http://$(curl -s ifconfig.me 2>/dev/null || echo 'localhost'):3000 (admin/${GRAFANA_PASSWORD:-admin})"
echo ""
echo -e "📋 Commandes utiles :"
echo -e "  docker compose -f deploy/docker-compose.vps.yml logs -f"
echo -e "  docker compose -f deploy/docker-compose.vps.yml down"
echo -e "  docker compose -f deploy/docker-compose.vps.yml restart"
echo ""

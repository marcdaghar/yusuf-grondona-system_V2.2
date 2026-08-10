#!/bin/bash
# ============================================================
# setup_ssl.sh – Configuration SSL Let's Encrypt
# Yusuf-Grondona System
# ============================================================
#
# Installe et configure Let's Encrypt pour HTTPS.
#
# Usage:
#   chmod +x setup_ssl.sh
#   ./setup_ssl.sh
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
echo -e "${GREEN}║              CONFIGURATION SSL                            ║${NC}"
echo -e "${GREEN}║                   Let's Encrypt                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ---- Variables ----
DOMAIN=${DOMAIN:-"admin.yusuf-grondona.com"}
EMAIL=${EMAIL:-"admin@yusuf-grondona.com"}
SSL_DIR=${SSL_DIR:-"./ssl"}

# ---- Vérification ----
if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "admin.yusuf-grondona.com" ]; then
    echo -e "${YELLOW}⚠️  Domaine par défaut. Modifiez la variable DOMAIN.${NC}"
    echo -e "   export DOMAIN=votre-domaine.com"
    exit 1
fi

# ---- Installation Certbot ----
echo -e "${BLUE}📦 Installation de Certbot...${NC}"

if command -v certbot &> /dev/null; then
    echo -e "${GREEN}✅ Certbot déjà installé${NC}"
else
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
    echo -e "${GREEN}✅ Certbot installé${NC}"
fi

# ---- Création du certificat ----
echo ""
echo -e "${BLUE}🔐 Création du certificat pour ${DOMAIN}...${NC}"

mkdir -p $SSL_DIR

sudo certbot certonly --standalone \
    -d $DOMAIN \
    --non-interactive \
    --agree-tos \
    -m $EMAIL \
    --cert-path $SSL_DIR/cert.pem \
    --key-path $SSL_DIR/key.pem \
    --fullchain-path $SSL_DIR/fullchain.pem \
    --chain-path $SSL_DIR/chain.pem

# ---- Permissions ----
echo ""
echo -e "${BLUE}🔑 Configuration des permissions...${NC}"
sudo chmod 644 $SSL_DIR/*.pem
sudo chown $USER:$USER $SSL_DIR/*.pem

# ---- Renouvellement automatique ----
echo ""
echo -e "${BLUE}⏰ Configuration du renouvellement automatique...${NC}"

# Cron pour le renouvellement
CRON_FILE="/etc/cron.daily/certbot-renew"
sudo cat > $CRON_FILE <<EOF
#!/bin/bash
/usr/bin/certbot renew --quiet --post-hook "docker restart yusuf-nginx"
EOF
sudo chmod +x $CRON_FILE

# Test du renouvellement
sudo certbot renew --dry-run

# ---- Vérification ----
echo ""
echo -e "${BLUE}🔍 Vérification du certificat...${NC}"
openssl x509 -in $SSL_DIR/cert.pem -text -noout | grep -E "Subject:|Not After"

# ---- Informations ----
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                ✅ SSL CONFIGURÉ                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📋 Certificat pour : ${DOMAIN}"
echo -e "📁 Emplacement     : ${SSL_DIR}/"
echo -e "⏰ Renouvellement  : Quotidien (cron)"
echo ""
echo -e "🔗 Accès HTTPS    : https://${DOMAIN}"

# API Reference

## 📋 Authentification

### POST `/token`

Authentification et récupération d'un token JWT.

**Body :**
```json
{
    "username": "admin",
    "password": "changeme123"
}
Réponse :
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
📊 Endpoints publics
GET /health
Vérification de la santé du service.
Réponse :
{
    "status": "healthy",
    "timestamp": 1234567890.0
}
GET /status
État de la simulation.
Réponse :
{
    "running": false,
    "current_year": 0,
    "last_run": 1234567890.0,
    "network_ready": true
}
GET /metrics
Métriques économiques globales.
Réponse :
{
    "global_reserves_nuqud_g": 25000.0,
    "global_fulus_supply": 150000.0,
    "zones": {
        "Chine": {
            "nuqud_reserve_grams": 20000,
            "fulus_supply": 100000,
            "exchange_rate": 10.0
        }
    }
}
POST /run
Lancement d'une simulation.
Body :
{
    "years": 1,
    "use_crd": true,
    "use_zakat": true,
    "use_bri": true,
    "use_blockchain": true
}
Réponse :
{
    "years": 1,
    "transactions": [...],
    "zakat_collected": 250.0,
    "bri_summary": {...}
}
POST /transfer
Transfert inter-zones.
Body :
{
    "from_zone": "Chine",
    "to_zone": "NUL",
    "amount_nuqud": 100.0
}
Réponse :
{
    "success": true,
    "from": "Chine",
    "to": "NUL",
    "gross": 100.0,
    "fee": 0.1,
    "net": 99.9
}
🕌 Endpoints Zakat
GET /zakat/history/{payer}
Historique des paiements de Zakat.
Réponse :
{
    "payer": "economy",
    "zakat_payments": [
        {
            "type": "zakat",
            "amount": 25.0,
            "currency": "nuqud",
            "year": 1
        }
    ]
}
✅ Endpoints Compliance
POST /compliance/certify
Certification halal d'un produit.
Paramètres :
    • product_name : Nom du produit
    • issuer : Émetteur du certificat
    • criteria : Liste des critères
Réponse :
{
    "certificate_id": "abc123...",
    "product_name": "Viande de bœuf",
    "issuer": "Muhtassib",
    "valid_until": "2027-01-01T00:00:00"
}
POST /compliance/audit_contract
Audit d'un smart contract.
Body :
{
    "contract_code": "function lend(amount, rate) { return amount * rate; }"
}
Réponse :
{
    "contract_hash": "0x...",
    "compliant": false,
    "issues": ["Présence de mot 'interest' (riba potentiel)"],
    "sharia_grade": "C"
}
🌐 API Publique (partenaires BRI)
POST /api/v1/exchange_rate
Taux de change entre zones.
Body :
{
    "from_zone": "Chine",
    "to_zone": "France",
    "amount_fulus": 1000
}
Réponse :
{
    "from": "Chine",
    "to": "France",
    "amount": 1000,
    "converted": 1150,
    "rate": 1.15
}
GET /api/v1/esg/{partner_id}
Score ESG d'un partenaire.
Réponse :
{
    "partner": "Chine",
    "year": 2026,
    "esg": {
        "environmental": 68,
        "social": 72,
        "governance": 65,
        "global": 68
    }
}
🔐 Endpoints protégés
Tous les endpoints suivants nécessitent un token JWT.
GET /secure/metrics
Métriques sécurisées.
POST /admin/bri_zones
Création de zones BRI (admin uniquement).
POST /admin/api_key/{username}
Génération d'une clé API (admin uniquement).
POST /admin/reset
Réinitialisation du système (admin uniquement).

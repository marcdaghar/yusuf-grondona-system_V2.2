# Yusuf-Grondona Monetary System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/barberoussedine/yusuf-grondona-system)
[![License](https://img.shields.io/badge/license-CC--BY--SA--4.0-blue.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.xxxxxx.svg)](https://doi.org/10.5281/zenodo.xxxxxx)

## 🏛️ Un système monétaire bimétallique pour l'économie réelle

Le système **Yusuf-Grondona** combine :

- **Nuqud (or/argent)** – réserve de valeur stable, étalon de mesure
- **Fulus** – monnaie de circulation à vélocité
- **CRD Grondona** – prix plancher/plafond avec stockpiles physiques
- **BRI Network** – transferts inter-zones en nuqud
- **Hisba** – inspection humaine du marché assistée par IA
- **Zakat politique** – collectée par l'émir, redistribuée aux 8 catégories
- **Blockchain** – DAO, MultiSig, crédits carbone, réputation

## 🚀 Lancer le système

```bash
git clone https://github.com/barberoussedine/yusuf-grondona-system.git
cd yusuf-grondona-system
pip install -r requirements_full.txt
streamlit run dashboard/complete_system.py

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/barberoussedine/yusuf-grondona-system)
[![License](https://img.shields.io/badge/license-CC--BY--SA--4.0-blue.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.xxxxxx.svg)](https://doi.org/10.5281/zenodo.xxxxxx)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/)

## 🏛️ Un système monétaire bimétallique pour l'économie réelle

Le système **Yusuf-Grondona** propose une alternative crédible à la finance chrématistique qui a appauvri et endetté des générations. Il combine :

| Composant | Fonction |
|-----------|----------|
| **Nuqud (or/argent)** | Réserve de valeur stable, étalon de mesure |
| **Fulus** | Monnaie de circulation à vélocité (seule fonction : transaction) |
| **CRD Grondona** | Prix plancher/plafond avec stockpiles physiques |
| **BRI Network** | Transferts inter-zones en nuqud |
| **Hisba** | Inspection humaine du marché assistée par IA |
| **Zakat politique** | Collectée par l'émir, redistribuée aux 8 catégories |
| **Blockchain** | DAO, MultiSig, crédits carbone, réputation, Zakat tracker |

## 📖 Principes fondamentaux

### 1. La hiérarchie monétaire à trois couches
COUCHE 1 (THAMAN) — ÉTALON DE MESURE
├── Or (primus inter pares)
└── Argent (primus inter pares)

COUCHE 2 (ADOSSEMENT) — RÉSERVE DE VALEUR
├── Panier Grondona (blé, cuivre, sel, terres rares)
├── Stockpiles publics (principe de Yusuf : stocker en abondance, distribuer en rareté)
└── CRD avec prix plancher/plafond

COUCHE 3 (MONNAIE DE VÉLOCITÉ) — FULUS
├── Monnaie locale convertible en panier Grondona
├── Système de paiement indépendant
└── Social Credit (distribution de la rente séignioriale)

text

### 2. Nuqud vs Fulus

| Caractéristique | Nuqud (نقود) | Fulus (فلس) |
|-----------------|--------------|-------------|
| Rôle | Mesure de valeur + Réserve de valeur | Moyen d'échange UNIQUEMENT |
| Règles du riba | STRICTES (ni surplus, ni délai) | ASSOUPLIES (petit surplus autorisé ≤5%) |
| Exemples | Or, argent, sel, blé (dans le panier) | Monnaie convertible |
| Thermodynamique | ~0% taux d'intérêt réel | Vélocité comme SEULE fonction |

**Règle d'or :** Dès qu'une commodité entre dans le panier Grondona, elle devient *nuqud* :
- Elle devient un ÉTALON DE MESURE
- Elle devient une RÉSERVE DE VALEUR
- Elle SORT du système monétaire (n'est plus *fulus*)

### 3. Le paramètre de bifurcation Λ
Λ = (D · r) / Ė_low

text

- **D** = Dette totale
- **r** = Taux d'intérêt moyen
- **Ė_low** = Taux d'extraction d'énergie/matières premières

**Seuil critique :** Λ > 1 → effondrement inévitable

## 🚀 Lancer le système

### Avec Docker (recommandé)

```bash
git clone https://github.com/barberoussedine/yusuf-grondona-system.git
cd yusuf-grondona-system
docker-compose up --build
Accès :

API : http://localhost:8000/docs

Dashboard : http://localhost:8501

Grafana : http://localhost:3000 (admin/admin)

Sans Docker
bash
pip install -r requirements_full.txt
uvicorn api.main:app --reload --port 8000 &
streamlit run dashboard/complete_system.py
📚 Documentation
bash
mkdocs serve
# Ouvrir http://localhost:8000
Documentation interactive en ligne : https://barberoussedine.github.io/yusuf-grondona-system/

🧪 Tester le système
bash
# Tests unitaires
pytest tests/ -v

# Test de résistance
python simulation/stress_test.py

# Simulation complète
python simulation/run_full.py --config config_bri_full.json
🏗️ Architecture
text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         YUSUF-GRONDONA PLATEFORME                           │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────────────┤
│ ESG     │ DAO     │ Badges  │ Audit   │ Stress  │ Zakat   │ BRI Map         │
│ Prophet │ Votes   │ BRI     │ PDF     │ Test    │ Simu-   │ 3D Globe        │
│ LSTM    │         │ Gold/Silver│ Hisba │ Crise   │ lator   │ Flux            │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BLOCKCHAIN + DEFI                                 │
│  YGDAO / YGR / MGT / CPT / BCC  |  DAO Governor  |  MultiSig 3/5           │
│  Staking  |  Chainlink Oracles  |  zk-SNARKs     |  ZakatTracker           │
└─────────────────────────────────────────────────────────────────────────────┘
🤝 Contribution
Consultez CONTRIBUTING.md pour les détails.

Toute contribution doit respecter :

La licence CC BY-SA 4.0

La mention "Marc Daghar" dans les crédits

Les principes de la finance islamique (riba interdit, Zakat, hisba)

📄 Licence
CC BY-SA 4.0 – Marc Daghar

Vous êtes libres de :

Partager — copier, distribuer, transmettre l'œuvre

Adapter — remixer, transformer, créer à partir de l'œuvre

Sous les conditions suivantes :

Attribution — Vous devez citer : "Daghar, M. (2026). The BRI as a Negentropic Bifurcation: From Entropic Collapse to Yusuf-Grondona Stabilized Economy. CC BY-SA 4.0."

Partage à l'identique — Vous devez distribuer votre contribution sous la même licence.

🙏 Remerciements
ChatGPT – pour l'ossature technique initiale

DeepSeek – pour la fidélisation critique (bassira, logistique, nuqud/fulus, Zakat, hisba, BRI)

Yuk Hui – pour le concept de cosmotechnique

Ibn Khaldun – pour la théorie de l'assabiyya

Héraclite – "La guerre est grande accoucheuse de vérités."

« L'économie ne se réduit pas aux équations. C'est aussi un monde d'images, de pressentiments, de ruines devinées. »

« La monnaie ne doit ni dominer ni être dominée – elle doit ancrer. Dans le nuqud, la stabilité ; dans le fulus, la circulation ; dans la Zakat, la justice ; dans la hisba, la confiance. »

« L'économie ne se réduit pas aux équations. C'est aussi un monde d'images, de pressentiments, de ruines devinées. »

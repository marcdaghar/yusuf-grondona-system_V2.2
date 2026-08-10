# Yusuf-Grondona Monetary System

![Version](https://img.shields.io/badge/version-1.0.0-green)
![License](https://img.shields.io/badge/license-CC--BY--SA--4.0-blue)
![Python](https://img.shields.io/badge/python-3.10-blue)

## 📖 Introduction

Le système **Yusuf-Grondona** est une implémentation complète d'un système monétaire bimétallique (or/argent) avec :

- **Nuqud** : argent mesurable/pesable (étalon + réserve de valeur)
- **Fulus** : monnaie de vélocité (circulation uniquement)
- **CRD Grondona** : prix plancher/plafond avec stockpiles publics
- **Hisba** : inspection humaine du marché
- **Zakat** : collectée par l'émir, distribuée aux 8 catégories
- **BRI Network** : corridors commerciaux inter-zones

## 🎯 Objectifs

1. **Stabilité monétaire** : ancrage dans des actifs réels (or, argent, commodités)
2. **Justice sociale** : redistribution par la Zakat
3. **Transparence** : traçabilité blockchain
4. **Résilience** : face aux chocs logistiques et climatiques
5. **Souveraineté** : indépendance des banques centrales et du dollar

## 📚 Documentation

| Section | Description |
|---------|-------------|
| [Installation](installation.md) | Guide d'installation et de déploiement |
| [Architecture](architecture.md) | Architecture technique du système |
| [API Reference](api_reference.md) | Documentation des endpoints API |
| [Modèle économique](economic_model.md) | Fondements théoriques et équations |
| [Compliance](compliance.md) | Conformité halal et audits |
| [FAQ](faq.md) | Foire aux questions |
| [Guide utilisateur](user_guide_nontech.md) | Guide pour non-techniciens |
| [Géopolitique BRI](bri_nuqud_geopolitics.md) | Nuqud comme corridor monétaire |
| [White paper](whitepaper_fiducial.md) | Document de référence complet |

## 🚀 Démarrage rapide

```bash
# Cloner le dépôt
git clone https://github.com/barberoussedine/yusuf-grondona-system.git
cd yusuf-grondona-system

# Installation
pip install -r requirements_full.txt

# Lancer l'API
uvicorn api.main:app --reload --port 8000

# Lancer le dashboard
streamlit run dashboard/complete_system.py
📄 Licence
CC BY-SA 4.0 – Marc Daghar

« L'économie ne se réduit pas aux équations. C'est aussi un monde d'images, de pressentiments, de ruines devinées. »

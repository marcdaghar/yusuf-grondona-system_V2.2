# Guide de contribution – Yusuf-Grondona System

Merci de votre intérêt pour le système Yusuf-Grondona ! Ce document décrit comment contribuer au projet de manière efficace et respectueuse.

## 📋 Table des matières

1. [Code de conduite](#code-de-conduite)
2. [Comment contribuer](#comment-contribuer)
3. [Standards de code](#standards-de-code)
4. [Processus de Pull Request](#processus-de-pull-request)
5. [Licence](#licence)

## 📜 Code de conduite

### Nos engagements

En tant que contributeurs, nous nous engageons à :

- **Respecter la diversité** des perspectives, des expériences et des compétences
- **Adopter une communication bienveillante** et constructive
- **Reconnaître les contributions** des autres
- **Respecter les principes islamiques** : pas de riba (usure), promotion de la Zakat et de la hisba
- **Citer les sources** selon la licence CC BY-SA 4.0

### Comportements inacceptables

- Langage ou images à caractère discriminatoire
- Harcèlement, intimidation ou aggression
- Publication d'informations privées sans consentement
- Comportement professionnel inapproprié

## 🛠️ Comment contribuer

### Types de contributions acceptées

| Type | Description |
|------|-------------|
| 🐛 Rapport de bug | Signaler un problème dans le code |
| 💡 Suggestion d'amélioration | Proposer une nouvelle fonctionnalité |
| 📝 Documentation | Améliorer la documentation (code, README, docs/) |
| 💻 Code | Corriger des bugs ou ajouter des fonctionnalités |
| 🔬 Recherche | Validation empirique, preuves mathématiques |
| 🎨 Design | Interface, visualisation, UX |
| 🌐 Traduction | Ajouter ou améliorer les traductions (i18n) |

### Processus

1. **Fork** le dépôt
2. **Clone** votre fork : `git clone https://github.com/votre-username/yusuf-grondona-system.git`
3. **Créez une branche** : `git checkout -b feature/ma-fonctionnalite`
4. **Codez** en suivant les standards
5. **Testez** : `pytest tests/ -v`
6. **Commit** : `git commit -m "Description claire"`
7. **Push** : `git push origin feature/ma-fonctionnalite`
8. **Pull Request** : ouvrez une PR vers la branche `main`

## 📐 Standards de code

### Python

- **Version** : Python 3.10+
- **Formatage** : Black (`black .`)
- **Linting** : Ruff (`ruff check .`)
- **Typage** : Annotations de type obligatoires
- **Docstrings** : Format Google ou NumPy

```python
def compute_lambda(debt: float, interest_rate: float, low_entropy_extraction: float) -> float:
    """
    Calcule le paramètre de stabilité Λ = (D * r) / Ė_low.

    Args:
        debt: Dette totale (en unités monétaires)
        interest_rate: Taux d'intérêt moyen (0-1)
        low_entropy_extraction: Taux d'extraction d'énergie (positif)

    Returns:
        Λ. Si Ė_low = 0, retourne inf.

    Raises:
        ValueError: Si l'un des paramètres est négatif.

    References:
        Daghar, M. (2026). The BRI as a Negentropic Bifurcation.
    """
    if debt < 0 or interest_rate < 0 or low_entropy_extraction < 0:
        raise ValueError("Tous les paramètres doivent être positifs")
    if low_entropy_extraction == 0:
        return float('inf')
    return (debt * interest_rate) / low_entropy_extraction
Solidity
Version : ^0.8.0

Style : Suivre les recommandations OpenZeppelin

Tests : Hardhat ou Foundry

solidity
// SPDX-License-Identifier: CC BY-SA 4.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";

contract MonContrat is AccessControl {
    // ...
}
Tests
bash
# Lancer tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=src --cov-report=html

# Test d'un module spécifique
pytest tests/test_core.py -v
🔄 Processus de Pull Request
Checklist avant soumission
□ Les tests passent localement
□ La documentation est mise à jour
□ Le code est formaté (Black)
□ Le linting ne génère pas d'erreurs (Ruff)
□ Les annotations de type sont présentes
□ La licence CC BY-SA 4.0 est respectée
□ Les principes islamiques (riba, Zakat, hisba) sont respectés
Template de Pull Request
markdown
## Description

[Description claire des changements]

## Type de changement

- [ ] Correction de bug
- [ ] Nouvelle fonctionnalité
- [ ] Amélioration de la documentation
- [ ] Refactoring
- [ ] Autre (précisez)

## Tests

- [ ] Tests unitaires ajoutés/modifiés
- [ ] Tous les tests passent

## Checklist

- [ ] Code formaté (Black)
- [ ] Linting OK (Ruff)
- [ ] Annotations de type présentes
- [ ] Documentation mise à jour
- [ ] Licence CC BY-SA 4.0 respectée

## Références

- Issue #...
- Section du white paper...
📚 Principes fondamentaux à respecter
Toute contribution doit respecter les principes suivants :

Principe	Description
Nuqud / Fulus	La distinction étalon/réserve vs monnaie de vélocité
Riba interdit	Pas d'intérêt, pas d'usure, pas de dette perpétuelle
Hisba	L'IA assiste le muhtassib, ne le remplace pas
Zakat	Collectée par l'émir, payable uniquement en nuqud
Logistique réelle	Transactions physiques (stockage, transport, main à main)
Bassira	La perception humaine ne se réduit pas aux équations
📄 Licence
Toute contribution est automatiquement sous CC BY-SA 4.0 avec mention de l'auteur original :

"Daghar, M. (2026). The BRI as a Negentropic Bifurcation: From Entropic Collapse to Yusuf-Grondona Stabilized Economy. CC BY-SA 4.0."

Merci de contribuer à un monde monétaire plus juste !

text

---

## 📄 .zenodo.json

```json
{
    "title": "Yusuf-Grondona Monetary System: A Bimetallic Alternative to Debt-Based Finance",
    "version": "1.0.0",
    "description": "Baseline stable du système monétaire bimétallique Yusuf-Grondona. Modèle multi-agents, IA régulatrice (PPO), blockchain (Fulus ERC-20), DAO, MultiSig, CRD Grondona, Zakat, hisba, corridors BRI, crédits carbone, drones, réalité augmentée.",
    "license": "CC-BY-SA-4.0",
    "creators": [
        {
            "name": "Daghar, Marc",
            "affiliation": "HSE Moscow / Independent Researcher",
            "orcid": "0000-0000-0000-0000"
        }
    ],
    "keywords": [
        "bimetallism",
        "Grondona system",
        "Islamic finance",
        "blockchain",
        "DAO",
        "reinforcement learning",
        "BRI corridor",
        "carbon credit",
        "Muhtassib",
        "Zakat",
        "Hisba",
        "nuqud",
        "fulus",
        "entropy",
        "bifurcation"
    ],
    "access_right": "open",
    "upload_type": "software",
    "communities": [
        {
            "identifier": "economics"
        },
        {
            "identifier": "islamic-finance"
        },
        {
            "identifier": "blockchain"
        }
    ],
    "related_identifiers": [
        {
            "scheme": "url",
            "identifier": "https://github.com/barberoussedine/yusuf-grondona-system",
            "relation": "isSupplementTo"
        }
    ]
}

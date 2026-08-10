#!/usr/bin/env python3
"""
Déploiement complet – Yusuf-Grondona System
===========================================

Déploie tous les contrats sur les différents réseaux.

Usage:
    python deploy_all.py

License: CC BY-SA 4.0 – Marc Daghar
"""

import os
import json
import time
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess

# Ajout du chemin parent pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def deploy_sepolia() -> Dict:
    """Déploie sur Sepolia"""
    print("\n🔷 DÉPLOIEMENT SUR SEPOLIA")
    print("=" * 50)

    from .deploy_sepolia import SepoliaDeployer
    deployer = SepoliaDeployer()
    return deployer.deploy_all()


def deploy_mainnet(network: str = "ethereum") -> Dict:
    """Déploie sur mainnet"""
    print(f"\n🔶 DÉPLOIEMENT SUR {network.upper()}")
    print("=" * 50)

    from .deploy_mainnet import MainnetDeployer
    deployer = MainnetDeployer(network)
    return deployer.deploy_core_contracts()


def deploy_all_contracts(include_mainnet: bool = False) -> Dict:
    """
    Déploie tous les contrats sur tous les réseaux

    Args:
        include_mainnet: Si True, déploie aussi sur mainnet
    """
    results = {
        "sepolia": {},
        "mainnet_ethereum": {},
        "mainnet_bnb": {}
    }

    # 1. Déploiement sur Sepolia
    try:
        results["sepolia"] = deploy_sepolia()
        print("✅ Sepolia: OK")
    except Exception as e:
        print(f"❌ Sepolia: {e}")
        results["sepolia"]["error"] = str(e)

    # 2. Déploiement sur mainnet (si demandé)
    if include_mainnet:
        # Ethereum
        try:
            results["mainnet_ethereum"] = deploy_mainnet("ethereum")
            print("✅ Ethereum mainnet: OK")
        except Exception as e:
            print(f"❌ Ethereum mainnet: {e}")
            results["mainnet_ethereum"]["error"] = str(e)

        # BNB Chain
        try:
            results["mainnet_bnb"] = deploy_mainnet("bnb")
            print("✅ BNB Chain: OK")
        except Exception as e:
            print(f"❌ BNB Chain: {e}")
            results["mainnet_bnb"]["error"] = str(e)

    # Sauvegarde des résultats
    deployment_file = "deployment_summary.json"
    with open(deployment_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "include_mainnet": include_mainnet,
            "results": results
        }, f, indent=2)

    print(f"\n💾 Résumé sauvegardé dans {deployment_file}")

    return results


# ---- Fonction principale ----
def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description="Déploiement complet")
    parser.add_argument("--mainnet", action="store_true",
                       help="Inclure le déploiement sur mainnet")
    parser.add_argument("--network", choices=["sepolia", "ethereum", "bnb"],
                       help="Déployer sur un réseau spécifique")

    args = parser.parse_args()

    try:
        if args.network:
            if args.network == "sepolia":
                deploy_sepolia()
            elif args.network == "ethereum":
                deploy_mainnet("ethereum")
            elif args.network == "bnb":
                deploy_mainnet("bnb")
        else:
            deploy_all_contracts(include_mainnet=args.mainnet)

        print("\n✅ Tous les déploiements sont terminés!")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

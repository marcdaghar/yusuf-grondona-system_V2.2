#!/usr/bin/env python3
"""
Déploiement sur Mainnet – Yusuf-Grondona System
===============================================

Déploie tous les smart contracts sur Ethereum mainnet ou BNB Chain.

⚠️ ATTENTION: Ce script nécessite des fonds réels.
   Utilisez-le uniquement après avoir testé sur Sepolia.

Prérequis :
- Compte Infura ou Alchemy avec un projet mainnet
- Compte avec des ETH/BNB sur mainnet
- Fichier .env avec les variables d'environnement

Usage:
    python deploy_mainnet.py --network ethereum
    python deploy_mainnet.py --network bnb

License: CC BY-SA 4.0 – Marc Daghar
"""

import os
import json
import time
import argparse
from typing import Dict, List, Optional, Any
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
import sys

# Ajout du chemin parent pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Chargement des variables d'environnement
load_dotenv()

# ---- Configuration des réseaux ----
NETWORKS = {
    "ethereum": {
        "rpc_url": os.getenv("ETH_MAINNET_RPC", "https://mainnet.infura.io/v3/demo"),
        "chain_id": 1,
        "gas_price_gwei": 50,
        "explorer": "https://etherscan.io"
    },
    "bnb": {
        "rpc_url": os.getenv("BNB_MAINNET_RPC", "https://bsc-dataseed.binance.org"),
        "chain_id": 56,
        "gas_price_gwei": 5,
        "explorer": "https://bscscan.com"
    }
}

PRIVATE_KEY = os.getenv("MAINNET_DEPLOYER_PRIVATE_KEY")
if not PRIVATE_KEY or PRIVATE_KEY == "0x...":
    print("⚠️  Veuillez configurer MAINNET_DEPLOYER_PRIVATE_KEY dans .env")
    sys.exit(1)


class MainnetDeployer:
    """
    Déploie les contrats sur mainnet
    """

    def __init__(self, network: str = "ethereum"):
        self.network = network
        self.config = NETWORKS.get(network)
        if not self.config:
            raise ValueError(f"Réseau {network} non supporté")

        self.rpc_url = self.config["rpc_url"]
        self.chain_id = self.config["chain_id"]
        self.gas_price_gwei = self.config["gas_price_gwei"]
        self.explorer = self.config["explorer"]

        # Connexion Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if self.network == "bnb":
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.w3.is_connected():
            raise ConnectionError(f"Impossible de se connecter à {network}: {self.rpc_url}")

        self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
        self.address = self.account.address
        self.gas_price = self.w3.to_wei(self.gas_price_gwei, "gwei")

        self.deployed_addresses = {}
        self.total_gas_used = 0

        print(f"🔗 Connecté à {network.upper()} (chain_id: {self.chain_id})")
        print(f"👤 Compte: {self.address}")
        balance = self.w3.eth.get_balance(self.address)
        print(f"💰 Solde: {balance / 10**18:.4f} {network.upper() == 'ETHEREUM' and 'ETH' or 'BNB'}")

        # Vérification du solde
        if balance < self.w3.to_wei(0.1, "ether"):
            print(f"⚠️  Solde faible (< 0.1 {network.upper() == 'ETHEREUM' and 'ETH' or 'BNB'})")
            print("    Assurez-vous d'avoir suffisamment de fonds pour le déploiement")

    def _load_contract_artifacts(self, contract_name: str) -> Dict:
        """
        Charge les artifacts du contrat
        """
        # En production, on chargerait depuis les fichiers compilés
        # Pour cette démo, on retourne des artifacts simulés
        return {
            "abi": [],  # À remplacer par le vrai ABI
            "bytecode": "0x608060405234801561001057600080fd5b506040516..."
        }

    def deploy_contract(self, contract_name: str, *args) -> str:
        """
        Déploie un contrat sur mainnet
        """
        print(f"  📦 Déploiement de {contract_name}...")

        artifacts = self._load_contract_artifacts(contract_name)

        contract = self.w3.eth.contract(
            abi=artifacts["abi"],
            bytecode=artifacts["bytecode"]
        )

        nonce = self.w3.eth.get_transaction_count(self.address)
        tx = contract.constructor(*args).build_transaction({
            "from": self.address,
            "nonce": nonce,
            "gas": 3000000,
            "gasPrice": self.gas_price,
            "chainId": self.chain_id
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print(f"    Transaction: {tx_hash.hex()[:16]}...")
        print(f"    Gas price: {self.gas_price_gwei} Gwei")

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if receipt.status != 1:
            raise Exception(f"Échec du déploiement de {contract_name}")

        gas_used = receipt.gasUsed
        gas_cost = gas_used * self.gas_price
        self.total_gas_used += gas_cost

        contract_address = receipt.contractAddress
        print(f"    ✅ {contract_name} déployé à: {contract_address}")
        print(f"    Gas utilisé: {gas_used} (coût: {gas_cost / 10**18:.6f} ETH)")

        self.deployed_addresses[contract_name] = contract_address
        return contract_address

    def deploy_core_contracts(self) -> Dict:
        """
        Déploie les contrats essentiels
        """
        print("\n🚀 DÉPLOIEMENT SUR MAINNET")
        print("=" * 50)

        # 1. YGDAO Token
        ygdao_addr = self.deploy_contract("YGDAO")
        time.sleep(3)

        # 2. Timelock Controller
        timelock_addr = self.deploy_contract(
            "TimelockController",
            86400,
            [self.address],
            [self.address],
            "0x0000000000000000000000000000000000000000"
        )
        time.sleep(3)

        # 3. YGGovernor
        governor_addr = self.deploy_contract(
            "YGGovernor",
            ygdao_addr,
            timelock_addr
        )
        time.sleep(3)

        # 4. MultiSigCRD
        # Pour mainnet, on utilise 3/5
        owners = [
            self.address,
            "0x" + "2" * 40,  # À remplacer par de vrais propriétaires
            "0x" + "3" * 40,
            "0x" + "4" * 40,
            "0x" + "5" * 40
        ]
        multisig_addr = self.deploy_contract(
            "MultiSigCRD",
            owners,
            3
        )
        time.sleep(3)

        # 5. CarbonCreditToken
        carbon_addr = self.deploy_contract("CarbonCreditToken")
        time.sleep(3)

        # 6. ZakatTracker
        zakat_addr = self.deploy_contract("ZakatTracker")
        time.sleep(3)

        # Sauvegarde
        self._save_deployment()

        print("\n✅ DÉPLOIEMENT TERMINÉ")
        print("=" * 50)
        print(f"Total gas utilisé: {self.total_gas_used / 10**18:.6f} {self.network.upper() == 'ETHEREUM' and 'ETH' or 'BNB'}")

        for name, address in self.deployed_addresses.items():
            print(f"  {name}: {address}")

        return self.deployed_addresses

    def _save_deployment(self):
        """Sauvegarde les adresses déployées"""
        deployment_file = f"deployed_mainnet_{self.network}.json"

        deployment_data = {
            "network": self.network,
            "chain_id": self.chain_id,
            "deployer": self.address,
            "timestamp": time.time(),
            "contracts": self.deployed_addresses,
            "total_gas_used": self.total_gas_used
        }

        with open(deployment_file, "w") as f:
            json.dump(deployment_data, f, indent=2)

        print(f"\n💾 Adresses sauvegardées dans {deployment_file}")


# ---- Fonction principale ----
def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Déploiement sur mainnet")
    parser.add_argument("--network", choices=["ethereum", "bnb"], default="ethereum",
                       help="Réseau cible")
    args = parser.parse_args()

    try:
        deployer = MainnetDeployer(args.network)
        deployer.deploy_core_contracts()

        print("\n📋 Vérifier sur l'explorateur:")
        for name, address in deployer.deployed_addresses.items():
            print(f"  {deployer.explorer}/address/{address}")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

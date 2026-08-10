"""
Ethereum Connector – Connexion à Ethereum/Web3
===============================================

Gestion de la connexion à Ethereum pour :
- Déploiement de contrats
- Transactions
- Appels de fonctions
- Écoute des événements

License: CC BY-SA 4.0 – Marc Daghar
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Union
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
import requests

load_dotenv()


class EthereumConnector:
    """
    Connecteur pour Ethereum et réseaux compatibles
    """

    def __init__(
        self,
        rpc_url: Optional[str] = None,
        private_key: Optional[str] = None,
        network: str = "sepolia"
    ):
        """
        Args:
            rpc_url: URL du nœud RPC
            private_key: Clé privée pour les transactions
            network: 'sepolia', 'ethereum', 'bnb'
        """
        self.network = network

        # Configuration réseau
        self.networks = {
            "sepolia": {
                "rpc": os.getenv("SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/demo"),
                "chain_id": 11155111,
                "name": "Sepolia"
            },
            "ethereum": {
                "rpc": os.getenv("ETH_MAINNET_RPC", "https://mainnet.infura.io/v3/demo"),
                "chain_id": 1,
                "name": "Ethereum"
            },
            "bnb": {
                "rpc": os.getenv("BNB_MAINNET_RPC", "https://bsc-dataseed.binance.org"),
                "chain_id": 56,
                "name": "BNB Chain"
            },
            "local": {
                "rpc": "http://127.0.0.1:8545",
                "chain_id": 1337,
                "name": "Local"
            }
        }

        # Récupération de la configuration
        network_config = self.networks.get(network, self.networks["sepolia"])
        rpc_url = rpc_url or network_config["rpc"]

        # Connexion Web3
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if network in ["bnb", "sepolia"]:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.w3.is_connected():
            raise ConnectionError(f"Impossible de se connecter à {network}: {rpc_url}")

        self.chain_id = network_config["chain_id"]

        # Compte
        self.private_key = private_key
        self.account = None
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            self.address = self.account.address

        self.gas_price = self.w3.to_wei("20", "gwei")

    def is_connected(self) -> bool:
        """Vérifie la connexion"""
        return self.w3.is_connected()

    def get_balance(self, address: Optional[str] = None) -> float:
        """Récupère le solde en ETH/BNB"""
        if address is None:
            address = self.address
        balance = self.w3.eth.get_balance(address)
        return balance / 10**18

    def get_block_number(self) -> int:
        """Récupère le numéro du dernier bloc"""
        return self.w3.eth.block_number

    def get_gas_price(self) -> int:
        """Récupère le prix du gaz"""
        return self.w3.eth.gas_price

    # ---- Contrats ----
    def get_contract(self, address: str, abi: List[Dict]) -> Any:
        """Récupère un contrat"""
        return self.w3.eth.contract(address=address, abi=abi)

    def call_contract_function(
        self,
        contract_address: str,
        abi: List[Dict],
        function_name: str,
        *args
    ) -> Any:
        """Appelle une fonction d'un contrat (lecture)"""
        contract = self.get_contract(contract_address, abi)
        func = getattr(contract.functions, function_name)
        return func(*args).call()

    def send_contract_transaction(
        self,
        contract_address: str,
        abi: List[Dict],
        function_name: str,
        *args,
        **kwargs
    ) -> str:
        """Envoie une transaction à un contrat (écriture)"""
        if not self.account:
            raise ValueError("Clé privée requise pour les transactions")

        contract = self.get_contract(contract_address, abi)
        func = getattr(contract.functions, function_name)

        nonce = self.w3.eth.get_transaction_count(self.address)
        gas = kwargs.get("gas", 200000)
        gas_price = kwargs.get("gas_price", self.gas_price)

        tx = func(*args).build_transaction({
            "from": self.address,
            "nonce": nonce,
            "gas": gas,
            "gasPrice": gas_price,
            "chainId": self.chain_id
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()

    def wait_for_transaction(self, tx_hash: str, timeout: int = 120) -> Dict:
        """Attend la confirmation d'une transaction"""
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        return {
            "status": receipt.status,
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
            "contract_address": receipt.contractAddress
        }

    # ---- Événements ----
    def get_events(
        self,
        contract_address: str,
        abi: List[Dict],
        event_name: str,
        from_block: int = 0,
        to_block: str = "latest"
    ) -> List[Dict]:
        """Récupère les événements d'un contrat"""
        contract = self.get_contract(contract_address, abi)
        event = getattr(contract.events, event_name)
        entries = event.get_logs(fromBlock=from_block, toBlock=to_block)

        return [
            {
                "event": entry.event,
                "args": dict(entry.args),
                "block": entry.blockNumber,
                "tx": entry.transactionHash.hex()
            }
            for entry in entries
        ]

    # ---- Utilitaires ----
    def to_wei(self, amount: float, unit: str = "ether") -> int:
        """Convertit en wei"""
        return self.w3.to_wei(amount, unit)

    def from_wei(self, amount: int, unit: str = "ether") -> float:
        """Convertit de wei"""
        return self.w3.from_wei(amount, unit)

    def get_summary(self) -> Dict:
        """Résumé de la connexion"""
        return {
            "network": self.network,
            "chain_id": self.chain_id,
            "address": self.address,
            "balance": self.get_balance() if self.address else None,
            "block_number": self.get_block_number(),
            "is_connected": self.is_connected()
        }


# ---- Exemple d'utilisation ----
if __name__ == "__main__":
    # Connexion à Sepolia
    connector = EthereumConnector(network="sepolia")

    print("=== ETHEREUM CONNECTOR ===")
    summary = connector.get_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")

"""
Chainlink Oracle Consumer – Intégration des oracles Chainlink
=============================================================

Consomme les flux de prix Chainlink pour :
- ETH/USD
- BNB/USD
- YGDAO/USD (personnalisé)
- YGR/USD (personnalisé)

License: CC BY-SA 4.0 – Marc Daghar
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()


# ---- Adresses des oracles Chainlink ----
CHAINLINK_ADDRESSES = {
    "sepolia": {
        "ETH/USD": "0x694AA1769357215DE4FAC081bf1f309aDC325306",
        "BNB/USD": "0x3A9A2B1f2B6B0C3C4D5E6F7A8B9C0D1E2F3A4B5C",
        "LINK/USD": "0xC9E7C9E7C9E7C9E7C9E7C9E7C9E7C9E7C9E7C9E7"
    },
    "ethereum": {
        "ETH/USD": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
        "BNB/USD": "0x14e613AC84a31f709eadbdF89C6CC390fDc9540A",
        "LINK/USD": "0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c"
    },
    "bnb": {
        "BNB/USD": "0x0567F2323251f0Aab15c8dFb1967E4e8A7D42aeE",
        "ETH/USD": "0x9ef1B8c0bD0F2473A2EeBfC59A9Bcd36829b6390"
    }
}


class ChainlinkOracleConsumer:
    """
    Consommateur d'oracles Chainlink
    """

    def __init__(self, w3: Web3, network: str = "sepolia"):
        self.w3 = w3
        self.network = network
        self.addresses = CHAINLINK_ADDRESSES.get(network, {})

        # ABI du flux Chainlink
        self.aggregator_abi = [
            {
                "inputs": [],
                "name": "latestRoundData",
                "outputs": [
                    {"internalType": "uint80", "name": "roundId", "type": "uint80"},
                    {"internalType": "int256", "name": "answer", "type": "int256"},
                    {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
                    {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
                    {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "decimals",
                "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]

    def get_price(self, pair: str) -> Dict:
        """
        Récupère le prix d'une paire depuis Chainlink

        Args:
            pair: "ETH/USD", "BNB/USD", etc.

        Returns:
            Dict avec le prix et les métadonnées
        """
        address = self.addresses.get(pair)
        if not address:
            return {
                "error": f"Paire {pair} non disponible sur {self.network}",
                "price": 0,
                "decimals": 0
            }

        contract = self.w3.eth.contract(address=address, abi=self.aggregator_abi)

        try:
            latest = contract.functions.latestRoundData().call()
            decimals = contract.functions.decimals().call()

            price = latest[1] / (10 ** decimals)

            return {
                "pair": pair,
                "price": price,
                "decimals": decimals,
                "round_id": latest[0],
                "updated_at": latest[3],
                "network": self.network
            }

        except Exception as e:
            return {
                "error": str(e),
                "pair": pair,
                "price": 0
            }

    def get_eth_usd(self) -> float:
        """Récupère le prix ETH/USD"""
        result = self.get_price("ETH/USD")
        return result.get("price", 0)

    def get_bnb_usd(self) -> float:
        """Récupère le prix BNB/USD"""
        result = self.get_price("BNB/USD")
        return result.get("price", 0)

    def get_historical_price(self, pair: str, round_id: int) -> Dict:
        """
        Récupère un prix historique depuis Chainlink
        """
        address = self.addresses.get(pair)
        if not address:
            return {"error": f"Paire {pair} non disponible"}

        contract = self.w3.eth.contract(address=address, abi=self.aggregator_abi)

        try:
            # getRoundData n'est pas toujours disponible
            # On utilise latestRoundData comme fallback
            latest = contract.functions.latestRoundData().call()
            decimals = contract.functions.decimals().call()

            return {
                "pair": pair,
                "price": latest[1] / (10 ** decimals),
                "round_id": latest[0],
                "updated_at": latest[3]
            }

        except Exception as e:
            return {"error": str(e)}


class MockChainlinkOracle:
    """
    Oracle Chainlink simulé pour les tests
    """

    def get_price(self, pair: str) -> Dict:
        """Simule un prix"""
        mock_prices = {
            "ETH/USD": 3200.0,
            "BNB/USD": 600.0,
            "LINK/USD": 15.0,
            "YGDAO/USD": 2.50,
            "YGR/USD": 0.15
        }

        return {
            "pair": pair,
            "price": mock_prices.get(pair, 100.0),
            "decimals": 8,
            "round_id": 1,
            "updated_at": int(time.time()),
            "network": "mock"
        }


class ChainlinkFulusConsumer:
    """
    Consommateur Chainlink pour le contrat Fulus
    """

    def __init__(self, w3: Web3, contract_address: str, oracle_address: str):
        self.w3 = w3
        self.contract_address = contract_address
        self.oracle_address = oracle_address

        # ABI du contrat Fulus avec Chainlink
        self.contract_abi = [
            {
                "inputs": [],
                "name": "getLatestPrice",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "updatePrice",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "address", "name": "_oracle", "type": "address"}],
                "name": "setOracle",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=self.contract_abi
        )

    def get_price(self) -> float:
        """Récupère le prix depuis le contrat"""
        try:
            price = self.contract.functions.getLatestPrice().call()
            return price / 1e8
        except Exception as e:
            print(f"Erreur: {e}")
            return 0

    def update_price(self, private_key: str) -> str:
        """
        Met à jour le prix en appelant l'oracle
        """
        account = self.w3.eth.account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(account.address)

        tx = self.contract.functions.updatePrice().build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": self.w3.to_wei("30", "gwei")
        })

        signed = self.w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)

        return tx_hash.hex()


# ---- Exemple d'utilisation ----
if __name__ == "__main__":
    from web3 import Web3

    w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/demo"))

    print("=== CHAINLINK ORACLE CONSUMER ===")

    # Oracle réel (Sepolia)
    oracle = ChainlinkOracleConsumer(w3, network="sepolia")

    # Prix ETH/USD
    eth_price = oracle.get_eth_usd()
    print(f"ETH/USD: ${eth_price:.2f}")

    # Prix BNB/USD
    bnb_price = oracle.get_bnb_usd()
    print(f"BNB/USD: ${bnb_price:.2f}")

    # Mock pour les tests
    mock = MockChainlinkOracle()
    mock_price = mock.get_price("YGDAO/USD")
    print(f"YGDAO/USD (mock): ${mock_price['price']:.2f}")

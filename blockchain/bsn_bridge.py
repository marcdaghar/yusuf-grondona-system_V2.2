"""
BSN Bridge – Interopérabilité avec la Blockchain Service Network (Chine)
========================================================================

Bridge entre le système Yusuf-Grondona et le BSN China pour :
- Interopérabilité cross-chain
- Enregistrement des assets
- Transferts entre réseaux

License: CC BY-SA 4.0 – Marc Daghar
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import hashlib


@dataclass
class BSNAsset:
    """Asset enregistré sur le BSN"""
    asset_id: str
    name: str
    symbol: str
    supply: float
    network: str
    registered_at: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)


class BSNBridge:
    """
    Pont vers la Blockchain Service Network (BSN) China
    """

    def __init__(
        self,
        api_key: str,
        api_base_url: str = "https://bsnapi.chinacloud.com",
        network: str = "bsn_china"
    ):
        self.api_key = api_key
        self.base_url = api_base_url
        self.network = network

        self.assets: Dict[str, BSNAsset] = {}
        self.transactions: List[Dict] = []

    def _headers(self) -> Dict:
        """Headers pour les requêtes API"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-BSN-Network": self.network
        }

    def _generate_asset_id(self, name: str, symbol: str) -> str:
        """Génère un ID d'asset unique"""
        return hashlib.sha256(f"{name}{symbol}{time.time()}".encode()).hexdigest()[:16]

    # ---- Gestion des assets ----
    def register_asset(
        self,
        name: str,
        symbol: str,
        initial_supply: float,
        metadata: Optional[Dict] = None
    ) -> BSNAsset:
        """
        Enregistre un asset sur le BSN

        Args:
            name: Nom de l'asset
            symbol: Symbole (ex: FUL, YGDAO)
            initial_supply: Supply initiale
            metadata: Métadonnées supplémentaires

        Returns:
            BSNAsset: L'asset enregistré
        """
        asset_id = self._generate_asset_id(name, symbol)

        # Appel API (simulé)
        payload = {
            "api_key": self.api_key,
            "asset": name,
            "symbol": symbol,
            "supply": initial_supply,
            "type": "interoperable",
            "metadata": metadata or {}
        }

        # En réalité, on appellerait l'API BSN
        # response = requests.post(f"{self.base_url}/api/asset/register", json=payload, headers=self._headers())

        asset = BSNAsset(
            asset_id=asset_id,
            name=name,
            symbol=symbol,
            supply=initial_supply,
            network=self.network,
            metadata=metadata or {}
        )

        self.assets[asset_id] = asset
        return asset

    def get_asset(self, asset_id: str) -> Optional[BSNAsset]:
        """Récupère un asset par son ID"""
        return self.assets.get(asset_id)

    def get_assets(self) -> List[BSNAsset]:
        """Liste tous les assets"""
        return list(self.assets.values())

    # ---- Transferts cross-chain ----
    def send_cross_chain_tx(
        self,
        from_network: str,
        to_network: str,
        asset_id: str,
        amount: float,
        receiver: str,
        memo: Optional[str] = None
    ) -> Dict:
        """
        Envoie une transaction cross-chain

        Args:
            from_network: Réseau source (ex: 'ethereum', 'bsn_china')
            to_network: Réseau destination
            asset_id: ID de l'asset à transférer
            amount: Montant
            receiver: Adresse du destinataire sur le réseau destination
            memo: Note optionnelle

        Returns:
            Dict: Résultat de la transaction
        """
        asset = self.assets.get(asset_id)
        if not asset:
            return {"error": f"Asset {asset_id} non trouvé"}

        if amount > asset.supply:
            return {"error": "Supply insuffisante"}

        # Construction de la transaction
        payload = {
            "api_key": self.api_key,
            "from": from_network,
            "to": to_network,
            "asset": asset_id,
            "amount": amount,
            "receiver": receiver,
            "memo": memo or "",
            "timestamp": time.time()
        }

        # Appel API (simulé)
        # response = requests.post(
        #     f"{self.base_url}/api/crosschain/transfer",
        #     json=payload,
        #     headers=self._headers()
        # )

        # Simulation
        tx_id = hashlib.sha256(json.dumps(payload).encode()).hexdigest()[:16]
        self.transactions.append({
            "tx_id": tx_id,
            **payload
        })

        # Mise à jour du supply
        asset.supply -= amount

        return {
            "tx_id": tx_id,
            "from": from_network,
            "to": to_network,
            "asset": asset.name,
            "amount": amount,
            "receiver": receiver,
            "status": "pending",
            "timestamp": time.time()
        }

    def get_transaction(self, tx_id: str) -> Optional[Dict]:
        """Récupère une transaction par son ID"""
        for tx in self.transactions:
            if tx.get("tx_id") == tx_id:
                return tx
        return None

    def get_transactions(self, limit: int = 10) -> List[Dict]:
        """Récupère les dernières transactions"""
        return self.transactions[-limit:]

    # ---- Interopérabilité ----
    def bridge_status(self) -> Dict:
        """Statut du pont BSN"""
        return {
            "network": self.network,
            "total_assets": len(self.assets),
            "total_transactions": len(self.transactions),
            "assets": [
                {
                    "id": a.asset_id,
                    "name": a.name,
                    "symbol": a.symbol,
                    "supply": a.supply
                }
                for a in self.assets.values()
            ]
        }


class MockBSNBridge(BSNBridge):
    """
    Bridge BSN simulé pour les tests
    """

    def __init__(self):
        super().__init__(api_key="mock_key", api_base_url="https://mock.bsn.com")

    def register_asset(self, name: str, symbol: str, initial_supply: float, metadata=None) -> BSNAsset:
        """Enregistrement simulé"""
        asset_id = self._generate_asset_id(name, symbol)
        asset = BSNAsset(
            asset_id=asset_id,
            name=name,
            symbol=symbol,
            supply=initial_supply,
            network="mock_bsn",
            metadata=metadata or {}
        )
        self.assets[asset_id] = asset
        return asset


# ---- Exemple d'utilisation ----
if __name__ == "__main__":
    print("=== BSN BRIDGE ===")

    # Bridge simulé pour démonstration
    bridge = MockBSNBridge()

    # Enregistrement d'un asset
    asset = bridge.register_asset("Fulus BRI", "FUL", 1000000, {"zone": "Chine"})
    print(f"Asset enregistré: {asset.name} ({asset.symbol}) - Supply: {asset.supply}")

    # Transaction cross-chain
    tx = bridge.send_cross_chain_tx(
        from_network="ethereum",
        to_network="bsn_china",
        asset_id=asset.asset_id,
        amount=1000,
        receiver="0xBSN_RECIPIENT"
    )
    print(f"Transaction: {tx['tx_id']} - {tx['amount']} {tx['asset']}")

    # Statut
    status = bridge.bridge_status()
    print(f"Statut: {status['total_assets']} assets, {status['total_transactions']} transactions")

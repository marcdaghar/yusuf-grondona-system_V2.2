"""
Simulation de blockchain pour la traçabilité
============================================

- Transactions en fulus / nuqud
- Paiements de Zakat
- Preuve de réserve (nuqud)
- Hachage SHA256

License: CC BY-SA 4.0 – Marc Daghar
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Block:
    """Un bloc dans la blockchain"""
    index: int
    timestamp: float
    transactions: List[Dict[str, Any]]
    previous_hash: str
    nonce: int = 0
    hash: str = ""

    def compute_hash(self) -> str:
        """Calcule le hash du bloc"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int = 2) -> None:
        """Mine le bloc (Proof of Work simplifié)"""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.compute_hash()
        print(f"Block {self.index} miné : {self.hash[:16]}...")


class Blockchain:
    """Blockchain simulée"""

    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """Crée le bloc genesis"""
        genesis = Block(0, time.time(), [], "0")
        genesis.mine_block(difficulty=1)
        self.chain.append(genesis)

    def get_latest_block(self) -> Block:
        """Retourne le dernier bloc"""
        return self.chain[-1]

    def add_transaction(self, transaction: Dict[str, Any]) -> None:
        """
        Ajoute une transaction en attente

        Transaction exemple :
        {
            "type": "payment" | "zakat" | "transfer",
            "from": "guilde_X",
            "to": "commercant_Y",
            "amount": 100,
            "currency": "fulus" | "nuqud",
            "zakat_category": "pauvres" (optionnel)
        }
        """
        # Validation minimale
        required_fields = ["type", "amount"]
        for field in required_fields:
            if field not in transaction:
                raise ValueError(f"Transaction manque le champ {field}")

        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address: str = "system") -> Block:
        """
        Mine les transactions en attente
        """
        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions,
            previous_hash=self.get_latest_block().hash
        )
        block.mine_block(self.difficulty)
        self.chain.append(block)
        self.pending_transactions = []
        return block

    def is_chain_valid(self) -> bool:
        """Vérifie l'intégrité de la blockchain"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Vérification du hash
            if current.hash != current.compute_hash():
                return False

            # Vérification du lien
            if current.previous_hash != previous.hash:
                return False

        return True

    def proof_of_reserve(self, nuqud_balance: float, onchain_balance: float) -> Dict[str, Any]:
        """
        Vérifie que les réserves nuqud déclarées correspondent à la blockchain
        """
        diff = abs(nuqud_balance - onchain_balance)
        return {
            "verified": diff < 0.001,
            "offchain_reserve": nuqud_balance,
            "onchain_reserve": onchain_balance,
            "difference": diff
        }

    def get_zakat_history(self, payer: str) -> List[Dict]:
        """Récupère l'historique des paiements de Zakat d'un payeur"""
        zakat_payments = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.get("type") == "zakat" and tx.get("from") == payer:
                    zakat_payments.append(tx)
        return zakat_payments

    def get_transactions_by_type(self, tx_type: str) -> List[Dict]:
        """Récupère les transactions par type"""
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.get("type") == tx_type:
                    transactions.append(tx)
        return transactions

    def get_total_by_currency(self, currency: str) -> float:
        """Calcule le total des transactions par devise"""
        total = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.get("currency") == currency:
                    total += tx.get("amount", 0)
        return total

    def get_summary(self) -> Dict:
        """Résumé de la blockchain"""
        return {
            "total_blocks": len(self.chain),
            "pending_transactions": len(self.pending_transactions),
            "total_transactions": sum(len(b.transactions) for b in self.chain),
            "is_valid": self.is_chain_valid(),
            "total_fulus": self.get_total_by_currency("fulus"),
            "total_nuqud": self.get_total_by_currency("nuqud")
        }


# Exemple d'utilisation
if __name__ == "__main__":
    bc = Blockchain()

    # Ajout de transactions
    bc.add_transaction({
        "type": "payment",
        "from": "guilde_001",
        "to": "commercant_001",
        "amount": 100,
        "currency": "fulus"
    })

    bc.add_transaction({
        "type": "zakat",
        "from": "economy",
        "to": "bayt_al_mal",
        "amount": 25,
        "currency": "nuqud",
        "zakat_category": "pauvres"
    })

    # Minage
    bc.mine_pending_transactions()

    print("=== BLOCKCHAIN ===")
    print(f"Blocs: {len(bc.chain)}")
    print(f"Valide: {bc.is_chain_valid()}")
    print(f"Résumé: {bc.get_summary()}")

    # Historique Zakat
    zakat_history = bc.get_zakat_history("economy")
    print(f"Zakat: {zakat_history}")

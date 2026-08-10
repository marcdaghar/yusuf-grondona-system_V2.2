"""
zk-SNARKs – Preuves à divulgation nulle de connaissance
========================================================

Simulation de zk-SNARKs pour les transactions confidentielles.
En production, utiliser ZoKrates, circom ou snarkjs.

License: CC BY-SA 4.0 – Marc Daghar
"""

import hashlib
import random
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class ZKProof:
    """Une preuve zk-SNARK"""
    commitment: str
    sender_hash: str
    receiver_hash: str
    proof_data: str
    public_inputs: List[str]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        return {
            'commitment': self.commitment,
            'sender_hash': self.sender_hash,
            'receiver_hash': self.receiver_hash,
            'proof_data': self.proof_data,
            'public_inputs': self.public_inputs,
            'timestamp': self.timestamp
        }


class ZKSnarkProof:
    """
    Simulateur de preuves zk-SNARK
    """

    @staticmethod
    def generate_proof(
        sender_pk: str,
        receiver_pk: str,
        amount: float,
        balance: float = 100.0,
        nonce: Optional[int] = None
    ) -> ZKProof:
        """
        Génère une preuve qu'une transaction est valide
        sans révéler les détails.

        Args:
            sender_pk: Clé publique de l'expéditeur
            receiver_pk: Clé publique du destinataire
            amount: Montant de la transaction (masqué)
            balance: Solde du compte (masqué)
            nonce: Nonce aléatoire (optionnel)

        Returns:
            ZKProof: La preuve générée
        """
        if nonce is None:
            nonce = random.randint(1, 2**32)

        # Vérification de la validité (simulée)
        if amount <= 0:
            raise ValueError("Le montant doit être positif")
        if amount > balance:
            raise ValueError("Solde insuffisant")

        # Engagement (hash du montant + nonce)
        commitment = hashlib.sha256(
            f"{amount}{nonce}".encode()
        ).hexdigest()

        # Hash des clés publiques
        sender_hash = hashlib.sha256(
            sender_pk.encode()
        ).hexdigest()[:16]

        receiver_hash = hashlib.sha256(
            receiver_pk.encode()
        ).hexdigest()[:16]

        # Données de la preuve (simulées)
        proof_data = json.dumps({
            'commitment': commitment,
            'sender_hash': sender_hash,
            'receiver_hash': receiver_hash,
            'amount_commitment': hashlib.sha256(str(amount).encode()).hexdigest(),
            'nonce': nonce
        })

        return ZKProof(
            commitment=commitment,
            sender_hash=sender_hash,
            receiver_hash=receiver_hash,
            proof_data=proof_data,
            public_inputs=[commitment, sender_hash, receiver_hash]
        )

    @staticmethod
    def verify_proof(proof: ZKProof) -> bool:
        """
        Vérifie une preuve zk-SNARK

        Args:
            proof: La preuve à vérifier

        Returns:
            bool: True si la preuve est valide
        """
        # Vérification de la structure
        if not proof.commitment or not proof.proof_data:
            return False

        # Vérification que l'engagement est présent
        try:
            data = json.loads(proof.proof_data)
            if data.get('commitment') != proof.commitment:
                return False
            return True
        except:
            return False

    @staticmethod
    def generate_mock_proof() -> ZKProof:
        """Génère une preuve de démonstration"""
        return ZKSnarkProof.generate_proof(
            sender_pk="0xAlice",
            receiver_pk="0xBob",
            amount=10.0,
            balance=100.0
        )


class PrivateTransactionLedger:
    """
    Ledger de transactions privées (masquées)
    """

    def __init__(self):
        self.transactions: List[ZKProof] = []
        self.commitments: List[str] = []

    def add_transaction(self, proof: ZKProof) -> bool:
        """
        Ajoute une transaction privée au ledger

        Args:
            proof: La preuve de la transaction

        Returns:
            bool: True si la transaction a été ajoutée
        """
        if not ZKSnarkProof.verify_proof(proof):
            return False

        # Vérification que l'engagement n'est pas déjà utilisé
        if proof.commitment in self.commitments:
            return False

        self.transactions.append(proof)
        self.commitments.append(proof.commitment)
        return True

    def get_verifiable_sum(self) -> str:
        """
        Calcule une somme vérifiable des transactions
        (sans révéler les montants individuels)
        """
        # Hash cumulatif des engagements
        total_hash = hashlib.sha256()
        for tx in self.transactions:
            total_hash.update(tx.commitment.encode())
        return total_hash.hexdigest()

    def get_transactions(self, limit: int = 10) -> List[Dict]:
        """Retourne les dernières transactions"""
        return [tx.to_dict() for tx in self.transactions[-limit:]]

    def get_count(self) -> int:
        """Nombre de transactions dans le ledger"""
        return len(self.transactions)

    def get_commitments(self) -> List[str]:
        """Liste des engagements"""
        return self.commitments.copy()


# ---- Simulation de preuve réelle (ZoKrates) ----
class RealZkSnark:
    """
    Interface avec ZoKrates pour les preuves réelles
    Nécessite ZoKrates installé
    """

    @staticmethod
    def generate_proof_zokrates(
        amount: int,
        balance: int,
        sender: str,
        receiver: str,
        nonce: int
    ) -> Dict:
        """
        Génère une preuve avec ZoKrates

        Commande:
            zokrates compute-witness -a <amount> <balance> <sender> <receiver> <nonce>
            zokrates generate-proof
        """
        import subprocess

        try:
            # Vérifier que ZoKrates est installé
            subprocess.run(['zokrates', '--version'], capture_output=True, check=True)

            # Génération de la preuve
            result = subprocess.run(
                [
                    'zokrates', 'compute-witness',
                    '-a', str(amount), str(balance), sender, receiver, str(nonce)
                ],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {'error': result.stderr}

            proof = json.loads(result.stdout)

            return {
                'proof': proof,
                'status': 'success'
            }

        except subprocess.CalledProcessError as e:
            return {'error': str(e)}
        except FileNotFoundError:
            return {'error': 'ZoKrates non installé'}

    @staticmethod
    def verify_on_chain(
        proof: Dict,
        commitment: str,
        contract_address: str,
        w3
    ) -> str:
        """
        Vérifie une preuve sur la blockchain

        Args:
            proof: La preuve générée par ZoKrates
            commitment: L'engagement public
            contract_address: Adresse du vérificateur
            w3: Instance Web3

        Returns:
            str: Hash de la transaction
        """
        # ABI du vérificateur ZoKrates
        verifier_abi = [
            {
                "inputs": [
                    {"internalType": "uint256[2]", "name": "a", "type": "uint256[2]"},
                    {"internalType": "uint256[2]", "name": "a_p", "type": "uint256[2]"},
                    {"internalType": "uint256[2]", "name": "b", "type": "uint256[2]"},
                    {"internalType": "uint256[2]", "name": "b_p", "type": "uint256[2]"},
                    {"internalType": "uint256[2]", "name": "c", "type": "uint256[2]"},
                    {"internalType": "uint256[2]", "name": "c_p", "type": "uint256[2]"},
                    {"internalType": "uint256[4]", "name": "input", "type": "uint256[4]"}
                ],
                "name": "verifyTx",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]

        contract = w3.eth.contract(address=contract_address, abi=verifier_abi)

        # Appel de la fonction de vérification
        # (À adapter selon la structure de la preuve)
        tx_hash = contract.functions.verifyTx(
            proof['a'],
            proof['a_p'],
            proof['b'],
            proof['b_p'],
            proof['c'],
            proof['c_p'],
            [int(commitment, 16), 0, 0, 0]
        ).transact()

        return tx_hash.hex()


# ---- Exemple d'utilisation ----
if __name__ == "__main__":
    print("=== ZK-SNARKS – PREUVES CONFIDENTIELLES ===")

    # Génération d'une preuve
    proof = ZKSnarkProof.generate_proof(
        sender_pk="0xAlice",
        receiver_pk="0xBob",
        amount=10.0,
        balance=100.0
    )

    print(f"\nPreuve générée:")
    print(f"  Commitment: {proof.commitment[:32]}...")
    print(f"  Sender hash: {proof.sender_hash}")
    print(f"  Receiver hash: {proof.receiver_hash}")

    # Vérification
    is_valid = ZKSnarkProof.verify_proof(proof)
    print(f"\nPreuve valide: {is_valid}")

    # Ledger privé
    ledger = PrivateTransactionLedger()
    ledger.add_transaction(proof)

    print(f"\nLedger:")
    print(f"  Transactions: {ledger.get_count()}")
    print(f"  Hash vérifiable: {ledger.get_verifiable_sum()[:32]}...")

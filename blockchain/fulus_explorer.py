"""
Fulus Explorer – Explorateur de blocs pour le système Fulus
===========================================================

Style Etherscan pour les transactions en fulus.

License: CC BY-SA 4.0 – Marc Daghar
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any
import time
import json

from .ethereum_connector import EthereumConnector


class FulusExplorer:
    """
    Explorateur de blocs pour le contrat Fulus
    """

    def __init__(self, rpc_url: str, contract_address: str):
        self.connector = EthereumConnector(rpc_url=rpc_url)
        self.contract_address = contract_address

        # ABI minimal du contrat Fulus
        self.abi = [
            {
                "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                    {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
                ],
                "name": "Transfer",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
                    {"indexed": True, "internalType": "address", "name": "spender", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
                ],
                "name": "Approval",
                "type": "event"
            }
        ]

        self.contract = None
        if self.connector.is_connected():
            self.contract = self.connector.get_contract(contract_address, self.abi)

    def get_total_supply(self) -> float:
        """Récupère le total supply"""
        if not self.contract:
            return 0
        try:
            return self.contract.functions.totalSupply().call() / 1e18
        except:
            return 0

    def get_balance(self, address: str) -> float:
        """Récupère le solde d'une adresse"""
        if not self.contract:
            return 0
        try:
            return self.contract.functions.balanceOf(address).call() / 1e18
        except:
            return 0

    def get_events(self, from_block: int = 0, to_block: str = "latest", limit: int = 50) -> pd.DataFrame:
        """Récupère les événements Transfer"""
        if not self.contract:
            return pd.DataFrame()

        try:
            events = self.connector.get_events(
                self.contract_address,
                self.abi,
                "Transfer",
                from_block,
                to_block
            )

            # Limite
            events = events[-limit:]

            return pd.DataFrame([
                {
                    "tx_hash": e["tx"][:16] + "...",
                    "from": e["args"]["from"][:10] + "...",
                    "to": e["args"]["to"][:10] + "...",
                    "value": e["args"]["value"] / 1e18,
                    "block": e["block"]
                }
                for e in events
            ])

        except Exception as e:
            return pd.DataFrame()

    def get_block_range(self, from_block: int, to_block: int) -> pd.DataFrame:
        """Récupère une plage de blocs"""
        blocks = []
        for block_num in range(from_block, to_block + 1):
            try:
                block = self.connector.w3.eth.get_block(block_num)
                blocks.append({
                    "height": block_num,
                    "timestamp": block.timestamp,
                    "transactions": len(block.transactions),
                    "gas_used": block.gasUsed,
                    "size": block.size
                })
            except:
                pass

        return pd.DataFrame(blocks)


# ---- Interface Streamlit ----
def display_explorer():
    """Affiche l'explorateur dans Streamlit"""
    st.set_page_config(page_title="Fulus Explorer", layout="wide")
    st.title("🔍 Fulus Explorer")

    # Configuration
    col1, col2 = st.columns(2)
    with col1:
        rpc_url = st.text_input("RPC URL", "https://sepolia.infura.io/v3/demo")
    with col2:
        contract_addr = st.text_input("Adresse du contrat", "0x...")

    if not contract_addr or contract_addr == "0x...":
        st.info("Entrez l'adresse du contrat pour commencer")
        return

    explorer = FulusExplorer(rpc_url, contract_addr)

    # Métriques
    col1, col2, col3 = st.columns(3)
    with col1:
        total_supply = explorer.get_total_supply()
        st.metric("Offre totale", f"{total_supply:,.2f} FUL")
    with col2:
        block_number = explorer.connector.get_block_number()
        st.metric("Dernier bloc", block_number)
    with col3:
        st.metric("Statut", "✅ Connecté" if explorer.contract else "❌ Non connecté")

    # Recherche de solde
    st.subheader("🔎 Vérifier un solde")
    address = st.text_input("Adresse (0x...)", placeholder="0x...")
    if address:
        balance = explorer.get_balance(address)
        st.success(f"💰 Solde: {balance:.4f} FUL")

    # Dernières transactions
    st.subheader("📜 Dernières transactions")
    df = explorer.get_events(limit=20)
    if not df.empty:
        st.dataframe(df, use_container_width=True)

        # Graphique des volumes
        fig = px.bar(df, x="block", y="value", title="Volumes des transactions")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune transaction récente")

    # Statistiques
    st.subheader("📊 Statistiques")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total transactions", len(df) if not df.empty else 0)
    with col2:
        if not df.empty:
            total_volume = df["value"].sum()
            st.metric("Volume total", f"{total_volume:,.2f} FUL")
    with col3:
        if not df.empty:
            avg_tx = df["value"].mean()
            st.metric("Moyenne par tx", f"{avg_tx:.2f} FUL")


if __name__ == "__main__":
    display_explorer()

"""
Fulus Explorer – Version Streamlit Cloud
========================================

Version déployable sur Streamlit Cloud avec secrets.

License: CC BY-SA 4.0 – Marc Daghar
"""

import streamlit as st
import pandas as pd
import requests
from typing import Dict, List, Optional

from .ethereum_connector import EthereumConnector


def display_cloud_explorer():
    """Version cloud avec secrets"""
    st.set_page_config(
        page_title="Fulus Explorer - Yusuf-Grondona",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🔍 Fulus Explorer")
    st.markdown("Explorateur de blocs pour le système monétaire Yusuf-Grondona")

    # Récupération des secrets
    RPC_URL = st.secrets.get("RPC_URL", "https://sepolia.infura.io/v3/demo")
    CONTRACT_ADDRESS = st.secrets.get("CONTRACT_ADDRESS", "0x...")
    ETHERSCAN_API_KEY = st.secrets.get("ETHERSCAN_API_KEY", "")

    # Sidebar
    with st.sidebar:
        st.header("🌐 Connexion")
        st.info(f"Réseau: Sepolia")
        st.info(f"Contrat: `{CONTRACT_ADDRESS[:10]}...{CONTRACT_ADDRESS[-8:]}`")

        if st.button("🔄 Rafraîchir"):
            st.cache_data.clear()

    # Métriques
    try:
        explorer = FulusExplorer(RPC_URL, CONTRACT_ADDRESS)
        total_supply = explorer.get_total_supply()
        block_number = explorer.connector.get_block_number()

        col1, col2, col3 = st.columns(3)
        col1.metric("Offre totale (FUL)", f"{total_supply:,.2f}")
        col2.metric("Dernier bloc", block_number)
        col3.metric("Réseau", "Sepolia (testnet)")

    except Exception as e:
        st.error(f"Erreur de connexion: {e}")
        return

    # Recherche
    st.subheader("🔎 Rechercher un solde")
    address = st.text_input("Adresse (0x...)", placeholder="0x...")
    if address:
        try:
            balance = explorer.get_balance(address)
            st.success(f"💰 Solde: {balance:.4f} FUL")
        except:
            st.error("Adresse invalide")

    # Transactions via Etherscan API
    st.subheader("📜 Dernières transactions")

    if ETHERSCAN_API_KEY:
        try:
            url = f"https://api-sepolia.etherscan.io/api?module=account&action=tokentx&contractaddress={CONTRACT_ADDRESS}&sort=desc&limit=20&apikey={ETHERSCAN_API_KEY}"
            response = requests.get(url)
            data = response.json()

            if data.get("status") == "1":
                df = pd.DataFrame(data["result"])
                df_display = df[["hash", "from", "to", "value"]].copy()
                df_display["value"] = (df_display["value"].astype(float) / 1e18).round(4)
                df_display.columns = ["Hash", "De", "Vers", "Montant (FUL)"]
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("Aucune transaction récente")
        except Exception as e:
            st.warning(f"Impossible de charger les transactions: {e}")
    else:
        st.info("🔑 API Key Etherscan non configurée")


if __name__ == "__main__":
    display_cloud_explorer()

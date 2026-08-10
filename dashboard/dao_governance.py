"""
DAO Governance – Gouvernance décentralisée
==========================================

Interface de vote et gestion des propositions DAO.

License: CC BY-SA 4.0 – Marc Daghar
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def display_dao_dashboard():
    """Affiche le dashboard DAO"""
    st.subheader("🗳️ Gouvernance DAO – Votes en temps réel")

    # Métriques
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Token YGDAO", "Déployé sur Sepolia")
    with col2:
        st.metric("Propositions", "12")
    with col3:
        st.metric("Taux de participation", "42.5%")

    # Propositions
    st.subheader("📜 Propositions en cours")

    proposals = pd.DataFrame({
        "ID": [1, 2, 3, 4],
        "Description": [
            "Ajustement du taux de change fulus/nuqud",
            "Subvention secteur agricole",
            "Modification des prix CRD du blé",
            "Nomination d'un nouveau muhtassib"
        ],
        "Status": ["🟡 En vote", "🟢 Acceptée", "🔴 Rejetée", "🟡 En vote"],
        "Votes Pour": [125000, 98000, 45000, 72000],
        "Votes Contre": [45000, 32000, 89000, 38000],
        "Quorum": ["85%", "75%", "34%", "65%"]
    })

    st.dataframe(proposals, use_container_width=True)

    # Graphique des votes
    st.subheader("📊 Distribution des votes (Proposition #1)")

    votes_data = pd.DataFrame({
        "Option": ["Pour", "Contre", "Abstention"],
        "Votes": [125000, 45000, 18000]
    })

    fig = px.pie(
        votes_data,
        values="Votes",
        names="Option",
        title="Résultat du vote",
        color_discrete_sequence=["green", "red", "gray"]
    )
    st.plotly_chart(fig, use_container_width=True)

    # Voter
    st.subheader("✍️ Voter")

    proposal_id = st.selectbox(
        "Sélectionner une proposition",
        ["1 - Ajustement du taux de change", "4 - Nomination d'un muhtassib"]
    )

    choice = st.radio("Vote", ["Pour", "Contre", "Abstention"], horizontal=True)

    if st.button("🗳️ Soumettre le vote", type="primary"):
        st.success(f"✅ Vote '{choice}' enregistré pour la proposition sélectionnée")
        st.info("Votre poids de vote: 12,500 YGDAO")
        st.progress(0.42)

    # Historique
    with st.expander("📜 Historique des votes"):
        history = pd.DataFrame({
            "Date": pd.date_range(start="2026-04-01", periods=5, freq="D"),
            "Proposal": [
                "Ajustement CRD",
                "Subvention agriculture",
                "Taux de change",
                "Nomination muhtassib",
                "Budget Zakat"
            ],
            "Vote": ["Pour", "Pour", "Contre", "Pour", "Abstention"],
            "Poids": [12500, 12500, 12500, 12500, 12500]
        })
        st.dataframe(history, use_container_width=True)

    # Staking
    st.subheader("💰 Staking YGDAO")

    col1, col2 = st.columns(2)

    with col1:
        stake_amount = st.number_input("Montant à staker (YGDAO)", min_value=0, value=1000, step=100)
        if st.button("Staker"):
            st.success(f"✅ {stake_amount} YGDAO stakés")

    with col2:
        st.metric("Récompenses accumulées", "125.75 YGR")
        st.metric("Taux APR", "8.5%")


if __name__ == "__main__":
    display_dao_dashboard()

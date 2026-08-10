"""
Admin Dashboard – Interface d'administration
============================================

Gestion des muhtassib, paramètres CRD, DAO, logs système.

License: CC BY-SA 4.0 – Marc Daghar
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Configuration ----
st.set_page_config(
    page_title="Admin – Yusuf-Grondona",
    page_icon="🔧",
    layout="wide"
)

# ---- Authentification simple ----
def check_password():
    """Vérification simple du mot de passe"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        password = st.sidebar.text_input("Mot de passe admin", type="password")
        if password == "admin123":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.warning("Accès réservé aux administrateurs")
            st.stop()
    return True


if not check_password():
    st.stop()

# ---- Titre ----
st.title("🔧 Interface d'administration")
st.markdown("*Gestion des muhtassib, CRD, DAO et logs*")

# ---- Onglets ----
tabs = st.tabs(["👥 Muhtassib", "🏭 CRD", "🗳️ DAO", "📜 Logs"])

# ---- Onglet 1 : Muhtassib ----
with tabs[0]:
    st.subheader("👥 Gestion des muhtassib")

    with st.form("add_muhtassib"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Nom")
        with col2:
            address = st.text_input("Adresse Ethereum", placeholder="0x...")
        with col3:
            zone = st.selectbox("Zone", ["France", "Italie", "Espagne", "Portugal", "NUL"])

        if st.form_submit_button("Ajouter"):
            st.success(f"✅ Muhtassib {name} ajouté")

    # Liste des muhtassib
    muhtassibs = pd.DataFrame({
        "Nom": ["Ahmed", "Fatima", "Omar", "Youssef", "Zaynab"],
        "Adresse": ["0x123...", "0x456...", "0x789...", "0xabc...", "0xdef..."],
        "Zone": ["France", "Italie", "Espagne", "Portugal", "NUL"],
        "Réputation": [85, 92, 67, 78, 54],
        "Inspections": [45, 38, 30, 20, 15]
    })

    st.dataframe(muhtassibs, use_container_width=True)

    # Graphique des réputations
    fig = px.bar(
        muhtassibs,
        x="Nom",
        y="Réputation",
        color="Zone",
        title="Réputation des muhtassib"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- Onglet 2 : CRD ----
with tabs[1]:
    st.subheader("🏭 Paramètres CRD (Grondona)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Blé**")
        wheat_floor = st.number_input("Prix plancher (€/t)", value=180, key="wheat_floor")
        wheat_ceiling = st.number_input("Prix plafond (€/t)", value=220, key="wheat_ceiling")
        wheat_stock = st.number_input("Stock (t)", value=5000, key="wheat_stock")

    with col2:
        st.markdown("**Cuivre**")
        copper_floor = st.number_input("Prix plancher (€/t)", value=8000, key="copper_floor")
        copper_ceiling = st.number_input("Prix plafond (€/t)", value=12000, key="copper_ceiling")
        copper_stock = st.number_input("Stock (t)", value=1000, key="copper_stock")

    if st.button("💾 Mettre à jour les paramètres CRD"):
        st.success("✅ Paramètres CRD mis à jour")

# ---- Onglet 3 : DAO ----
with tabs[2]:
    st.subheader("🗳️ Propositions DAO")

    proposals = pd.DataFrame({
        "ID": [1, 2, 3],
        "Description": [
            "Augmenter le taux de change fulus",
            "Subventionner l'agriculture",
            "Ajuster les prix CRD du cuivre"
        ],
        "Statut": ["En vote", "Acceptée", "Rejetée"],
        "Votes pour": [125000, 98000, 45000],
        "Votes contre": [45000, 32000, 89000]
    })
st.dataframe(proposals, use_container_width=True)

    if st.button("🗳️ Simuler un vote"):
        st.success("Vote enregistré – Poids: 12,500 YGDAO")

# ---- Onglet 4 : Logs ----
with tabs[3]:
    st.subheader("📜 Logs système")

    logs = pd.DataFrame({
        "Timestamp": pd.date_range(start="2026-05-01", periods=10, freq="H"),
        "Niveau": ["INFO", "WARNING", "INFO", "ERROR", "INFO", "INFO", "WARNING", "INFO", "ERROR", "INFO"],
        "Message": [
            "Simulation démarrée",
            "Prix du blé proche du plancher",
            "Transaction enregistrée #1234",
            "Erreur de connexion à l'API",
            "Zakat distribuée",
            "Muhtassib Ahmed en inspection",
            "Retard logistique détecté",
            "CRD a libéré des stocks",
            "Échec de validation du certificat",
            "Système stable"
        ]
    })

    st.dataframe(logs, use_container_width=True)

    if st.button("📥 Exporter les logs"):
        st.info("Logs exportés en CSV")

# ---- Footer ----
st.divider()
st.caption("🔧 Yusuf-Grondona Admin v1.0.0")

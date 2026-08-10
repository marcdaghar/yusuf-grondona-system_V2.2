"""
Plateforme ultime v5 – Tous les modules
=======================================

Version la plus complète avec tous les onglets disponibles.

License: CC BY-SA 4.0 – Marc Daghar
"""

import streamlit as st

from .bri_world_map import display_bri_map
from .esg_metrics import display_esg_metrics
from .dao_governance import display_dao_dashboard
from .iot_integration import display_iot_panel
from .pdf_generator import render_pdf_download_button
from .streamlit_app_with_alerts import generate_mock_data, generate_alerts

# ---- Configuration ----
st.set_page_config(
    page_title="Yusuf-Grondona – Plateforme Ultime v5",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Titre ----
st.title("🏛️ Yusuf-Grondona – Plateforme Ultime v5")
st.markdown("*Tous les modules : ESG, DAO, BRI, IoT, Zakat, Hisba, Certifications, Staking*")

# ---- Onglets ----
tabs = st.tabs([
    "📊 Dashboard",
    "🗺️ BRI Map",
    "🌱 ESG",
    "🗳️ DAO",
    "📡 IoT",
    "📄 PDF",
    "🏅 Certifications",
    "💰 Staking"
])

# ---- Onglet 1 : Dashboard ----
with tabs[0]:
    st.header("📊 Tableau de bord")

    data = generate_mock_data()
    alerts = generate_alerts()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Transactions", data["transactions"])
    col2.metric("Zakat collectée", f"{data['zakat_collected']:.2f} g or")
    col3.metric("Vélocité fulus", data["velocity"])
    col4.metric("Score ESG", f"{data['esg_score']}/100")

    for alert in alerts:
        if alert["type"] == "critical":
            st.error(f"🔴 {alert['message']}")
        elif alert["type"] == "warning":
            st.warning(f"🟡 {alert['message']}")
        else:
            st.info(f"🔵 {alert['message']}")

# ---- Onglet 2 : BRI Map ----
with tabs[1]:
    display_bri_map()

# ---- Onglet 3 : ESG ----
with tabs[2]:
    display_esg_metrics({"esg_global": 68, "unemployment": 7.2})

# ---- Onglet 4 : DAO ----
with tabs[3]:
    display_dao_dashboard()

# ---- Onglet 5 : IoT ----
with tabs[4]:
    display_iot_panel()

# ---- Onglet 6 : PDF ----
with tabs[5]:
    render_pdf_download_button({"esg_scores": {"global": 68}})

# ---- Onglet 7 : Certifications ----
with tabs[6]:
    st.subheader("🏅 Certifications BRI")

    partners = [
        {"name": "Chine", "level": "gold", "status": "✅ Validé"},
        {"name": "Russie", "level": "gold", "status": "✅ Validé"},
        {"name": "Turquie", "level": "silver", "status": "🔄 En cours"},
        {"name": "France", "level": "silver", "status": "✅ Validé"},
    ]

    for p in partners:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{p['name']}**")
        with col2:
            st.write(f"🥇 {p['level'].upper()}")
        with col3:
            st.write(p['status'])

# ---- Onglet 8 : Staking ----
with tabs[7]:
    st.subheader("💰 Staking YGDAO")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("TVL", "$1,250,000", "+5.2%")
    with col2:
        st.metric("APY", "12.5%", "+0.8%")
    with col3:
        st.metric("YGDAO Stakés", "500,000", "+2.1%")

    st.progress(0.42)
    st.caption("42% des YGDAO en circulation sont stakés")

# ---- Footer ----
st.divider()
st.caption("🏛️ Yusuf-Grondona System v1.0.0 – CC BY-SA 4.0")

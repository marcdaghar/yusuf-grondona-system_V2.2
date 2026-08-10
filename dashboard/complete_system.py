"""
Système complet – Point d'entrée unifié
=======================================

Fusionne tous les modules du dashboard en une seule interface.

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
    page_title="Yusuf-Grondona – Système Complet",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Titre ----
st.title("🏛️ Yusuf-Grondona – Système Complet")
st.markdown("*Intégration : ESG, DAO, BRI, IoT, Zakat, Hisba*")

# ---- Sidebar ----
with st.sidebar:
    st.header("📋 Navigation")
    page = st.radio(
        "Aller à",
        ["📊 Tableau de bord", "🗺️ Carte BRI", "🌱 ESG", "🗳️ DAO", "📡 IoT", "📄 Export PDF"]
    )

# ---- Contenu ----
if page == "📊 Tableau de bord":
    st.header("📊 Tableau de bord")

    data = generate_mock_data()
    alerts = generate_alerts()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Transactions", data["transactions"])
    col2.metric("Zakat collectée", f"{data['zakat_collected']:.2f} g or")
    col3.metric("Vélocité fulus", data["velocity"])
    col4.metric("Score ESG", f"{data['esg_score']}/100")

    # Alertes
    for alert in alerts:
        if alert["type"] == "critical":
            st.error(f"🔴 {alert['message']}")
        elif alert["type"] == "warning":
            st.warning(f"🟡 {alert['message']}")
        else:
            st.info(f"🔵 {alert['message']}")

elif page == "🗺️ Carte BRI":
    display_bri_map()

elif page == "🌱 ESG":
    display_esg_metrics({"esg_global": 68, "unemployment": 7.2})

elif page == "🗳️ DAO":
    display_dao_dashboard()

elif page == "📡 IoT":
    display_iot_panel()

elif page == "📄 Export PDF":
    render_pdf_download_button({"esg_scores": {"global": 68}})

# ---- Footer ----
st.divider()
st.caption("🏛️ Yusuf-Grondona System v1.0.0 – CC BY-SA 4.0")

"""
Dashboard principal avec alertes – Yusuf-Grondona System
========================================================

Affiche les indicateurs clés et les alertes du muhtassib.

License: CC BY-SA 4.0 – Marc Daghar
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# ---- Configuration de la page ----
st.set_page_config(
    page_title="Yusuf-Grondona – Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- CSS personnalisé ----
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
        margin-bottom: 0.5rem;
    }
    .alert-critical {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin-bottom: 0.5rem;
    }
    .alert-warning {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin-bottom: 0.5rem;
    }
    .alert-info {
        background: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ---- Simulation des données ----
def generate_mock_data():
    """Génère des données simulées pour le dashboard"""
    return {
        "transactions": random.randint(50, 200),
        "utility": round(random.uniform(70, 95), 1),
        "entropy_loss": round(random.uniform(5, 25), 2),
        "zakat_collected": round(random.uniform(100, 500), 2),
        "velocity": round(random.uniform(2, 8), 2),
        "esg_score": random.randint(55, 85),
        "gini": round(random.uniform(0.25, 0.45), 3),
        "confidence": round(random.uniform(0.5, 0.8), 2),
        "active_shocks": random.randint(0, 2),
        "muhtassib_alerts": random.randint(0, 5)
    }


def generate_alerts():
    """Génère des alertes simulées"""
    alerts = []
    alert_types = [
        {"type": "critical", "message": "Fraude détectée sur la balance du commerçant X"},
        {"type": "warning", "message": "Prix du blé proche du plancher CRD"},
        {"type": "info", "message": "Inspection programmée pour demain"},
        {"type": "critical", "message": "Certificat halal expiré pour le produit Y"},
        {"type": "warning", "message": "Retard logistique sur la route Chine-NUL"},
        {"type": "info", "message": "Zakat distribuée à 45 bénéficiaires"}
    ]

    n_alerts = random.randint(1, 4)
    return random.sample(alert_types, n_alerts)


# ---- Titre ----
st.markdown('<div class="main-header">🏛️ Yusuf-Grondona – Système monétaire</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Bassira & ‘alam al‑mithāl – Économie réelle, logistique, nuqud/fulus, Zakat, hisba</div>', unsafe_allow_html=True)

# ---- Sidebar ----
with st.sidebar:
    st.header("⚙️ Contrôle")

    # Simulation
    if st.button("🔄 Rafraîchir les données"):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # Paramètres de simulation
    st.subheader("Paramètres")
    years = st.number_input("Années à simuler", min_value=1, max_value=10, value=1)
    use_crd = st.checkbox("Activer CRD (Grondona)", value=True)
    use_zakat = st.checkbox("Activer Zakat", value=True)
    use_bri = st.checkbox("Activer réseau BRI", value=True)

    if st.button("▶️ Lancer simulation", type="primary"):
        with st.spinner("Simulation en cours..."):
            time.sleep(2)
            st.success("✅ Simulation terminée")
            st.session_state["simulation_run"] = True

    st.divider()

    # Informations
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")
    st.caption("🔗 API : http://localhost:8000")
    st.caption("📄 Licence CC BY-SA 4.0")

# ---- Simulation des données ----
if "simulation_run" not in st.session_state:
    st.session_state["simulation_run"] = False

if st.session_state["simulation_run"]:
    data = generate_mock_data()
    alerts = generate_alerts()
else:
    data = generate_mock_data()
    alerts = generate_alerts()

# ---- Métriques principales ----
st.subheader("📊 Indicateurs clés")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Transactions", data["transactions"], delta=f"+{random.randint(5, 20)}%")
with col2:
    st.metric("Utilité consommateur", data["utility"], delta=f"+{random.randint(1, 5)}%")
with col3:
    st.metric("Entropie (perte €)", data["entropy_loss"], delta=f"-{random.randint(1, 10)}%")
with col4:
    st.metric("Zakat collectée", f"{data['zakat_collected']:.2f} g or", delta=f"+{random.randint(0, 50)}")
with col5:
    st.metric("Vélocité fulus", data["velocity"], delta=f"+{random.randint(0, 3)}")

# ---- Deuxième ligne de métriques ----
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Score ESG", f"{data['esg_score']}/100", delta=f"{random.randint(-5, 5)}")
with col2:
    st.metric("Coefficient de Gini", data["gini"], delta=f"{random.uniform(-0.02, 0.02):.3f}")
with col3:
    st.metric("Confiance sociale", f"{data['confidence']:.0%}", delta=f"{random.uniform(-5, 5):.0%}")
with col4:
    st.metric("Chocs actifs", data["active_shocks"], delta=f"{random.randint(-1, 1)}")

# ---- Graphiques ----
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Évolution de la vélocité")
    # Données simulées
    months = list(range(1, 13))
    velocity_data = [random.uniform(2, 8) for _ in range(12)]

    fig = px.line(
        x=months, y=velocity_data,
        labels={"x": "Mois", "y": "Vélocité (tours/an)"},
        title="Vélocité du fulus",
        markers=True
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Répartition de la Zakat")
    categories = ["Pauvres", "Indigents", "Endettés", "Voyageurs", "Collecteurs", "Autres"]
    values = [random.randint(10, 40) for _ in range(6)]

    fig = px.pie(
        values=values, names=categories,
        title="Distribution de la Zakat",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# ---- Alertes du muhtassib ----
st.subheader("🧑‍⚖️ Alertes du muhtassib")

if alerts:
    for alert in alerts:
        if alert["type"] == "critical":
            st.markdown(f'<div class="alert-critical">🔴 {alert["message"]}</div>', unsafe_allow_html=True)
        elif alert["type"] == "warning":
            st.markdown(f'<div class="alert-warning">🟡 {alert["message"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-info">🔵 {alert["message"]}</div>', unsafe_allow_html=True)
else:
    st.success("✅ Aucune alerte active")

# ---- Chocs logistiques ----
st.subheader("🚢 Événements logistiques")

if data["active_shocks"] > 0:
    shocks = ["Port de Beyrouth – retard", "Route Chine-NUL – fermeture"]
    for shock in shocks[:data["active_shocks"]]:
        st.warning(f"⚠️ {shock}")
else:
    st.success("✅ Aucun choc logistique actif")

# ---- Footer ----
st.divider()
st.caption(f"🏛️ Yusuf-Grondona System v1.0.0 – {datetime.now().strftime('%Y-%m-%d %H:%M')}")

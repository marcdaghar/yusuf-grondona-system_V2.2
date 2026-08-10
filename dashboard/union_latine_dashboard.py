"""
Union Latine Dashboard – France, Italie, Espagne, Portugal
==========================================================

Dashboard spécifique à l'Union Latine dans le corridor BRI.

License: CC BY-SA 4.0 – Marc Daghar
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.core.bri_network import ZoneBRI, create_default_network


# ---- Configuration ----
st.set_page_config(
    page_title="Union Latine – Dashboard",
    page_icon="🇪🇺",
    layout="wide"
)

# ---- Titre ----
st.title("🇪🇺 Union Latine – Dashboard économique")
st.markdown("*Intégration monétaire et commerciale avec le corridor BRI*")

# ---- Initialisation des zones ----
@st.cache_resource
def init_union_latine():
    """Initialise les zones de l'Union Latine"""
    zones = {
        "France": ZoneBRI("France", "Paris", 4000, 0, 10.0, region="Europe"),
        "Italie": ZoneBRI("Italie", "Rome", 3000, 0, 10.0, region="Europe"),
        "Espagne": ZoneBRI("Espagne", "Madrid", 2500, 0, 10.0, region="Europe"),
        "Portugal": ZoneBRI("Portugal", "Lisbonne", 1500, 0, 10.0, region="Europe"),
    }

    # Ajout de données simulées
    for zone in zones.values():
        zone.fulus_supply = 10000 + random.randint(-2000, 5000)
        zone.nuqud_reserve_grams = zone.nuqud_reserve_grams + random.randint(-500, 500)

    return zones


import random

zones = init_union_latine()

# ---- Métriques ----
st.subheader("📊 Situation des zones")

col1, col2, col3, col4 = st.columns(4)
for i, (name, zone) in enumerate(zones.items()):
    with [col1, col2, col3, col4][i]:
        st.metric(
            name,
            f"{zone.fulus_supply:,.0f} FUL",
            delta=f"{zone.nuqud_reserve_grams:.0f} g or"
        )

# ---- Graphique des réserves ----
st.subheader("🏦 Réserves en nuqud (or/argent)")

reserve_data = pd.DataFrame([
    {"Pays": name, "Réserves (g or)": zone.nuqud_reserve_grams}
    for name, zone in zones.items()
])

fig = px.bar(
    reserve_data,
    x="Pays",
    y="Réserves (g or)",
    color="Pays",
    title="Réserves de change bimétalliques"
)
st.plotly_chart(fig, use_container_width=True)

# ---- Flux commerciaux ----
st.subheader("🚢 Flux commerciaux simulés")

if st.button("Simuler un échange France → Chine"):
    st.success("Transaction réalisée: Machines – 500 g or")
    st.json({
        "from": "France",
        "to": "Chine",
        "goods": "machines",
        "price_nuqud": 500,
        "settled": "in_nuqud"
    })

# ---- Dernières transactions ----
st.subheader("📦 Dernières transactions")

exchange_data = []
for zone_name, zone in zones.items():
    # Simulation de transactions
    for _ in range(random.randint(0, 3)):
        exchange_data.append({
            "Zone": zone_name,
            "Avec": random.choice(["Chine", "Russie", "Turquie", "NUL"]),
            "Montant (g or)": round(random.uniform(10, 200), 1),
            "Date": pd.Timestamp.now() - pd.Timedelta(days=random.randint(0, 30))
        })

if exchange_data:
    df = pd.DataFrame(exchange_data)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Aucune transaction inter-zone récente")

# ---- Footer ----
st.divider()
st.caption("🏛️ Yusuf-Grondona System – Union Latine v1.0.0")

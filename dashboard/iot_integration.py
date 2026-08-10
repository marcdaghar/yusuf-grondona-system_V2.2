"""
IoT Integration – Capteurs et logistique en temps réel
=======================================================

Intégration des données IoT pour la logistique.

License: CC BY-SA 4.0 – Marc Daghar
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import time
import random


def generate_iot_data():
    """Génère des données IoT simulées"""
    warehouses = ["Entrepôt Nord", "Entrepôt Sud", "Entrepôt Centre", "Port de Beyrouth"]

    data = []
    for wh in warehouses:
        data.append({
            "warehouse": wh,
            "temperature": round(random.uniform(15, 30), 1),
            "humidity": round(random.uniform(40, 80), 1),
            "stock": round(random.uniform(100, 1000), 0),
            "co2": round(random.uniform(400, 800), 0),
            "status": random.choice(["✅ Normal", "⚠️ Attention", "🔴 Critique"])
        })

    return pd.DataFrame(data)


def display_iot_panel():
    """Affiche le panel IoT"""
    st.subheader("📡 Capteurs IoT – Logistique en temps réel")

    # Métriques
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Entropie logistique", round(random.uniform(0.1, 0.5), 3), delta="-0.02")
    with col2:
        st.metric("Délai moyen", f"{random.randint(2, 8)} jours", delta="-1 jour")
    with col3:
        st.metric("Capteurs actifs", f"{random.randint(12, 25)}", delta="+2")

    # Données des entrepôts
    df = generate_iot_data()

    # Tableau
    st.dataframe(df, use_container_width=True)

    # Graphique des températures
    fig = px.bar(
        df,
        x="warehouse",
        y="temperature",
        color="status",
        title="Température par entrepôt",
        labels={"temperature": "Température (°C)"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Simulation MQTT
    if st.button("🔄 Simuler envoi MQTT"):
        with st.spinner("Envoi des données..."):
            time.sleep(1)
            st.success("✅ Données envoyées vers test.mosquitto.org/yusuf/warehouse")

    # Dernières données reçues
    with st.expander("📡 Dernières données reçues"):
        last_data = pd.DataFrame({
            "Timestamp": pd.date_range(start="2026-05-01", periods=5, freq="min"),
            "Entrepôt": ["Entrepôt Nord", "Entrepôt Sud", "Entrepôt Centre", "Port de Beyrouth", "Entrepôt Nord"],
            "Température": [22.5, 25.3, 20.1, 18.7, 23.0],
            "Humidité": [55, 62, 48, 71, 58],
            "Stock (t)": [450, 320, 780, 150, 420]
        })
        st.dataframe(last_data, use_container_width=True)

    # Configuration MQTT
    st.subheader("⚙️ Configuration MQTT")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Broker", "test.mosquitto.org")
        st.text_input("Port", "1883")

    with col2:
        st.text_input("Topic", "yusuf/warehouse/+")
        st.text_input("Client ID", "dashboard_" + str(random.randint(1000, 9999)))

    if st.button("🔗 Connecter"):
        st.success("✅ Connecté au broker MQTT")

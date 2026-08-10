"""
BRI World Map – Carte 3D et flux commerciaux
=============================================

Visualisation interactive des flux commerciaux du corridor BRI.

License: CC BY-SA 4.0 – Marc Daghar
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


class BRIWorldMap:
    """Carte mondiale du réseau BRI"""

    def __init__(self):
        # Coordonnées des zones
        self.zones = {
            "Chine": {"lat": 35.0, "lon": 105.0, "color": "red"},
            "Russie": {"lat": 60.0, "lon": 90.0, "color": "darkred"},
            "NUL": {"lat": 33.9, "lon": 35.5, "color": "orange"},
            "Turquie": {"lat": 39.0, "lon": 35.0, "color": "orange"},
            "France": {"lat": 46.5, "lon": 2.5, "color": "blue"},
            "Italie": {"lat": 42.5, "lon": 12.5, "color": "blue"},
            "Espagne": {"lat": 40.5, "lon": -3.7, "color": "blue"},
            "Portugal": {"lat": 39.5, "lon": -8.0, "color": "blue"},
            "Émirat": {"lat": 24.0, "lon": 54.0, "color": "gold"},
            "Indonésie": {"lat": -0.8, "lon": 113.0, "color": "green"},
            "Inde": {"lat": 21.0, "lon": 78.0, "color": "orange"},
            "Égypte": {"lat": 26.0, "lon": 30.0, "color": "gold"}
        }

        # Flux commerciaux
        self.flows = [
            {"from": "Chine", "to": "France", "value": 5000, "goods": "machines"},
            {"from": "Chine", "to": "Italie", "value": 3500, "goods": "électronique"},
            {"from": "Chine", "to": "NUL", "value": 2000, "goods": "matériaux"},
            {"from": "Russie", "to": "France", "value": 2500, "goods": "énergie"},
            {"from": "Turquie", "to": "France", "value": 1500, "goods": "textiles"},
            {"from": "Émirat", "to": "France", "value": 1200, "goods": "pétrole"},
            {"from": "Chine", "to": "Espagne", "value": 2800, "goods": "machines"},
            {"from": "Russie", "to": "Italie", "value": 1800, "goods": "gaz"},
            {"from": "Inde", "to": "France", "value": 2000, "goods": "pharmaceutique"},
            {"from": "Égypte", "to": "NUL", "value": 800, "goods": "céréales"},
        ]

    def create_globe_map(self):
        """Crée la carte 3D globe"""
        fig = go.Figure()

        # Ajout des zones
        for zone, info in self.zones.items():
            fig.add_trace(go.Scattergeo(
                lon=[info["lon"]],
                lat=[info["lat"]],
                mode='markers+text',
                marker=dict(size=20, color=info["color"], symbol='circle'),
                text=zone,
                textposition="top center",
                name=zone,
                hovertemplate=f"{zone}<br>Lat: {info['lat']:.1f}<br>Lon: {info['lon']:.1f}<extra></extra>"
            ))

        # Ajout des flux
        for flow in self.flows:
            from_zone = self.zones.get(flow["from"])
            to_zone = self.zones.get(flow["to"])

            if from_zone and to_zone:
                fig.add_trace(go.Scattergeo(
                    lon=[from_zone["lon"], to_zone["lon"]],
                    lat=[from_zone["lat"], to_zone["lat"]],
                    mode='lines',
                    line=dict(width=flow["value"]/500 + 1, color='gold'),
                    opacity=0.6,
                    name=f"{flow['from']} → {flow['to']}",
                    hovertemplate=f"{flow['from']} → {flow['to']}<br>{flow['goods']}<br>{flow['value']} t<extra></extra>"
                ))

        fig.update_layout(
            title="Flux commerciaux BRI",
            geo=dict(
                projection_type="natural earth",
                showland=True,
                landcolor="lightgray",
                countrycolor="black",
                coastlinecolor="black",
                showocean=True,
                oceancolor="lightblue",
                showcountries=True,
                showframe=False
            ),
            height=700,
            showlegend=True
        )

        return fig

    def create_sankey(self):
        """Crée un diagramme Sankey des flux"""
        nodes = list(self.zones.keys())
        node_indices = {node: i for i, node in enumerate(nodes)}

        sources = [node_indices[flow["from"]] for flow in self.flows]
        targets = [node_indices[flow["to"]] for flow in self.flows]
        values = [flow["value"] for flow in self.flows]

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=nodes,
                color=["red", "darkred", "orange", "orange", "blue", "blue", "blue", "blue", "gold", "green", "orange", "gold"]
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                label=[f"{f['goods']}" for f in self.flows]
            )
        )])

        fig.update_layout(title="Diagramme des flux commerciaux BRI", height=500)
        return fig


def display_bri_map():
    """Affiche la carte BRI dans Streamlit"""
    st.subheader("🗺️ Carte BRI – Flux commerciaux")

    bri_map = BRIWorldMap()

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = bri_map.create_globe_map()
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig_sankey = bri_map.create_sankey()
        st.plotly_chart(fig_sankey, use_container_width=True)

    # Statistiques
    st.subheader("📊 Top des corridors commerciaux")

    flow_df = pd.DataFrame(bri_map.flows)
    top_corridors = flow_df.groupby(["from", "to"])["value"].sum().reset_index()
    top_corridors = top_corridors.sort_values("value", ascending=False)

    st.dataframe(top_corridors, use_container_width=True)

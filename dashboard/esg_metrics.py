"""
ESG Metrics – Indicateurs Environnementaux, Sociaux, de Gouvernance
===================================================================

Calcul et affichage des scores ESG.

License: CC BY-SA 4.0 – Marc Daghar
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np


class ESGCalculator:
    """Calculateur de scores ESG"""

    def __init__(self, economy_data):
        self.data = economy_data

    def environmental_score(self) -> float:
        """Score Environnemental (0-100)"""
        logistics_entropy = self.data.get("logistics_entropy", 0.5)
        carbon_footprint = self.data.get("carbon_footprint", 100)
        renewables = self.data.get("renewables_share", 0.3)

        score = 100 * (1 - logistics_entropy / 2) * (1 - carbon_footprint / 200) * (0.5 + 0.5 * renewables)
        return max(0, min(100, score))

    def social_score(self) -> float:
        """Score Social (0-100)"""
        unemployment = self.data.get("unemployment", 0.08)
        gini = self.data.get("gini_index", 0.35)
        zakat = self.data.get("zakat_distributed", 0)

        score = 100 * (1 - unemployment) * (1 - gini) * (1 + zakat / 1000)
        return max(0, min(100, score))

    def governance_score(self) -> float:
        """Score de Gouvernance (0-100)"""
        corruption = self.data.get("corruption_index", 0.2)
        hisba = self.data.get("hisba_compliance", 0.8)
        blockchain = self.data.get("blockchain_audit", 1.0)

        score = 100 * (1 - corruption) * hisba * blockchain
        return max(0, min(100, score))

    def aggregate(self) -> dict:
        """Score ESG agrégé"""
        return {
            "Environmental": self.environmental_score(),
            "Social": self.social_score(),
            "Governance": self.governance_score(),
            "Global": (self.environmental_score() + self.social_score() + self.governance_score()) / 3
        }


def display_esg_metrics(economy_data):
    """Affiche les métriques ESG dans Streamlit"""
    st.subheader("🌱 Indicateurs ESG")

    calc = ESGCalculator(economy_data)
    scores = calc.aggregate()

    # Métriques
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🌍 Environmental", f"{scores['Environmental']:.0f}/100")
    with col2:
        st.metric("👥 Social", f"{scores['Social']:.0f}/100")
    with col3:
        st.metric("⚖️ Governance", f"{scores['Governance']:.0f}/100")
    with col4:
        st.metric("🏆 ESG Global", f"{scores['Global']:.0f}/100")

    # Jauge de progrès
    st.progress(scores['Global'] / 100)

    # Détails
    with st.expander("📊 Détails des scores"):
        st.write("**Environmental** : Entropie logistique, empreinte carbone, part des renouvelables")
        st.write("**Social** : Chômage, inégalités (Gini), Zakat distribuée")
        st.write("**Governance** : Transparence, conformité hisba, auditabilité blockchain")

    # Graphique radar
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[scores['Environmental'], scores['Social'], scores['Governance']],
        theta=['Environmental', 'Social', 'Governance'],
        fill='toself',
        name='Score ESG',
        line=dict(color='green', width=2)
    ))

    fig.add_trace(go.Scatterpolar(
        r=[50, 50, 50],
        theta=['Environmental', 'Social', 'Governance'],
        fill='none',
        name='Référence (50)',
        line=dict(color='gray', width=1, dash='dash')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title="Profil ESG",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Évolution simulée
    st.subheader("📈 Évolution des scores ESG")

    dates = pd.date_range(start="2020-01-01", periods=24, freq="M")
    data = {
        "date": dates,
        "Environmental": 50 + np.cumsum(np.random.normal(0, 2, 24)),
        "Social": 50 + np.cumsum(np.random.normal(0, 1.5, 24)),
        "Governance": 50 + np.cumsum(np.random.normal(0, 1, 24))
    }
    df = pd.DataFrame(data)
    df = df.clip(0, 100)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df["date"], y=df["Environmental"], name="Environmental", line=dict(color="green")))
    fig2.add_trace(go.Scatter(x=df["date"], y=df["Social"], name="Social", line=dict(color="blue")))
    fig2.add_trace(go.Scatter(x=df["date"], y=df["Governance"], name="Governance", line=dict(color="orange")))

    fig2.update_layout(
        title="Évolution des scores ESG (2020-2022)",
        xaxis_title="Date",
        yaxis_title="Score",
        height=300
    )

    st.plotly_chart(fig2, use_container_width=True)

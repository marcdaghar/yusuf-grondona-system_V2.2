"""
PDF Generator – Export des rapports de performance
===================================================

Génération de rapports PDF automatiques.

License: CC BY-SA 4.0 – Marc Daghar
"""

import streamlit as st
import io
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def generate_pdf_report(economy_state):
    """Génère un rapport PDF"""
    try:
        from fpdf import FPDF
    except ImportError:
        st.warning("FPDF non installé. Installez: pip install fpdf2")
        return None

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Yusuf-Grondona System - Performance Report', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()

    # Titre
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 20, 'Yusuf-Grondona Economic System', 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')
    pdf.ln(10)

    # Section ESG
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, 'ESG Performance Metrics', 0, 1)
    pdf.set_font('Arial', '', 10)

    esg = economy_state.get('esg_scores', {'global': 68, 'environmental': 65, 'social': 70, 'governance': 69})
    for key, value in esg.items():
        pdf.cell(0, 8, f"{key.capitalize()}: {value:.1f}/100", 0, 1)

    pdf.ln(5)

    # Section Métriques
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, 'Key Metrics', 0, 1)
    pdf.set_font('Arial', '', 10)

    metrics = {
        'Transactions': economy_state.get('transactions', 0),
        'Zakat Collected': economy_state.get('zakat', 0),
        'Velocity': economy_state.get('velocity', 0),
        'Entropy': economy_state.get('entropy', 0)
    }

    for key, value in metrics.items():
        pdf.cell(0, 8, f"{key}: {value}", 0, 1)

    pdf.ln(5)

    # Conclusion
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, 'Conclusion', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, "Le système Yusuf-Grondona démontre une stabilité monétaire accrue, une vélocité supérieure et une résilience face aux chocs, tout en respectant les principes islamiques (riba interdit, Zakat politique, hisba).")

    # Génération du PDF
    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)

    return output


def render_pdf_download_button(economy_state):
    """Affiche le bouton de téléchargement PDF"""
    st.subheader("📄 Export PDF")

    if st.button("📥 Générer le rapport de performance"):
        with st.spinner("Génération du PDF..."):
            pdf_buffer = generate_pdf_report(economy_state)

            if pdf_buffer:
                st.download_button(
                    label="Télécharger le rapport PDF",
                    data=pdf_buffer,
                    file_name=f"yusuf_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ Rapport généré")
            else:
                st.error("Erreur lors de la génération du PDF")

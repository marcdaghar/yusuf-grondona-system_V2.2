"""
Yusuf-Grondona Monetary System – Dashboard Module
=================================================

Ce module contient les interfaces Streamlit pour le système :
- streamlit_app_with_alerts.py : Dashboard principal avec alertes
- complete_system.py : Point d'entrée unifié
- ultimate_platform_v5.py : Plateforme ultime avec tous les modules
- union_latine_dashboard.py : Dashboard Union Latine
- admin_dashboard.py : Interface d'administration
- bri_world_map.py : Carte BRI 3D interactive
- esg_metrics.py : Indicateurs ESG
- dao_governance.py : Gouvernance DAO
- iot_integration.py : IoT temps réel
- pdf_generator.py : Export PDF

License: CC BY-SA 4.0 – Marc Daghar
"""

from .streamlit_app_with_alerts import main as main_with_alerts
from .complete_system import main as main_complete
from .ultimate_platform_v5 import main as main_ultimate

__all__ = [
    'main_with_alerts',
    'main_complete',
    'main_ultimate',
]

__version__ = '1.0.0'

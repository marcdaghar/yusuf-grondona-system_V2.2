"""
Yusuf-Grondona Monetary System – API Module
===========================================

Ce module contient l'API REST FastAPI avec tous les endpoints :
- main.py : API principale (simulation, transferts, métriques)
- main_light.py : Version allégée sans dépendances lourdes
- auth.py : Authentification JWT + API Key
- metrics.py : Endpoint Prometheus
- public_api.py : API publique pour partenaires BRI
- mobile_api.py : API pour application mobile (muhtassib)
- ar_inspection.py : Réalité augmentée pour inspections
- webhooks.py : Webhooks pour partenaires
- websocket_manager.py : Communication temps réel
- certificate_monitor.py : Monitoring des certificats

License: CC BY-SA 4.0 – Marc Daghar
"""

from .auth import authenticate_user, create_access_token, get_current_user
from .main import app as main_app
from .public_api import app as public_app

__all__ = [
    'authenticate_user',
    'create_access_token',
    'get_current_user',
    'main_app',
    'public_app',
]

__version__ = '1.0.0'

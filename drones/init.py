"""
Yusuf-Grondona Monetary System – Drones Module
==============================================

Ce module contient le contrôleur de drones pour la surveillance des corridors BRI.

License: CC BY-SA 4.0 – Marc Daghar
"""

from .drone_controller import Drone, DroneFleetManager, DroneWebSocketServer

__all__ = [
    'Drone',
    'DroneFleetManager',
    'DroneWebSocketServer',
]

__version__ = '1.0.0'

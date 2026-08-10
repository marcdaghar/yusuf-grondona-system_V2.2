"""
Yusuf-Grondona SDK – Python
===========================

SDK officiel pour l'intégration des partenaires BRI au système Yusuf-Grondona.

Installation:
    pip install yusuf-grondona-sdk

Usage:
    from yusuf_sdk import YusufGrondonaSDK

    sdk = YusufGrondonaSDK(api_key="your_api_key")
    rate = sdk.get_exchange_rate("Chine", "France", 1000)

License: CC BY-SA 4.0 – Marc Daghar
"""

from .yusuf_sdk import YusufGrondonaSDK, YusufClient

__all__ = [
    'YusufGrondonaSDK',
    'YusufClient',
]

__version__ = '1.0.0'

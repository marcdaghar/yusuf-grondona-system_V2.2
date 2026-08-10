"""
Yusuf-Grondona SDK – Client Python
==================================

Client officiel pour l'API du système Yusuf-Grondona.

License: CC BY-SA 4.0 – Marc Daghar
"""

import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import json
import time


class YusufGrondonaSDK:
    """
    SDK pour l'API Yusuf-Grondona

    Args:
        api_key: Clé API pour l'authentification
        base_url: URL de base de l'API (par défaut: https://api.yusuf-grondona.com)
        timeout: Timeout des requêtes en secondes
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.yusuf-grondona.com",
        timeout: int = 30
    ):
        self.api_key = api_key
      
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Yusuf-Grondona-SDK/1.0.0"
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Effectue une requête HTTP
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "failed",
                "message": "Request failed"
            }

    # ---- Endpoints publics ----

    def health_check(self) -> Dict:
        """
        Vérifie la disponibilité de l'API

        Returns:
            Dict: Statut de l'API
        """
        return self._request("GET", "/api/v1/health")

    def get_exchange_rate(
        self,
        from_zone: str,
        to_zone: str,
        amount: float
    ) -> Dict:
        """
        Obtient le taux de change entre deux zones BRI

        Args:
            from_zone: Zone source (ex: "Chine")
            to_zone: Zone destination (ex: "France")
            amount: Montant en fulus

        Returns:
            Dict: Taux de change et montant converti
        """
        return self._request(
            "POST",
            "/api/v1/exchange_rate",
            data={
                "from_zone": from_zone,
                "to_zone": to_zone,
                "amount_fulus": amount
            }
        )

    def get_esg_score(self, partner_id: str, year: int = 2026) -> Dict:
        """
        Récupère le score ESG d'un partenaire BRI

        Args:
            partner_id: ID du partenaire (ex: "Chine")
            year: Année du rapport

        Returns:
            Dict: Score ESG et détails
        """
        return self._request(
            "GET",
            f"/api/v1/esg/{partner_id}",
            params={"year": year}
        )

    def get_crd_prices(self) -> Dict:
        """
        Récupère les prix plancher/plafond du CRD Grondona

        Returns:
            Dict: Prix des commodités
        """
        return self._request("GET", "/api/v1/crd/prices")

    def record_transaction(
        self,
        partner_id: str,
        tx_type: str,
        amount: float,
        currency: str = "fulus",
        reference: Optional[str] = None
    ) -> Dict:
        """
        Enregistre une transaction BRI

        Args:
            partner_id: ID du partenaire
            tx_type: Type de transaction
            amount: Montant
            currency: Devise ("fulus" ou "nuqud")
            reference: Référence optionnelle

        Returns:
            Dict: ID de transaction
        """
        return self._request(
            "POST",
            "/api/v1/transactions/record",
            data={
                "partner_id": partner_id,
                "tx_type": tx_type,
                "amount": amount,
                "currency": currency,
                "reference": reference
            }
        )

    def get_zakat_rate(self) -> Dict:
        """
        Récupère le taux de Zakat en vigueur

        Returns:
            Dict: Taux de Zakat et seuils Nisab
        """
        return self._request("GET", "/api/v1/zakat/rate")

    # ---- Endpoints protégés (nécessitent authentification) ----

    def get_metrics(self) -> Dict:
        """
        Récupère les métriques économiques globales

        Returns:
            Dict: Métriques du système
        """
        return self._request("GET", "/secure/metrics")

    def run_simulation(
        self,
        years: int = 1,
        use_crd: bool = True,
        use_zakat: bool = True,
        use_bri: bool = True
    ) -> Dict:
        """
        Lance une simulation

        Args:
            years: Nombre d'années
            use_crd: Activer le CRD
            use_zakat: Activer la Zakat
            use_bri: Activer le réseau BRI

        Returns:
            Dict: Résultats de la simulation
        """
        return self._request(
            "POST",
            "/run",
            data={
                "years": years,
                "use_crd": use_crd,
                "use_zakat": use_zakat,
                "use_bri": use_bri
            }
        )

    def transfer_nuqud(
        self,
        from_zone: str,
        to_zone: str,
        amount: float
    ) -> Dict:
        """
        Effectue un transfert de nuqud entre zones

        Args:
            from_zone: Zone source
            to_zone: Zone destination
            amount: Montant en grammes d'or équivalent

        Returns:
            Dict: Résultat du transfert
        """
        return self._request(
            "POST",
            "/transfer",
            data={
                "from_zone": from_zone,
                "to_zone": to_zone,
                "amount_nuqud": amount
            }
        )

    # ---- Webhooks ----

    def subscribe_webhook(
        self,
        partner_id: str,
        url: str,
        events: List[str],
        secret: str
    ) -> Dict:
        """
        S'abonne à des webhooks

        Args:
            partner_id: ID du partenaire
            url: URL du webhook
            events: Liste des événements
            secret: Secret pour la signature HMAC

        Returns:
            Dict: Statut de l'abonnement
        """
        return self._request(
            "POST",
            "/api/webhooks/subscribe",
            data={
                "partner_id": partner_id,
                "url": url,
                "events": events,
                "secret": secret
            }
        )

    def unsubscribe_webhook(self, partner_id: str, url: str) -> Dict:
        """
        Se désabonne d'un webhook

        Args:
            partner_id: ID du partenaire
            url: URL du webhook

        Returns:
            Dict: Statut du désabonnement
        """
        return self._request(
            "DELETE",
            "/api/webhooks/unsubscribe",
            params={"partner_id": partner_id, "url": url}
        )

    def get_webhook_subscriptions(self, partner_id: str) -> Dict:
        """
        Liste les abonnements webhook d'un partenaire

        Args:
            partner_id: ID du partenaire

        Returns:
            Dict: Liste des abonnements
        """
        return self._request(
            "GET",
            "/api/webhooks/subscriptions",
            params={"partner_id": partner_id}
        )


class YusufClient(YusufGrondonaSDK):
    """
    Alias pour compatibilité ascendante
    """
    pass


# ---- Exemple d'utilisation ----
if __name__ == "__main__":
    # Initialisation du SDK
    sdk = YusufGrondonaSDK(api_key="demo_key", base_url="http://localhost:8000")

    print("=== YUSUF-GRONDONA SDK ===\n")

    # Health check
    health = sdk.health_check()
    print(f"Health: {health}")

    # Taux de change
    rate = sdk.get_exchange_rate("Chine", "France", 1000)
    print(f"Taux de change: {rate}")

    # ESG
    esg = sdk.get_esg_score("Chine")
    print(f"ESG Chine: {esg}")

    # CRD
    crd = sdk.get_crd_prices()
    print(f"CRD: {crd}")

    # Transfert
    transfer = sdk.transfer_nuqud("Chine", "NUL", 100)
    print(f"Transfert: {transfer}")

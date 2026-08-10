"""
Carbon Offsetting Manager – Crédits carbone BCC
===============================================

Gestion des crédits carbone (BRI Carbon Credit – BCC) pour :
- Suivi de l'empreinte carbone des partenaires BRI
- Offsetting des émissions
- Marché des crédits carbone
- Intégration avec le smart contract CarbonCreditToken

License: CC BY-SA 4.0 – Marc Daghar
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple


@dataclass
class CarbonAccount:
    """
    Compte carbone d'un partenaire BRI
    """
    partner_id: str
    partner_name: str
    footprint_tco2: float = 0.0  # Empreinte carbone (tonnes CO2)
    offset_credits: float = 0.0  # Crédits d'offset
    bcc_balance: float = 0.0     # Solde BCC
    total_emissions: float = 0.0  # Émissions totales
    total_offset: float = 0.0    # Total offsetté

    def to_dict(self) -> Dict:
        return {
            "partner_id": self.partner_id,
            "partner_name": self.partner_name,
            "footprint_tco2": self.footprint_tco2,
            "offset_credits": self.offset_credits,
            "bcc_balance": self.bcc_balance,
            "total_emissions": self.total_emissions,
            "total_offset": self.total_offset,
            "net_footprint": self.net_footprint()
        }

    def net_footprint(self) -> float:
        """Empreinte nette (footprint - offset)"""
        return max(0, self.footprint_tco2 - self.offset_credits * 10)


class CarbonOffsetManager:
    """
    Gestionnaire des crédits carbone
    """

    def __init__(self):
        self.accounts: Dict[str, CarbonAccount] = {}
        self.transactions: List[Dict] = []
        self.market_price: float = 3.50  # USD par BCC

        # Facteurs d'émission par mode de transport (tCO2/km/tonne)
        self.emission_factors = {
            "maritime": 0.015,
            "rail": 0.005,
            "road": 0.08,
            "air": 0.6,
            "pipeline": 0.003
        }

    def register_partner(self, partner_id: str, partner_name: str) -> CarbonAccount:
        """Enregistre un partenaire BRI"""
        if partner_id not in self.accounts:
            account = CarbonAccount(
                partner_id=partner_id,
                partner_name=partner_name
            )
            self.accounts[partner_id] = account
        return self.accounts[partner_id]

    def get_account(self, partner_id: str) -> Optional[CarbonAccount]:
        """Récupère le compte d'un partenaire"""
        return self.accounts.get(partner_id)

    def record_emissions(
        self,
        partner_id: str,
        distance_km: float,
        weight_tons: float,
        transport_mode: str
    ) -> Dict:
        """
        Enregistre les émissions d'une expédition

        Args:
            partner_id: ID du partenaire
            distance_km: Distance en kilomètres
            weight_tons: Poids en tonnes
            transport_mode: Mode de transport

        Returns:
            Dict: Résultat avec les émissions calculées
        """
        if partner_id not in self.accounts:
            return {"error": "Partenaire non trouvé"}

        factor = self.emission_factors.get(transport_mode, 0.02)
        emissions = distance_km * weight_tons * factor

        account = self.accounts[partner_id]
        account.footprint_tco2 += emissions
        account.total_emissions += emissions

        self.transactions.append({
            "type": "emission",
            "partner_id": partner_id,
            "distance_km": distance_km,
            "weight_tons": weight_tons,
            "transport_mode": transport_mode,
            "emissions_tco2": emissions,
            "timestamp": time.time()
        })

        return {
            "partner_id": partner_id,
            "emissions_tco2": emissions,
            "total_footprint": account.footprint_tco2,
            "transport_mode": transport_mode
        }

    def mint_credits(self, partner_id: str, amount: float, reason: str = "") -> Dict:
        """
        Émet des crédits carbone (BCC)

        Args:
            partner_id: ID du partenaire
            amount: Nombre de crédits
            reason: Raison de l'émission

        Returns:
            Dict: Résultat
        """
        if partner_id not in self.accounts:
            return {"error": "Partenaire non trouvé"}

        account = self.accounts[partner_id]
        account.bcc_balance += amount
        account.offset_credits += amount

        self.transactions.append({
            "type": "mint",
            "partner_id": partner_id,
            "amount": amount,
            "reason": reason,
            "timestamp": time.time()
        })

        return {
            "partner_id": partner_id,
            "amount": amount,
            "new_balance": account.bcc_balance,
            "reason": reason
        }

    def offset_emissions(self, partner_id: str, amount: float) -> Dict:
        """
        Utilise des crédits carbone pour offsetter des émissions

        Args:
            partner_id: ID du partenaire
            amount: Nombre de crédits à utiliser

        Returns:
            Dict: Résultat
        """
        if partner_id not in self.accounts:
            return {"error": "Partenaire non trouvé"}

        account = self.accounts[partner_id]

        if account.bcc_balance < amount:
            return {"error": f"Solde insuffisant. Disponible: {account.bcc_balance}"}

        account.bcc_balance -= amount
        account.total_offset += amount * 10  # 1 crédit = 10 tonnes CO2

        # Réduction de l'empreinte
        reduction = amount * 10
        account.footprint_tco2 = max(0, account.footprint_tco2 - reduction)

        self.transactions.append({
            "type": "offset",
            "partner_id": partner_id,
            "amount": amount,
            "reduction_tco2": reduction,
            "timestamp": time.time()
        })

        return {
            "partner_id": partner_id,
            "credits_used": amount,
            "reduction_tco2": reduction,
            "new_balance": account.bcc_balance,
            "remaining_footprint": account.footprint_tco2
        }

    def calculate_shipment_carbon(
        self,
        distance_km: float,
        weight_tons: float,
        transport_mode: str
    ) -> Dict:
        """
        Calcule l'empreinte carbone d'une expédition

        Returns:
            Dict: Émissions et crédits nécessaires
        """
        factor = self.emission_factors.get(transport_mode, 0.02)
        emissions = distance_km * weight_tons * factor

        return {
            "distance_km": distance_km,
            "weight_tons": weight_tons,
            "transport_mode": transport_mode,
            "emissions_tco2": emissions,
            "credits_needed": emissions / 10,  # 1 crédit = 10 tonnes
            "cost_usd": (emissions / 10) * self.market_price
        }

    def get_market_stats(self) -> Dict:
        """Statistiques du marché des crédits carbone"""
        total_bcc = sum(a.bcc_balance for a in self.accounts.values())
        total_emissions = sum(a.total_emissions for a in self.accounts.values())
        total_offset = sum(a.total_offset for a in self.accounts.values())

        return {
            "market_price_usd": self.market_price,
            "total_bcc_in_circulation": total_bcc,
            "total_emissions_tco2": total_emissions,
            "total_offset_tco2": total_offset,
            "offset_rate": total_offset / total_emissions if total_emissions > 0 else 0,
            "active_partners": len([a for a in self.accounts.values() if a.total_emissions > 0])
        }

    def get_partner_status(self, partner_id: str) -> Optional[Dict]:
        """Statut complet d'un partenaire"""
        if partner_id not in self.accounts:
            return None

        account = self.accounts[partner_id]
        return {
            **account.to_dict(),
            "offset_rate": account.total_offset / account.total_emissions if account.total_emissions > 0 else 0,
            "bcc_value_usd": account.bcc_balance * self.market_price
        }

    def get_transactions(self, limit: int = 20) -> List[Dict]:
        """Transactions récentes"""
        return self.transactions[-limit:]


# ---- Exemple d'utilisation ----
if __name__ == "__main__":
    manager = CarbonOffsetManager()

    print("=== CRÉDITS CARBONE BCC ===\n")

    # Enregistrement des partenaires
    manager.register_partner("Chine", "Chine")
    manager.register_partner("France", "France")

    # Calcul d'une expédition
    shipment = manager.calculate_shipment_carbon(11000, 500, "maritime")
    print(f"Expédition Chine→France:")
    print(f"  Distance: {shipment['distance_km']} km")
    print(f"  Poids: {shipment['weight_tons']} tonnes")
    print(f"  Émissions: {shipment['emissions_tco2']:.2f} tCO2")
    print(f"  Crédits nécessaires: {shipment['credits_needed']:.1f} BCC")

    # Émission de crédits
    manager.mint_credits("Chine", 100, "Réduction des émissions")
    print(f"\n100 BCC émis pour la Chine")

    # Offsetting
    result = manager.offset_emissions("Chine", 50)
    print(f"Offset: {result['reduction_tco2']:.0f} tCO2 réduites")

    # Statistiques
    stats = manager.get_market_stats()
    print(f"\nStatistiques du marché:")
    print(f"  Prix: ${stats['market_price_usd']}/BCC")
    print(f"  Total BCC: {stats['total_bcc_in_circulation']:.0f}")
    print(f"  Total offset: {stats['total_offset_tco2']:.0f} tCO2")

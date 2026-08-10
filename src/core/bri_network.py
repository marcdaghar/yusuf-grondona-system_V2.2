"""
Réseau BRI (Belt and Road Initiative) – Multi-zones
===================================================

Réseau multi‑zones : Chine, Russie, NUL (New Unified Levant),
Émirat, Indonésie, Turquie, France, Italie, Espagne, Portugal

Convertibilité inter‑zones en nuqud (or/argent) ou panier BRI

License: CC BY-SA 4.0 – Marc Daghar
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import time
import math


@dataclass
class ZoneBRI:
    """
    Une zone BRI avec ses réserves et paramètres monétaires
    """
    name: str
    capital_city: str
    nuqud_reserve_grams: float      # en équivalent or (grammes)
    fulus_supply: float = 0.0
    exchange_rate_from_nuqud: float = 1.0   # 1g or = X fulus
    local_currency_name: str = "fulus"

    # Métadonnées
    population: Optional[float] = None
    gdp_usd: Optional[float] = None
    region: str = ""

    # Historique des transactions
    transactions: List[Dict] = field(default_factory=list)

    def mint_fulus(self, against_nuqud: float) -> Optional['Fulus']:
        """
        Émission de fulus contre dépôt de nuqud (or/argent)
        """
        if against_nuqud <= self.nuqud_reserve_grams:
            from .fulus import Fulus
            fulus_issued = against_nuqud * self.exchange_rate_from_nuqud
            self.nuqud_reserve_grams -= against_nuqud
            self.fulus_supply += fulus_issued
            return Fulus(fulus_issued, issued_by=f"BRI-{self.name}")
        return None

    def receive_nuqud(self, amount_grams: float):
        """Reçoit du nuqud en réserve"""
        self.nuqud_reserve_grams += amount_grams

    def send_nuqud(self, amount_grams: float) -> bool:
        """Envoie du nuqud depuis la réserve"""
        if amount_grams <= self.nuqud_reserve_grams:
            self.nuqud_reserve_grams -= amount_grams
            return True
        return False

    def record_transaction(self, tx: Dict):
        """Enregistre une transaction"""
        self.transactions.append(tx)

    def get_summary(self) -> Dict:
        """Retourne un résumé de la zone"""
        return {
            'name': self.name,
            'capital': self.capital_city,
            'nuqud_reserve_grams': self.nuqud_reserve_grams,
            'fulus_supply': self.fulus_supply,
            'exchange_rate': self.exchange_rate_from_nuqud,
            'total_transactions': len(self.transactions),
            'region': self.region
        }


@dataclass
class LiquidityBridge:
    """
    Pont de liquidité entre deux zones BRI
    """
    from_zone: str
    to_zone: str
    min_transfer_nuqud: float = 10.0
    fee_basis_points: int = 10      # 10 bps = 0.1%
    max_transfer_nuqud: float = 10000.0

    def transfer(self, zone_a: ZoneBRI, zone_b: ZoneBRI, amount_nuqud: float) -> Dict:
        """
        Transfère du nuqud d'une zone à l'autre
        """
        if amount_nuqud < self.min_transfer_nuqud:
            return {"error": "montant inférieur au seuil minimum"}

        if amount_nuqud > self.max_transfer_nuqud:
            return {"error": "montant supérieur au seuil maximum"}

        fee = amount_nuqud * (self.fee_basis_points / 10_000)
        net = amount_nuqud - fee

        if zone_a.nuqud_reserve_grams >= amount_nuqud:
            zone_a.nuqud_reserve_grams -= amount_nuqud
            zone_b.nuqud_reserve_grams += net

            result = {
                "success": True,
                "from": self.from_zone,
                "to": self.to_zone,
                "gross": amount_nuqud,
                "fee": fee,
                "net": net,
                "timestamp": time.time()
            }

            # Enregistrement des transactions
            zone_a.record_transaction({
                'type': 'outgoing',
                'to': self.to_zone,
                'amount': amount_nuqud,
                'fee': fee,
                'net': net
            })
            zone_b.record_transaction({
                'type': 'incoming',
                'from': self.from_zone,
                'amount': net
            })

            return result

        return {"error": "réserve insuffisante dans la zone source"}


class BRINetwork:
    """
    Réseau BRI complet avec zones et ponts de liquidité
    """

    def __init__(self):
        self.zones: Dict[str, ZoneBRI] = {}
        self.bridges: List[LiquidityBridge] = []
        self.global_transactions: List[Dict] = []

    def add_zone(self, zone: ZoneBRI):
        """Ajoute une zone au réseau"""
        self.zones[zone.name] = zone

    def add_bridge(self, from_zone: str, to_zone: str, **kwargs):
        """Ajoute un pont de liquidité entre deux zones"""
        bridge = LiquidityBridge(from_zone=from_zone, to_zone=to_zone, **kwargs)
        self.bridges.append(bridge)

    def get_zone(self, name: str) -> Optional[ZoneBRI]:
        """Récupère une zone par son nom"""
        return self.zones.get(name)

    def transfer(self, from_zone: str, to_zone: str, amount_nuqud: float) -> Dict:
        """
        Effectue un transfert entre deux zones
        """
        if from_zone not in self.zones or to_zone not in self.zones:
            return {"error": "zone inconnue"}

        # Trouver le pont (symétrique)
        for bridge in self.bridges:
            if bridge.from_zone == from_zone and bridge.to_zone == to_zone:
                result = bridge.transfer(self.zones[from_zone],
                                         self.zones[to_zone],
                                         amount_nuqud)
                if result.get('success'):
                    self.global_transactions.append(result)
                return result

        # Chercher un pont dans l'autre sens
        for bridge in self.bridges:
            if bridge.from_zone == to_zone and bridge.to_zone == from_zone:
                # Transfert inversé
                result = bridge.transfer(self.zones[to_zone],
                                         self.zones[from_zone],
                                         amount_nuqud)
                if result.get('success'):
                    self.global_transactions.append(result)
                return result

        return {"error": "aucun pont direct trouvé"}

    def global_summary(self) -> Dict:
        """Retourne un résumé global du réseau"""
        return {
            zone.name: zone.get_summary()
            for zone in self.zones.values()
        }

    def get_total_nuqud_reserves(self) -> float:
        """Total des réserves nuqud de toutes les zones"""
        return sum(z.nuqud_reserve_grams for z in self.zones.values())

    def get_total_fulus_supply(self) -> float:
        """Total de la masse fulus de toutes les zones"""
        return sum(z.fulus_supply for z in self.zones.values())

    def get_zone_by_region(self, region: str) -> List[ZoneBRI]:
        """Récupère les zones d'une région donnée"""
        return [z for z in self.zones.values() if z.region == region]

    def get_recent_transactions(self, n: int = 10) -> List[Dict]:
        """Retourne les n dernières transactions globales"""
        return self.global_transactions[-n:]


# Zones BRI par défaut
def create_default_network() -> BRINetwork:
    """Crée un réseau BRI avec les zones par défaut"""
    network = BRINetwork()

    zones = [
        ZoneBRI("Chine", "Pékin", 20000, 0, 10.0, region="Asie"),
        ZoneBRI("Russie", "Moscou", 15000, 0, 9.5, region="Eurasie"),
        ZoneBRI("NUL", "Beyrouth", 5000, 0, 8.0, region="Méditerranée"),
        ZoneBRI("Émirat", "Abu Dhabi", 8000, 0, 11.0, region="Moyen-Orient"),
        ZoneBRI("Indonésie", "Jakarta", 12000, 0, 9.0, region="Asie du Sud-Est"),
        ZoneBRI("Turquie", "Istanbul", 7000, 0, 8.5, region="Eurasie"),
        ZoneBRI("France", "Paris", 4000, 0, 10.0, region="Europe"),
        ZoneBRI("Italie", "Rome", 3000, 0, 10.0, region="Europe"),
        ZoneBRI("Espagne", "Madrid", 2500, 0, 10.0, region="Europe"),
        ZoneBRI("Portugal", "Lisbonne", 1500, 0, 10.0, region="Europe"),
    ]

    for zone in zones:
        network.add_zone(zone)

    # Ponts par défaut
    default_bridges = [
        ("Chine", "Russie", 10, 15),
        ("Chine", "NUL", 10, 10),
        ("Russie", "NUL", 10, 12),
        ("NUL", "Émirat", 10, 10),
        ("Émirat", "Turquie", 10, 12),
        ("Chine", "Indonésie", 10, 10),
        ("France", "NUL", 10, 10),
        ("France", "Turquie", 10, 10),
        ("Italie", "France", 10, 5),
        ("Espagne", "Portugal", 10, 5),
        ("Espagne", "France", 10, 8),
    ]

    for from_z, to_z, min_amt, fee in default_bridges:
        network.add_bridge(from_z, to_z, min_transfer_nuqud=min_amt, fee_basis_points=fee)

    return network


# Exemple d'utilisation
if __name__ == "__main__":
    network = create_default_network()

    print("=== RÉSEAU BRI ===")
    summary = network.global_summary()
    for zone, data in summary.items():
        print(f"\n🌏 {zone}")
        print(f"   Réserves nuqud: {data['nuqud_reserve_grams']:.0f} g or eq")
        print(f"   Masse fulus: {data['fulus_supply']:.0f}")
        print(f"   Taux de change: {data['exchange_rate']:.2f}")

    # Transfert test
    print("\n=== TRANSFERT TEST ===")
    result = network.transfer("Chine", "NUL", 100)
    print(f"Chine → NUL (100g): {result}")

    print(f"\nRéserves totales: {network.get_total_nuqud_reserves():.2f} g")
    print(f"Masse fulus totale: {network.get_total_fulus_supply():.2f}")

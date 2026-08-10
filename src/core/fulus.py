"""
Fulus (فلس) – Monnaie de vélocité (pluriel : fulus)
====================================================

Selon la loi islamique, le fulus :
1. Est soumis à des règles PLUS SOUPLES sur le riba
2. Permet des échanges avec délai (al-nasia assoupli)
3. Permet des échanges avec surplus modéré (al-fadl assoupli)
4. N'est NI un étalon de mesure, NI une réserve de valeur
5. N'a qu'une fonction : FACILITER LES TRANSACTIONS (vélocité)

Le fulus est l'équivalent de la monnaie courante convertible.
Il signale les prix aux agents à rationalité limitée.

License: CC BY-SA 4.0 – Marc Daghar
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import random
import time


@dataclass
class Fulus:
    """
    Représente une quantité de fulus (monnaie de vélocité).
    """
    amount: float
    issued_by: str = "system"
    issuer_type: str = "guilde"  # 'guilde', 'emir', 'system'
    timestamp: float = field(default_factory=time.time)
    velocity_target: float = 10.0  # tours par an

    def __repr__(self) -> str:
        return f"Fulus({self.amount:.2f}, issued_by={self.issued_by})"


@dataclass
class FulusCurrency:
    """
    Monnaie de vélocité (fulus)

    Différence fondamentale avec le nuqud :
    - Le fulus N'EST PAS thésaurisable
    - Le fulus N'EST PAS un étalon de mesure
    - Le fulus N'a qu'une fonction : la vélocité marchande

    Le fulus doit CIRCULER. Sa non-circulation est une inefficacité.
    """
    name: str
    symbol: str
    is_convertible_to_nuqud: bool = True
    convertibility_mechanism: str = "Grondona CRD"

    # Taux de vélocité cible (doit être élevé)
    target_velocity_per_year: float = 10.0

    # Règles assouplies (différentes du nuqud)
    riba_al_fadl_allowed: bool = True   # Surplus modéré autorisé
    riba_al_nasia_allowed: bool = True  # Délai autorisé
    max_riba_fadl_percent: float = 0.05  # 5% max pour le fulus

    def __post_init__(self):
        self.circulation_supply: float = 0.0
        self.velocity_history: List[float] = []
        self.transaction_history: List[Dict] = []

    def issue(self, amount: float, purpose: str) -> Dict:
        """
        Émission de fulus (monnaie de vélocité)
        Contrairement au nuqud, le fulus est créé pour faciliter les échanges,
        non pour stocker de la valeur
        """
        # Le fulus doit être adossé à des biens réels (convertibilité)
        self.circulation_supply += amount

        return {
            'status': 'issued',
            'amount': amount,
            'purpose': purpose,
            'circulation_supply': self.circulation_supply,
            'message': f"Émission de {amount} {self.symbol}. "
                       f"Cette monnaie doit CIRCULER, non être thésaurisée."
        }

    def destroy(self, amount: float) -> Dict:
        """Destruction de fulus (contraction monétaire)"""
        if amount > self.circulation_supply:
            return {
                'status': 'error',
                'message': f"Montant {amount} supérieur à la masse en circulation {self.circulation_supply}"
            }

        self.circulation_supply -= amount

        return {
            'status': 'destroyed',
            'amount': amount,
            'circulation_supply': self.circulation_supply
        }

    def velocity(self, annual_transactions: float) -> float:
        """Vélocité monétaire = transactions / masse monétaire"""
        if self.circulation_supply == 0:
            return 0.0
        v = annual_transactions / self.circulation_supply
        self.velocity_history.append(v)
        return v

    def velocity_efficiency(self, annual_transactions: float) -> Dict:
        """Efficacité de la vélocité par rapport à la cible"""
        v_actual = self.velocity(annual_transactions)
        efficiency = v_actual / self.target_velocity_per_year

        return {
            'velocity_actual': v_actual,
            'velocity_target': self.target_velocity_per_year,
            'efficiency': efficiency,
            'is_circulating_well': efficiency >= 0.8,
            'message': "La monnaie circule bien" if efficiency >= 0.8
                      else "La monnaie est thésaurisée (inefficace)"
        }

    def riba_validation(self, exchange_amount: float,
                        surplus_percent: float,
                        has_delay: bool) -> Tuple[bool, str]:
        """
        Validation des règles assouplies pour le fulus

        Différence avec le nuqud :
        - Surplus modéré autorisé (contrairement au nuqud)
        - Délai autorisé (contrairement au nuqud)
        """
        if not self.riba_al_fadl_allowed and surplus_percent > 0:
            return False, "RIBA AL-FADL : Surplus interdit dans cet échange"

        if surplus_percent > self.max_riba_fadl_percent:
            return False, f"SURPLUS EXCESSIF : {surplus_percent:.1%} > {self.max_riba_fadl_percent:.1%}"

        if not self.riba_al_nasia_allowed and has_delay:
            return False, "RIBA AL-NASIA : Délai interdit dans cet échange"

        return True, "Échange conforme aux règles assouplies du fulus"

    def record_transaction(self, from_entity: str, to_entity: str,
                           amount: float, purpose: str) -> Dict:
        """Enregistre une transaction en fulus"""
        self.transaction_history.append({
            'from': from_entity,
            'to': to_entity,
            'amount': amount,
            'purpose': purpose,
            'timestamp': time.time()
        })
        return {
            'status': 'recorded',
            'transaction_id': len(self.transaction_history) - 1
        }

    def get_status(self) -> Dict:
        """Retourne l'état complet de la monnaie"""
        return {
            'name': self.name,
            'symbol': self.symbol,
            'circulation_supply': self.circulation_supply,
            'target_velocity': self.target_velocity_per_year,
            'avg_velocity': sum(self.velocity_history[-10:]) / len(self.velocity_history[-10:]) if self.velocity_history else 0,
            'total_transactions': len(self.transaction_history),
            'convertible': self.is_convertible_to_nuqud
        }


class FulusSignalSystem:
    """
    Le fulus comme système de signal pour agents à rationalité limitée

    Dans un marché parfait, les prix contiennent toute l'information.
    Mais les agents ont une rationalité LIMITÉE et une asymétrie d'information.

    Le fulus sert de SIGNAL aux agents économiques :
    - Il indique quand acheter/vendre (via prix plancher/plafond Grondona)
    - Il permet la coordination sans information parfaite
    - Il compense l'asymétrie des données
    """

    def __init__(self, fulus: FulusCurrency):
        self.fulus = fulus
        self.price_signals_history: List[Dict] = []

    def generate_signal(self, current_price: float,
                        floor_price: float,
                        ceiling_price: float,
                        market_context: str) -> Dict:
        """
        Le fulus génère un signal aux agents
        Ce signal compense leur rationalité limitée et l'asymétrie d'information
        """
        signal = {
            'context': market_context,
            'current_price': current_price,
            'floor_price': floor_price,
            'ceiling_price': ceiling_price,
            'action_signal': None,
            'confidence': 0.0,
            'timestamp': time.time()
        }

        if current_price < floor_price:
            signal['action_signal'] = 'BUY'
            signal['confidence'] = min(0.9, (floor_price - current_price) / floor_price)
            signal['message'] = "Prix sous le plancher → opportunité d'achat (CRD va acheter)"

        elif current_price > ceiling_price:
            signal['action_signal'] = 'SELL'
            signal['confidence'] = min(0.9, (current_price - ceiling_price) / ceiling_price)
            signal['message'] = "Prix au-dessus du plafond → opportunité de vente (CRD va vendre)"

        else:
            signal['action_signal'] = 'HOLD'
            signal['confidence'] = 0.5
            signal['message'] = "Prix dans la fourchette de stabilité"

        self.price_signals_history.append(signal)
        return signal

    def bounded_rationality_compensation(self, signal: Dict,
                                         agent_knowledge_level: float) -> Dict:
        """
        Compense l'asymétrie d'information et la rationalité limitée
        Un agent avec peu d'information (knowledge_level bas) reçoit un signal plus fort
        """
        # Si l'agent a peu d'information, le signal doit être plus clair
        compensation_factor = 1.0 / max(0.1, agent_knowledge_level)

        compensated_signal = {
            'original_signal': signal['action_signal'],
            'agent_knowledge_level': agent_knowledge_level,
            'compensated_confidence': min(1.0, signal['confidence'] * compensation_factor),
            'message': None
        }

        if agent_knowledge_level < 0.3:
            compensated_signal['message'] = "Signal renforcé (asymétrie élevée)"
        elif agent_knowledge_level > 0.7:
            compensated_signal['message'] = "Signal normal (agent informé)"
        else:
            compensated_signal['message'] = "Signal adapté à la rationalité limitée"

        return compensated_signal

    def get_recent_signals(self, n: int = 10) -> List[Dict]:
        """Retourne les n derniers signaux"""
        return self.price_signals_history[-n:]


# Exemple d'utilisation
if __name__ == "__main__":
    # Création de la monnaie
    fulus = FulusCurrency("Fulus Méditerranéen", "FUL")
    print("=== SYSTÈME FULUS ===")

    # Émission
    result = fulus.issue(10000, "Lancement de la production")
    print(f"Émission: {result['message']}")

    # Vélocité
    efficiency = fulus.velocity_efficiency(50000)
    print(f"Vélocité: {efficiency['velocity_actual']:.2f} tours/an")
    print(f"Efficacité: {efficiency['efficiency']:.1%}")

    # Signal
    signal_system = FulusSignalSystem(fulus)
    signal = signal_system.generate_signal(95, 100, 120, "Marché du blé")
    print(f"Signal: {signal['message']}")

    # Compensation pour agent peu informé
    compensated = signal_system.bounded_rationality_compensation(signal, 0.2)
    print(f"Signal compensé: {compensated['message']}")

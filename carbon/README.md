# Carbon Credits – BCC (BRI Carbon Credit)

Module de gestion des crédits carbone pour le système Yusuf-Grondona.

## Fonctionnalités

- Suivi de l'empreinte carbone des partenaires BRI
- Calcul des émissions par mode de transport
- Émission et utilisation de crédits carbone (BCC)
- Marché des crédits
- Intégration avec le smart contract CarbonCreditToken

## Utilisation

```python
from carbon.offsetting_manager import CarbonOffsetManager

manager = CarbonOffsetManager()

# Enregistrement d'un partenaire
manager.register_partner("Chine", "Chine")

# Calcul des émissions
emissions = manager.calculate_shipment_carbon(11000, 500, "maritime")

# Émission de crédits
manager.mint_credits("Chine", 100, "Réduction des émissions")

# Offsetting
manager.offset_emissions("Chine", 50)

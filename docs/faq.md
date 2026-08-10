# Foire aux questions (FAQ)

## Généralités

### Qu'est-ce que le système Yusuf-Grondona ?

C'est une alternative monétaire complète qui remplace la monnaie-dette (créée par les banques) par une monnaie bimétallique (or/argent) adossée à l'économie réelle. Il respecte les principes islamiques : pas d'intérêt (riba), Zakat politique, inspection du marché (hisba).

### En quoi est-il différent des cryptomonnaies ?

Bitcoin n'a pas d'ancrage réel (or/argent). Le fulus est convertible en nuqud et sa masse est limitée par les réserves physiques. De plus, notre système inclut une gouvernance humaine (muhtassib, émir) et des obligations religieuses (Zakat).

## Utilisation quotidienne

### Comment payer avec le fulus ?

Vous pouvez utiliser un portefeuille numérique (dashboard, application mobile) ou des QR codes. Le commerçant accepte le fulus comme n'importe quelle monnaie.

### Où puis-je convertir mes fulus en nuqud ?

Dans les bureaux de change agréés par l'émir, ou via l'API. Le taux de change est fixe par zone (ex: 1g or = 10 fulus).

### Que se passe-t-il en cas de pénurie ?

Le CRD (Commodity Reserve Department) libère des stocks de produits de première nécessité. La Zakat est redistribuée en urgence.

## Gouvernance

### Qui est l'émir ?

L'émir est le chef politique local qui collecte la Zakat, nomme le muhtassib, et garantit la bonne circulation du fulus.

### Quel est le rôle du muhtassib ?

Le muhtassib inspecte le marché : vérifie les poids, les certificats halal, et signale les fraudes. L'IA l'assiste, mais c'est lui qui décide.

## Technique

### Faut-il être informaticien pour utiliser le système ?

Non. Le dashboard Streamlit est une interface web simple. Les commerçants utilisent un portefeuille avec QR code.

### Puis-je l'installer chez moi (pour ma commune) ?

Oui. Le système est open-source (licence CC BY-SA). Vous pouvez le déployer sur un petit serveur (Raspberry Pi, VPS).

## Aspects religieux

### Le fulus est-il halal ?

Oui. Le fulus est une monnaie de circulation (pas de thésaurisation). Il n'y a pas d'intérêt (riba). Seul le nuqud supporte la Zakat (2.5%).

### La Zakat est-elle obligatoire ?

Oui. Dans le système, la Zakat est *prise* par l'émir (comme à Médine), non laissée à la volonté individuelle.

## Dépannage

### Mon fulus ne passe pas sur le réseau

Vérifiez que votre portefeuille est connecté à l'API. Contactez votre muhtassib local.

### Je n'arrive pas à certifier mon produit halal

Assurez-vous d'avoir les documents requis. Le muhtassib peut vous assister.

### Le dashboard affiche des erreurs

Vérifiez que l'API tourne : `curl http://localhost:8000/health`. Regardez les logs : `docker compose logs api`.

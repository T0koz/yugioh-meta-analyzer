# 0027 — Base : une copie de référence partagée, pas de base hébergée (option A)

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Claude (note de comparaison TOK-110), recommandation retenue ; à confirmer par Thomas si la source ne le dit pas
- Tickets : TOK-110

## Contexte
Le ticket partait de « deux copies de SQLite qui divergent ». L'analyse montre qu'il n'y a qu'un écrivain légitime, le job du lundi sur le Mac de Thomas ; les tables dérivées se recalculent depuis le code.

## Options
- A : copie de référence partagée (instantané exporté vers un dossier Drive), 0 €, environ 1 h
- B : fichier SQLite sur stockage objet (R2, B2), environ ½ jour
- C : Turso, plusieurs jours (quota d'écritures gratuit presque consommé par le fetch du lundi)
- D : Postgres managé (Neon, Supabase), 1 à 2 semaines

## Décision
Option A maintenant. B si le job quitte le Mac de Thomas ; D à réévaluer quand le produit B2B aura besoin d'écrire en ligne, pour la partie service seulement.

## Raison
Pipeline mono-écrivain : la force de Postgres (écritures concurrentes) n'est pas utile aujourd'hui, la migration coûte cher et n'apporte rien à l'analyse. Tarifs vérifiés le 2026-11-16, à revérifier au moment de choisir. Contrainte : base privée (≈ 15 000 pseudos de joueurs), coût zéro.

## Conséquences
Une seule base de référence (celle de Thomas) ; la copie de la collaboratrice est un bac à sable ; ce qui devient officiel passe par du code commité. Statut « acceptée » : la source est une recommandation ; l'acceptation de Thomas n'y est pas consignée explicitement, mais `CLAUDE.md` applique la règle.

## Sources
- `docs/collaboration/base-hebergee.md`

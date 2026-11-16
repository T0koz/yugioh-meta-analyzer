# 0003 — Crédibilité des chiffres traitée avant la nouvelle page d'accueil

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Recommandation de l'agent retenue par défaut (Thomas n'a rien coché pour les points 1 à 10 ; à corriger s'il le souhaite)
- Tickets : TOK-94, TOK-106, TOK-113

## Contexte
L'audit a relevé des chiffres affichés peu crédibles : Elfnote « mars 2027 » déjà à 20 % en TCG, Ash Blossom à 100/100, tier list datée du 17 juin, écart OCG → TCG de 3 ou 4 mois.

## Options
- Options détaillées dans `docs/audit-front/rapport.md` et `3-proposition.md`, non reprises ici.

## Décision
Traiter ces chiffres avant la nouvelle page d'accueil, avec l'agent `data-scientist-ygo`.

## Raison
Un site plus beau qui affiche des chiffres faux perdrait sa crédibilité (`decisions-2026-11-16.md`, § « Ce que change la décision 11 »).

## Conséquences
Impose un ordre : fiabilisation des chiffres (nettoyage du 2026-11-16, TOK-113) puis accueil (TOK-106). Le titre de l'accueil a ensuite été corrigé (voir la note sur TOK-106).

## Sources
- `docs/audit-front/decisions-2026-11-16.md` (décision 3)

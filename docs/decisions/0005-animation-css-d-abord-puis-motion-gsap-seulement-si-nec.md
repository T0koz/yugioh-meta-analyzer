# 0005 — Animation : CSS d'abord, puis Motion, GSAP seulement si nécessaire

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Recommandation de l'agent retenue par défaut (Thomas n'a rien coché pour les points 1 à 10 ; à corriger s'il le souhaite)
- Tickets : TOK-94

## Contexte
La refonte prévoit un langage de mouvement et un récit au défilement.

## Options
- Options détaillées dans `docs/audit-front/rapport.md` et `3-proposition.md`, non reprises ici.

## Décision
CSS d'abord, puis Motion ; GSAP seulement si le récit au défilement l'exige.

## Raison
Raison non consignée dans le tableau.

## Conséquences
L'accueil (TOK-106) est réalisé avec du CSS et un interrupteur `data-live`, sans GSAP (`context.md`, section TOK-106).

## Sources
- `docs/audit-front/decisions-2026-11-16.md` (décision 5)

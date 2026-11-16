# 0008 — Graphiques : SVG maison avec D3, remplacement de recharts et vis-network

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Recommandation de l'agent retenue par défaut (Thomas n'a rien coché pour les points 1 à 10 ; à corriger s'il le souhaite)
- Tickets : TOK-94, TOK-99, TOK-102

## Contexte
recharts et vis-network pèsent sur le JavaScript chargé et limitent le design.

## Options
- Options détaillées dans `docs/audit-front/rapport.md` et `3-proposition.md`, non reprises ici.

## Décision
SVG maison avec D3 pour les graphiques ; Sigma.js ou PixiJS pour le graphe.

## Raison
Raison non consignée dans le tableau. Mesuré après coup : `/evolution` passe de 274,1 à 190,6 ko de JavaScript (`context.md`, TOK-99).

## Conséquences
Graphiques faits (TOK-99, recharts supprimé). Le graphe de synergies (TOK-102) reste en attente.

## Sources
- `docs/audit-front/decisions-2026-11-16.md` (décision 8)

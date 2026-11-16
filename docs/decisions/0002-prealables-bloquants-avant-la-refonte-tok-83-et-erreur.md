# 0002 — Préalables bloquants avant la refonte : TOK-83 et erreur 500 de /early-signals

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Recommandation de l'agent retenue par défaut (Thomas n'a rien coché pour les points 1 à 10 ; à corriger s'il le souhaite)
- Tickets : TOK-94, TOK-83, TOK-95

## Contexte
Deux défauts techniques précédaient la refonte : le correctif de lenteur du Ban Radar (TOK-83) n'était pas dans `main`, et `/early-signals` renvoyait une erreur 500.

## Options
- Options détaillées dans `docs/audit-front/rapport.md` et `3-proposition.md`, non reprises ici.

## Décision
Fusionner le correctif TOK-83 dans `main` et corriger l'erreur 500 de `/early-signals` tout de suite.

## Raison
Raison non consignée (le tableau ne la donne pas).

## Conséquences
TOK-83 figure parmi les tickets terminés (index `idx_cards_name_clean`, `context.md`). `context.md` cite aussi TOK-95 (`EarlySignal.archetype` nullable) ; le lien avec l'erreur 500 n'est pas confirmé par les sources lues.

## Sources
- `docs/audit-front/decisions-2026-11-16.md` (décision 2)

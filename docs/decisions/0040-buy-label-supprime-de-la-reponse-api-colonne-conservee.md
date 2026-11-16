# 0040 — buy_label supprimé de la réponse API, colonne conservée en base

- Date : 2026-11-16
- Statut : à valider par Thomas
- Décidé par : Lot 1, par défaut ; en attente de revue de Thomas
- Tickets : TOK-113

## Contexte
Le libellé relatif au premier du lot (`buy_label`) est remplacé par un libellé absolu.

## Options
- Supprimer le champ de l'API
- Le conserver

## Décision
Champ supprimé de la réponse API (remplacé par `signal_label`) ; colonne laissée en base.

## Raison
« Plus aucun libellé relatif » ; la colonne en base évite de toucher au scoring.

## Conséquences
Changement de contrat d'API : tout consommateur de `buy_label` doit passer à `signal_label`.

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lot 1)

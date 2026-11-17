# 0045 — GET /archetypes/{slug} : nouvel endpoint sans calcul statistique nouveau

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Lot 4, par défaut ; validée par Thomas le 2026-11-17 (revue du matin)
- Tickets : TOK-101

## Contexte
Aucun endpoint ne servait l'historique mensuel ni les cartes d'attache par archétype.

## Options
- Calculer de nouvelles statistiques
- Recomposer des colonnes déjà servies

## Décision
Endpoint créé sur des tables de `SERVED_TABLES` (`meta_scores`, `ban_radar`, `ocg_archetype_scores`, `boutique_buy_signals`) ; champs ajoutés `slug`, `decks`, `archetype_slug` ; rien de retiré.

## Raison
Aucun calcul statistique nouveau, donc pas de passage par `data-scientist-ygo`.

## Conséquences
Part et tier sur la fenêtre de la tier list, cartes clés sur celle du Ban Radar (deux fenêtres sur la même page, chacune avec son pied).

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lot 4)

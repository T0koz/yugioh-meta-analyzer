# 0044 — URL d'archétype : /archetype/{slug}, slug calculé et servi par l'API

- Date : 2026-11-16
- Statut : à valider par Thomas
- Décidé par : Lot 4, par défaut ; en attente de revue de Thomas
- Tickets : TOK-101

## Contexte
Les noms d'archétypes contiennent `/`, `.`, `@`, `☆` ; un `%2F` est décodé ou refusé selon le serveur.

## Options
- Nom brut encodé dans l'URL
- Slug a-z 0-9 et tiret calculé par l'API

## Décision
`/archetype/{slug}`, slug calculé par l'API (`backend/app/slugs.py`) et servi (`slug`, `archetype_slug`) ; le front ne le recalcule jamais.

## Raison
Une seule règle de slug, côté API ; aucune collision sur 231 archétypes.

## Conséquences
Réutilisé pour le sitemap et pour TOK-114.

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lot 4)

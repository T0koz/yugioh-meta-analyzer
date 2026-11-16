# 0041 — Données de Kewl Tune figées dans le front pour l'exemple de l'accueil

- Date : 2026-11-16
- Statut : à valider par Thomas
- Décidé par : Lot 2, par défaut ; en attente de revue de Thomas
- Tickets : TOK-106

## Contexte
Le graphique « preuve » a besoin des parts OCG mensuelles ; `meta_scores_ocg` n'est pas dans la base de service.

## Options
- Nouvel endpoint et table servie
- Données figées dans `frontend/src/lib/proof-data.ts`

## Décision
Données figées (relevé en lecture seule du 2026-11-16), source et date affichées sous le graphique.

## Raison
Pas d'écriture en base ni de nouvel endpoint cette nuit ; réversible.

## Conséquences
À relever de nouveau quand la base change ; un endpoint pourra le remplacer avec TOK-101.

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lot 2)

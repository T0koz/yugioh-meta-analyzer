# 0048 — Tests visuels sur une fausse API rejouant des réponses JSON commitées

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Lot 5, par défaut ; validée par Thomas le 2026-11-17 (revue du matin)
- Tickets : TOK-100

## Contexte
Les données changent chaque lundi, ce qui rendrait les captures instables.

## Options
- Masquer le contenu variable
- Figer la base

## Décision
Fausse API rejouant 12 réponses JSON commitées (268 ko), build dans `.next-visual`.

## Raison
Une base ne se commite pas (dépôt public) ; masquer viderait les pages ; la suite tourne sans base ni backend.

## Conséquences
Si la forme d'une réponse d'API change : `--refresh-fixtures`, sinon la suite teste un contrat périmé. Références en WebP sans perte (3,4 Mo).

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lot 5)

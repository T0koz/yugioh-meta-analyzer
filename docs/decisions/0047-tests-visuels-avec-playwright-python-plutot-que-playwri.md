# 0047 — Tests visuels avec Playwright Python plutôt que @playwright/test

- Date : 2026-11-16
- Statut : à valider par Thomas
- Décidé par : Lot 5, par défaut ; en attente de revue de Thomas
- Tickets : TOK-100

## Contexte
Outil des tests visuels à choisir.

## Options
- `@playwright/test` côté front
- Playwright Python + Pillow, `scripts/visual_tests.py`

## Décision
Playwright Python + Pillow.

## Raison
Déjà installés avec Chromium ; aucune dépendance ajoutée ; même langage que `check.py`.

## Conséquences
Option `python scripts/check.py --visuel` (45 s, build dépendant du réseau pour les polices Google) : hors défaut, rappel non bloquant.

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lot 5)
- `docs/tests-visuels.md`

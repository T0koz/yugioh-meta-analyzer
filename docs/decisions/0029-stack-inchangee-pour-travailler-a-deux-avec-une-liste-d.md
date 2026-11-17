# 0029 — Stack inchangée pour travailler à deux, avec une liste de frictions à traiter

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Claude (avis TOK-111) ; à valider par Thomas pour les points non faits
- Tickets : TOK-111

## Contexte
Question posée : la stack tient-elle à deux ?

## Options
- Changer de stack (Postgres, orchestrateur, Git LFS…)
- Garder la stack et traiter l'outillage autour

## Décision
Aucun changement de stack. Pas de Postgres, pas d'orchestrateur (Airflow, Dagster, Prefect), pas de pull requests obligatoires, pas de DVC ni de Git LFS. À traiter : outillage (`check.py`, `requirements.txt` racine, chemins relatifs : faits), `nbstripout`, calculs qui écrivent en base dans `scripts/` plutôt que dans des notebooks.

## Raison
Ce qui gêne à deux est l'outillage, pas les technologies (tests, installation, jobs liés au Mac de Thomas, notebooks).

## Conséquences
Restent à décider : `git rm --cached data/raw/cards.json` (32 Mo), où tournent les jobs (avec TOK-35), tests de non-régression sur les chiffres clés.

## Sources
- `docs/collaboration/avis-stack.md`

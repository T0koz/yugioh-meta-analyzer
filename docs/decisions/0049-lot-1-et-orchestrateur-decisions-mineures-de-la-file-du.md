# 0049 — Lot 1 et orchestrateur : décisions mineures de la file du soir

- Date : 2026-11-16
- Statut : à valider par Thomas
- Décidé par : Lot 1 et orchestrateur, par défaut ; en attente de revue de Thomas
- Tickets : TOK-113

## Contexte
Registre des décisions de moindre portée prises par défaut pendant ce lot. Chaque ligne est une décision, rangée ici pour ne pas multiplier les notes d'une ligne.

## Options
- Pour chaque ligne, voir la source (question et alternatives).

## Décision

  - Table `ocg_archetype_scores` absente de `serving.db` → **ajoutée à `SERVED_TABLES`, l'API renvoie `signal_label = null` tant que la base n'est pas reconstruite** (pas d'écriture dans la base de référence)
  - `serving.db` ne portait pas le nouveau libellé pour les lots front → **reconstruite avec `build_serving_db.py` après sauvegarde dans `data/backup_serving_avant_lot01_20261116.db` ; `yugioh.db` non touchée** (dérivé reproductible, réversible)
  - `main` local a 4 commits d'avance sur `origin/main` (briefs non poussés) → **branche `claude/front-nuit-17-11` créée depuis `main` local, sans pousser** (les briefs n'existent que dans ces commits)
  - Où fusionner les lots → **dépôt principal basculé sur `claude/front-nuit-17-11` (retour : `git checkout main`)** (seul checkout avec les bases et `node_modules`)
  - Qui fusionne (`regles.md` dit la session, l'orchestrateur dit lui-même) → **l'orchestrateur fusionne, lance `check.py`, écrit le compte rendu ; les sessions s'arrêtent après leur dernier commit** (un seul acteur écrit sur la branche d'intégration)
  - Fichiers de planning non suivis invisibles depuis un worktree → **commités tels quels sur la branche d'intégration** (un fichier non commité n'existe pas dans un worktree)
  - Brief du benchmark « pas de commit » contre la file « tout s'empile » → **la session commite sur sa branche, l'orchestrateur fusionne** (sans commit rien ne sort du worktree)
  - Thomas demande de lancer la suite sans attendre le lot 6 → **lot 7 en parallèle du lot 6, exception ponctuelle à « une seule session à la fois »** (aucun fichier commun ; retour à une session à la fois dès le lot 8)

## Raison
Une raison est donnée entre parenthèses pour chaque ligne.

## Conséquences
À relire par Thomas ligne par ligne ; chacune est réversible sauf mention contraire dans la source.

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lot 1 et orchestrateur)

# Yugioh Meta Analyzer — instructions Claude Code

@context.md
@BACKLOG.md
@frontend/AGENTS.md

## Avec qui tu travailles

Deux personnes poussent directement sur `main`, **sans revue**, sur un dépôt **public** :
**Thomas** (fondateur) et une **collaboratrice data scientist**. Si tu ne sais pas laquelle
des deux est en face de toi, regarde `git config user.name` ou demande.

- Réponds **en français**.
- Le but est de **livrer**, pas de donner des indices. Mais **explique tes choix** :
  Thomas suit le bootcamp Le Wagon Data Science & AI (oct. → déc. 2026) et veut
  comprendre le pourquoi, surtout côté stats / ML. Avec la collaboratrice, va droit aux
  arguments statistiques, sans vulgariser.
- Quand une **décision** est à prendre, prépare un **formulaire à copier-coller** :
  options en `[ ]` / `[x]`, ta recommandation pré-cochée, une ligne « Commentaire libre ».
- **Commits : tu proposes, la personne valide. Push : jamais sans son accord explicite**,
  et jamais si `python scripts/check.py` échoue. Jamais `git push --force` sur `main`,
  jamais `--no-verify` de ta propre initiative.
- Après chaque fonctionnalité, mets à jour `context.md` (pièges, résultats) et
  `BACKLOG.md` (statut des tickets TOK). C'est la mémoire du projet.
- Linear (tickets TOK) : MCP à reconnecter avant toute synchro.

## Travailler à deux sans casser (règles complètes : `docs/ONBOARDING.md` §8)

- **Avant de pousser : `python scripts/check.py`.** Il choisit seul les vérifications selon
  ce qui a changé (secrets et fichiers interdits, `WEIGHTS`, tsc + eslint, `SERVED_TABLES`,
  test de fumée sur `yugioh.db` et `serving.db`, backtest si le scoring bouge). Une étape
  « ignorée » n'est pas une étape réussie : dis-le.
- **`git pull --rebase` avant de commencer et avant de pousser** : l'autre a peut-être
  poussé entre-temps (surtout `context.md` et `BACKLOG.md`).
- **Dépôt public** : jamais de `.env`, de base `.db`, de clé ou de mot de passe dans un commit
  (`HANDOFF.md` non plus). Les identifiants vont dans `.env`, exclu par `.gitignore`.
- **Une seule base de référence** : celle de Thomas, mise à jour par le job du lundi. La
  copie de la collaboratrice est un bac à sable. Ce qui devient officiel passe par du
  **code commité**, jamais par des tables échangées à la main.
- **`data/prediction_log.jsonl`** n'est commité que par Thomas (c'est la preuve datée des
  prédictions) : ne lance pas `log_predictions.py` sur une copie.
- Un calcul qui écrit en base va dans `scripts/`, pas dans un notebook (relecture et fusion
  impossibles à deux sur du JSON).

## Lancer le projet

- Backend : `cd backend && ../.venv/bin/uvicorn app.main:app --reload --port 8000`
  → `http://localhost:8000/api/v1`
- Front : `cd frontend && npm run dev` → `http://localhost:3000`
- Vérifications : `python scripts/check.py` (tout ce qui concerne tes changements ;
  `--all` pour tout). Hook optionnel : `git config core.hooksPath .githooks`.
  Pour un vrai test navigateur, Playwright est installé dans `.venv`.

## Pièges à ne pas refaire

- **Scoring Ban Radar** : tout changement passe par
  `python scripts/build_ban_radar.py --backtest`. Les `WEIGHTS` sont dupliqués entre
  `scripts/build_ban_radar.py` et `backend/app/routers/ban_radar.py` : les garder alignés.
  Ne jamais baisser `BACKTEST_MIN_DECKS` (600) pour faire entrer des listes.
- **`deck_cards`** : index unique `(deck_id, card_name, zone)` (créé par
  `fetch_tournament_decks.py`). Purger les lignes d'un deck et agréger les cartes
  éclatées avant réinsertion, sinon `IntegrityError`.
- Champs yugiohmeta tantôt chaîne, tantôt objet `{_id, name}` → toujours passer par `extract_name`.
- **SQLite** : tout endpoint sync passe par `get_db()` (`check_same_thread=False`).
- `GET /cards/search` déclaré **avant** `GET /cards/{name}`.
- **Nouvel endpoint** → ajouter ses tables à `SERVED_TABLES` dans `scripts/build_serving_db.py`
  et lancer `python scripts/build_serving_db.py --check`, sinon `serving.db` casse en prod.
- Jointure `cards` ↔ noms issus de `deck_cards` : `cards.name` porte `<P>`/`<C>`/`<Q>` →
  `REPLACE(REPLACE(c.name,'<',''),'>','')`.
- **Next.js 16** : lire `node_modules/next/dist/docs/` avant de toucher au cache/fetch ;
  `rm -rf frontend/.next` si une donnée fraîche de l'API n'apparaît pas.
- `meta_score` plafonne ~0.15 : toute barre se recalibre sur le max du dataset.
- Toute page qui utilise `CardChip` / le panneau de survol est enveloppée dans
  `<HoverPreviewProvider>` + `<HoverPreviewPanel />`.

## Agents spécialisés (`.claude/agents/`)

- **data-scientist-ygo** : scoring, modèles, backtest, data leakage. À solliciter pour
  toute modification du Ban Radar, des notebooks de prédiction ou du clustering.
- **gardien-donnees** : scripts d'ingestion, schéma SQLite, base de service. À solliciter
  pour tout script qui écrit en base ou tout nouvel endpoint.

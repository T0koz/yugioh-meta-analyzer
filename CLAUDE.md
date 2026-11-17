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
- **Front : toujours le modèle le plus puissant disponible** (Fable, sinon Opus), pour un rendu visuellement
  au top. Le modèle économique sert aux données, à la doc et aux tâches mécaniques.
- Après chaque fonctionnalité, mets à jour `context.md` (pièges, résultats) et
  `BACKLOG.md` (statut des tickets TOK). C'est la mémoire du projet.
- Linear (tickets TOK) : MCP à reconnecter avant toute synchro.
- **Règle d'or : une seule session de travail à la fois ; une deuxième seulement sur demande explicite de
  Thomas.** Une session ne lance ni autre session ni sous-agent de sa propre initiative.
  Précision du 17/11 (files d'orchestrateur) : un lot à la fois ; une deuxième session seulement si la première est
  bloquée par une attente longue et passive (téléchargement, build long, attente de validation), sur des fichiers
  différents, et jamais plus de deux sessions en même temps.
- **Rigueur statistique (principe de Thomas, 17/11)** : tout score, prédiction, seuil ou libellé affiché est
  estimé à partir des données, validé hors échantillon dans le temps, comparé à une méthode naïve (hasard,
  popularité, « le mois dernier ») et affiché avec son incertitude. Un réglage à la main n'est acceptable que
  s'il est déclaré comme tel. Toute session qui crée ou modifie un score sollicite `data-scientist-ygo`.
- **Journal de décisions** : toute décision structurante (architecture, données, design, process) est notée dans
  `docs/decisions/` (une note par décision, modèle et index dans `docs/decisions/README.md`). Une décision prise
  par défaut en autonomie va d'abord dans le `decisions-prises.md` du jour, et rejoint le journal après validation.
- **Plan mode** : ne le propose à Thomas que lorsqu'il est vraiment la solution (changement large, risqué ou mal
  cadré, que le brief n'a pas préparé), jamais par défaut ni par habitude.
- **Garde-fou** (`.claude/settings.json`, hook `.claude/hooks/garde_fou.py`) : `git push`, `--force`, `--no-verify`
  et `rm -rf` hors `.claude/worktrees/` sont refusés. Le push, c'est Thomas, depuis son terminal, après
  `python scripts/check.py`. `/fin-de-journee` propose la mise à jour de `context.md` et `BACKLOG.md` (sans commiter).

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

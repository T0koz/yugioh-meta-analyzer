# Yugioh Meta Analyzer — instructions Claude Code

@context.md
@BACKLOG.md
@frontend/AGENTS.md

## Travailler avec Thomas

- Réponds **en français**.
- Le but est de **livrer**, pas de donner des indices. Mais **explique tes choix** :
  Thomas suit le bootcamp Le Wagon Data Science & AI (oct. → déc. 2026) et veut
  comprendre le pourquoi, surtout côté stats / ML.
- Quand une **décision** est à prendre, prépare un **formulaire à copier-coller** :
  options en `[ ]` / `[x]`, ta recommandation pré-cochée, une ligne « Commentaire libre ».
- **Commits : tu proposes, il valide. Push : jamais sans lui.**
- Après chaque fonctionnalité, mets à jour `context.md` (pièges, résultats) et
  `BACKLOG.md` (statut des tickets TOK). C'est la mémoire du projet.
- Linear (tickets TOK) : MCP à reconnecter avant toute synchro.

## Lancer le projet

- Backend : `cd backend && ../.venv/bin/uvicorn app.main:app --reload --port 8000`
  → `http://localhost:8000/api/v1`
- Front : `cd frontend && npm run dev` → `http://localhost:3000`
- Vérification front : `npx tsc --noEmit` et `npx eslint src/...` depuis `frontend/`.
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

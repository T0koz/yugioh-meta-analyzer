### ✅ Backend FastAPI — Livré (TOK-31, 2026-08-05)

**Stack :** FastAPI + sqlite3 stdlib (pas d'ORM), lecture directe de `data/yugioh.db`
**Dossier :** `backend/app/`
**Dev :** `.venv/bin/uvicorn app.main:app --reload --port 8000` (lancé depuis `backend/`, config dans `.claude/launch.json` nom `"backend"`) → `http://localhost:8000/api/v1`

**Structure :**
```
backend/app/
├── main.py            # FastAPI app + CORS (ouvert *) + include_routers, prefix /api/v1
├── db.py              # get_db() : connexion sqlite3.Row vers data/yugioh.db
├── schemas.py         # Pydantic models miroir de frontend/src/types/index.ts
├── labels.py          # Mappings DB → front : tier ("field"→"Rogue"), trend_label (emoji FR → Rising/Stable/Declining), pred_direction (↑→↓ → idem)
└── routers/
    ├── meta.py        # GET /meta/tier-list, /meta/evolution, /meta/predictions
    ├── boutique.py    # GET /boutique/signals, /early-signals
    ├── graph.py       # GET /graph/synergies (nodes card_graph_metrics + edges card_cooccurrence)
    └── cards.py       # GET /cards/{name} (fuzzy match), POST /simulate-ban
```

**Points d'attention (à connaître avant de retoucher) :**
- `meta_score` (formule `sqrt(share × placement_score_norm)`) ne dépasse jamais ~0.15 en pratique — toute UI qui l'affiche en barre doit se recalibrer en relatif au max du dataset, pas en absolu sur [0,1] (corrigé sur tier-list et predictions)
- `boutique_buy_signals` a une ligne par **(archétype, carte)** : une staple générique (ex: Super Polymerization) apparaît sous plusieurs archétypes → toute clé React doit combiner les deux, pas juste `card_name`
- `/simulate-ban` : `bridge_score` vient de `card_impact` (35 cartes seulement, sinon 0) ; `fragmentation` est une approximation (betweenness normalisée sur le max du dataset, pas de métrique de fragmentation précalculée) ; `community_id = -1` si la carte n'a pas de `top_archetype` dans `card_impact`
- Pas de table card→communauté : `/graph/synergies` groupe par `cards.archetype`, pas par `graph_communities.community_id` (qui n'est qu'un résumé par communauté, 63 lignes)
- **⚠ Bug corrigé (2026-08-05)** : `sqlite3.ProgrammingError` intermittente sur tous les endpoints — FastAPI exécute les routes `def` (sync) dans un threadpool, `sqlite3.connect()` sans `check_same_thread=False` casse dès que la requête tombe sur un thread différent de celui qui a ouvert la connexion. Fix dans `db.py`. **Si un nouvel endpoint sync est ajouté et manipule `db` directement sans passer par `get_db()`, il aura le même problème.**
- `GET /cards/search` est enregistré **avant** `GET /cards/{name}` dans `cards.py` — sinon FastAPI matche `/cards/search` comme `{name}="search"`. Respecter cet ordre pour toute nouvelle route `/cards/...`.

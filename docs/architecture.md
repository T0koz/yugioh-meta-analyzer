# Architecture — Yu-Gi-Oh! Meta Analyzer

## Architecture Pattern

**Pipeline monolith** — data flows one-way through numbered phases. Each notebook is a self-contained transformation step that reads from SQLite, computes, and writes back. The Streamlit dashboard is a pure read layer (Phases 1–4). Phase 5 adds a Next.js public frontend + FastAPI backend.

```
YGOPRODeck API ──────────────────┐
yugiohmeta.com ──────────────────┤
Yugipedia (scraping) ────────────┤→ scripts/ (ETL) → yugioh.db → notebooks/ → app.py (Streamlit)
YouTube (transcripts) ───────────┤                                    │
Cardmarket prices (daily cron) ──┘                                    └→ serving.db → FastAPI
                                                                              ↑
                                                                     Next.js frontend (frontend/)
```

---

## Phase 5 — Frontend Architecture (mise à jour 2026-11-18)

### Stack

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Frontend | Next.js 16 + React 19 + TypeScript | App Router ; lire `node_modules/next/dist/docs/` avant de toucher au cache (`frontend/AGENTS.md`) |
| Styling | Tailwind CSS v4, design system « Braise vivante » (`docs/design-system.md`) | Tokens dans `globals.css`, contrôles dans `components/ds/control.tsx` |
| Charts | SVG maison calculés avec `d3-array`, `d3-shape` (client) et `d3-scale` (serveur) | recharts supprimé (TOK-99) ; graphe : vis-network |
| API client | `fetch` natif | `src/lib/api.ts`, `apiBaseUrl()` : `API_URL` → `BACKEND_URL` + `/api/v1` → `NEXT_PUBLIC_API_URL` → `localhost:8000` |
| Images de cartes | Hébergement propre (`data/card-images/`, Cloudflare R2 prévu) | `src/lib/card-images.ts`, `NEXT_PUBLIC_CARD_IMAGES_URL` (TOK-92) |
| Backend | FastAPI (TOK-31 ✅) | Lecture seule sur SQLite, préfixe `/api/v1` |
| Deploy | Vercel Services (`vercel.json`), préparé, rien de déployé (TOK-35) | Base de service embarquée (`serving.db`, ~12 Mo), guide `docs/deploiement.md` |

### Pages livrées (`frontend/src/app/`)

Toutes consomment l'API réelle via `src/lib/api.ts` ; chaque page passe par `pageMetadata` (`src/lib/seo.ts`).

| Route | Contenu | Endpoint(s) |
|-------|---------|-------------|
| `/` | Accueil : exemple Kewl Tune (parts TCG et OCG), bento d'outils, méthode | `GET /archetypes/{slug}`, plusieurs autres |
| `/tier-list` | Tier list calculée à la volée, bandes de Wilson, tiers « limite » | `GET /meta/tier-list` |
| `/evolution` | Courbes de part des decks (SVG), bande de Wilson | `GET /meta/evolution` |
| `/predictions` | Haltères observé → prévu | `GET /meta/predictions` |
| `/archetype/{slug}` | Part, tier, tendance, parts mensuelles TCG et OCG, cartes clés, signal boutique | `GET /archetypes/{slug}` |
| `/decks`, `/decks/{slug}` | Index et fiche de composition, 5 listes récentes | `GET /decks`, `GET /decks/{slug}` |
| `/boutique` | Signaux par archétype, fenêtre d'arrivée, courbes de prix | `GET /boutique/signals`, `GET /boutique/prices` |
| `/early-signals` | Signaux précoces | `GET /early-signals` |
| `/graph` | Graphe de co-occurrences (vis-network) | `GET /graph/synergies` |
| `/ban` | Onglets Radar, Historique, Cartes à impact, Simulateur (`?tab=`) | `GET /ban-radar`, `GET /ban-radar/history`, `GET /card-impact`, `POST /simulate-ban` |
| `/methode` | Méthode, sans formule | — |

Variables d'environnement : voir `frontend/.env.example` et `docs/deploiement.md` (`API_URL` ne va jamais dans Vercel).

---

## Layer 1 — Data Ingestion (scripts/)

Deux chaînes : `scripts/refresh_decks.py` (job du lundi : cartes nouvelles, decks TCG et OCG, banlists, légalité,
puis `refresh_all.py`, `build_serving_db.py` et le contrôle de fraîcheur) et `scripts/refresh_all.py` (tables dérivées,
`--list` affiche l'ordre).

| Script | Source | Output tables | Frequency |
|--------|--------|---------------|-----------|
| `fetch_cards.py` | YGOPRODeck API v7 | `data/raw/cards.json` (JSON seul) | On demand |
| `init_db.py` | cards.json | `cards`, `card_sets`, `card_prices` (rafraîchissement complet, écrase `views_week`) | On demand, jamais dans la chaîne |
| `fetch_new_cards.py` | YGOPRODeck API v7 | `cards` (ajout des cartes absentes, garde de nom) | Weekly (`refresh_decks`, `refresh_all`) |
| `fetch_tournament_decks.py` | yugiohmeta.com (TCG) | `tournament_decks`, `deck_cards` | Weekly (`refresh_decks`) |
| `fetch_ocg_decks.py` | yugiohmeta.com (OCG) | `tournament_decks` (ocg=1), `deck_cards` | Weekly (`refresh_decks`) |
| `fetch_banlist_history.py` | Yugipedia (TCG + OCG) | `banlist_history` | Weekly (`refresh_decks`) |
| `compute_deck_legality.py` | yugioh.db | `deck_legality` | Weekly (`refresh_decks`) |
| `build_banlist_features.py` | yugioh.db | `banlist_features` | `refresh_all` |
| `build_buy_signals.py` | yugioh.db | `boutique_buy_signals` | `refresh_all` |
| `snapshot_prices.py` | YGOPRODeck bulk API | `card_price_history` | `refresh_all` (idempotent par jour) |
| `build_boutique_price_history.py` | yugioh.db | `boutique_price_history` | `refresh_all` |
| `build_early_signals.py` | yugioh.db | `early_card_signals` | `refresh_all` (remplace le notebook 11, lot 20) |
| `build_ban_radar.py` | yugioh.db | `ban_radar` | `refresh_all` |
| `build_card_impact.py` | `ban_radar` | `card_impact` | `refresh_all` |
| `build_archetype_profiles.py` | yugioh.db | `archetype_card_profile`, `archetype_recent_decks`, `archetype_recent_deck_cards` | `refresh_all` |
| `log_predictions.py` | tables de prédiction | `prediction_log`, `data/prediction_log.jsonl` | `refresh_all` (Thomas seul commite le JSONL) |
| `download_card_images.py` | YGOPRODeck images | `data/card-images/` (3 tailles WebP) | `refresh_all` (incrémental) |
| `fetch_banlist_announcements.py` | Yugipedia + sources citées | `banlist_announcements` | `refresh_all` (dernière étape) |
| `build_ban_history.py` | yugioh.db | `ban_backtest_lists`, `ban_backtest_cards` | À la main (hors chaîne) |
| `validate_predictions.py` | `prediction_log` | `prediction_validation` | À la main |
| `build_serving_db.py` | yugioh.db | `data/serving.db` | `refresh_decks` ; `--check` dans `refresh_all` |
| `check_freshness.py` | serving.db + yugioh.db | ligne `fraicheur_tables` de `data/fetch_health.jsonl` | `refresh_decks` (dernière étape), `deploy_prebuilt.py` |
| `setup_impact_tables.py` | yugioh.db | `ban_impact` (sa partie `card_impact` est remplacée par `build_card_impact.py`) | On demand |
| `explore_limitless.py` | Playwright | Diagnostic only | On demand |

Scripts de diagnostic en lecture seule (rien d'affiché ne change) : `diagnose_ban_radar.py`, `diagnose_ban_radar_rangs.py`,
`diagnose_pont_simulateur.py`, `bridge_date.py`, `backtest_early_signals.py`, `build_arrival_survival.py` et
`build_prediction_intervals.py` (écrivent seulement avec `--write`, après formulaire), `evaluate_prediction.py`.
Outillage : `check.py`, `check_copy.py`, `visual_tests.py`, `deploy_prebuilt.py`, `export_db_snapshot.py` ; moteur de combos :
`combos_*.py`, `build_judge_form.py`.

**Key design decisions:**
- `snapshot_prices.py` uses a single bulk API call (~12s for 13,797 cards) instead of per-card requests
- OCG decks share the same `tournament_decks` table as TCG, differentiated by `ocg = 1` flag
- `cards` table includes `image_url` and `image_url_small` columns from YGOPRODeck CDN
- Deck fetchers are **idempotent**: `deck_cards` has a unique index on
  `(deck_id, card_name, zone)` and each deck's rows are purged before reinsertion.
  Re-running them never duplicates.
- `fetch_banlist_history.py` rebuilds `banlist_history` wholesale — Yugipedia is
  the source of truth and amends past lists retroactively. It scrapes both formats
  and stamps a `format` column; do not filter on `list_name LIKE '%TCG%'`, which
  misses the 33 pre-2021 TCG lists that Yugipedia names without a suffix.

---

## Layer 2 — Storage (SQLite)

Single SQLite file at `data/yugioh.db` (~236 MB). No ORM — raw SQL via Python `sqlite3`.

**Serving DB.** The API reads 18 of the 49 tables, and `SERVED_TABLES` copies 20 (two are read by no router:
`archetype_trend`, `meta_tier_list`) — everything it returns is precomputed. `deck_cards` and its indexes alone account for 74% of the file and are
never queried online (notebooks and `build_ban_radar.py` only). `build_serving_db.py`
extracts the served subset into `data/serving.db` (~12 MB), small enough to ship with
the deployment: no persistent volume to provision or back up. The backend resolves
`YGO_DB_PATH` first, falling back to `data/yugioh.db`. The script guards against
drift by scanning router SQL and failing if an endpoint references a table missing
from `SERVED_TABLES`. `scripts/check_freshness.py` (TOK-93) has one freshness rule per served table.

**Table groups:**

| Group | Tables | Purpose |
|-------|--------|---------|
| Raw data | `cards`, `card_sets`, `card_prices`, `card_price_history`, `tournament_decks`, `deck_cards`, `deck_legality`, `banlist_history`, `banlist_announcements`, `archetypes_official`, `archetype_mapping` | Source of truth |
| Co-occurrence | `card_cooccurrence`, `card_cooccurrence_90d`, `card_cooccurrence_side`, `card_cooccurrence_extra`, `card_cooccurrence_elite`, `card_cooccurrence_quarterly`, `archetype_extra_profile` | Synergy signals |
| Graph | `card_graph_metrics`, `graph_communities`, `deck_style_clusters` | Network analysis |
| Meta scoring | `meta_scores`, `meta_scores_ocg`, `meta_scores_regional`, `archetype_trend`, `meta_tier_list`, `meta_predictions`, `banlist_features`, `ban_impact`, `card_impact`, `ban_radar`, `ban_backtest_lists`, `ban_backtest_cards` | Ranking + forecasting |
| Decks | `archetype_card_profile`, `archetype_recent_decks`, `archetype_recent_deck_cards` | Deck composition pages |
| Predictions log | `prediction_log`, `prediction_validation` | Dated proof of predictions |
| NLP | `text_synergies`, `card_mechanic_tags`, `combo_mentions`, `combo_edges`, `combo_edges_global`, `early_card_signals` | Semantic signals |
| Boutique | `boutique_alerts`, `boutique_card_alerts`, `boutique_buy_signals`, `boutique_price_history`, `ocg_archetype_scores` | B2B shop intelligence |

**Key schema decisions:**
- Co-occurrence Jaccard weight = `(1/placement) × exp(-days/365)`, normalized per deck
- `card_price_history` primary key is `(card_id, snapshot_date)` — one row per card per day
- `ban_tcg` column in boutique tables: NULL = legal, 'Limited', 'Semi-Limited', 'Forbidden'
- Banlist status shown or used by the derived tables comes from `banlist_history` (in force on the date), not from `cards.ban_tcg`, frozen at the last `init_db.py`
- Every consumer of decks filters on `deck_legality.legal = 1`

---

## Layer 3 — Analysis Pipeline (notebooks/)

Notebooks are numbered. Those of the weekly chain (02, 04, 05, 10) are run by `scripts/refresh_all.py`; the others are
run by hand and some of their tables are stale (03: graph, TOK-136; 07: `text_synergies`).

| Notebook | Input tables | Output tables | Key algorithm |
|----------|-------------|---------------|---------------|
| `01_exploration.ipynb` | `cards`, `card_prices` | — | Exploratory only |
| `02_cooccurrence.ipynb` | `deck_cards`, `tournament_decks`, `deck_legality` | 6 co-occurrence tables + `archetype_extra_profile` | Weighted Jaccard |
| `03_graph.ipynb` | `card_cooccurrence` | `card_graph_metrics`, `graph_communities` | NetworkX Louvain + betweenness centrality |
| `04_meta_score.ipynb` | `tournament_decks`, `deck_legality` | `meta_scores` (TCG), `meta_scores_ocg`, `archetype_trend` | `sqrt(share × placement_norm)` |
| `05_meta_prediction.ipynb` | `meta_scores`, `banlist_features` | `meta_predictions` | 70 % naïf + 30 % Ridge (AR(1) testé, écarté) |
| `06_card_ban_impact.ipynb` | `deck_cards`, `meta_scores`, `banlist_history` | `ban_impact`, `card_impact` (ancienne version : la table servie vient de `build_card_impact.py`) | Bridge score |
| `07_nlp_text_synergies.ipynb` | `cards` | `text_synergies`, `card_mechanic_tags` | TF-IDF + keyword Jaccard |
| `08_nlp_combos.ipynb` | YouTube transcripts | `combo_mentions`, `combo_edges`, `combo_edges_global` | ASR regex pipeline |
| `09_banlist_history.ipynb` | Yugipedia scraping | `banlist_history` (remplacé par `fetch_banlist_history.py` ; `banlist_features` : `build_banlist_features.py`) | Web scraping |
| `09_ocg_tcg_correlation.ipynb` | `meta_scores` (ocg/tcg) | — | Pearson + lag analysis |
| `10_archetypes_official.ipynb` | YGOPRODeck `/archetypes.php` | `archetypes_official`, `archetype_mapping` | Fuzzy matching |
| `10_boutique_alert_score.ipynb` | `tournament_decks`, `deck_cards`, `deck_legality`, `banlist_history`, `cards` | `boutique_alerts`, `boutique_card_alerts`, `ocg_archetype_scores` (`boutique_buy_signals` : `build_buy_signals.py`) | Alert score, archétypes pas encore en TCG |
| `11_early_card_signal.ipynb` | `cards`, `text_synergies`, `meta_scores` | — (calcul repris par `build_early_signals.py`, lot 20) | Composite signal (views + text + OCG) |
| `12_deck_clustering.ipynb` | `deck_cards` | `deck_style_clusters` | K-Means k=4, silhouette=0.171 |

---

## Layer 4 — Dashboard (app.py)

Streamlit app with 9 pages, pure read-only access to SQLite. All data cached with `@st.cache_data(ttl=300)`.

| Page | Key tables | Description |
|------|-----------|-------------|
| 📊 Tier List | `meta_tier_list`, `meta_scores` | Current meta rankings |
| 📈 Évolution | `meta_scores` | Historical meta share by archetype |
| 🔮 Prédictions | `meta_predictions` | Next-month forecast |
| 🚨 Signal précoce | `early_card_signals` | New cards entering meta |
| 🛒 Signal boutique | `boutique_buy_signals` | B2B shop buy signals with banlist flags |
| 🎮 Combos NLP | `combo_edges_global` | YouTube combo graphs |
| 📜 Banlist historique | `banlist_history` | TCG banlist timeline |
| 🕸️ Graphe synergies | `card_cooccurrence` | Interactive vis-network graph |
| 🚫 Simulateur ban | `card_graph_metrics`, `graph_communities` | Simulate ban impact |

**Run:** `streamlit run app.py` or `bash run.sh`

---

## Key Algorithms

### Meta Score
```
meta_score = sqrt(share × placement_score_norm)
placement_score_norm = 1 / log(1 + avg_placement)
```
Geometric mean of volume (share) and quality (placement). Range ~0–1.

### Weighted Jaccard Co-occurrence
```
weight_deck = (1 / placement) × exp(-days_since_tournament / 365)
W_deck = weight_deck / sum(all_weights)
Jaccard(A,B) = Σ min(W_A, W_B) / Σ max(W_A, W_B)
```

### Prediction Ensemble
```
pred = 0.70 × naive_score + 0.30 × ridge_delta_pred
```
Walk-forward CV (9-month window). Naïf = "no change from last month". Évaluation : `docs/evaluation-prediction.md` ;
intervalles de prévision : TOK-131 (non servis avant formulaire).

### OCG Alert Score (boutique)
```
alert_score = meta_score_ocg × log(1 + avg_views_week_core_cards)
```
Depuis TOK-113 (v3), seuls les archétypes pas encore en TCG sont notés ; le libellé affiché est le rang de l'archétype
parmi les archétypes OCG (`backend/app/signal_label.py`), pas `buy_label`. Score boutique ≈ part OCG (ρ 0,94, audit lot 19).

### Early Card Signal
```
early_score = 0.35 × signal_views + 0.35 × signal_text + 0.30 × signal_ocg
```
Calcul : `scripts/build_early_signals.py` (lot 20), référence = dernier deck TCG, banlist en vigueur à cette date,
cartes déjà en méta exclues. `views_week` figé au 13/06 ; `signal_text` nul (TOK-129).

---

## External APIs

| API | Base URL | Auth | Rate limit | Usage |
|-----|----------|------|------------|-------|
| YGOPRODeck v7 | `https://db.ygoprodeck.com/api/v7/cardinfo.php` | None | 20 req/s | Cards, prices, archetypes |
| yugiohmeta.com | `https://www.yugiohmeta.com/api/v1/top-decks` | None | Unknown | Tournament decklists |
| Yugipedia | Web scraping | None | Be polite | Banlist history |
| YouTube Transcript | `youtube_transcript_api` lib | None | — | Combo NLP |

**YGOPRODeck image CDN:**
- Full: `https://images.ygoprodeck.com/images/cards/{id}.jpg`
- Small: `https://images.ygoprodeck.com/images/cards_small/{id}.jpg`

---

## Phase 5 — Architecture (FastAPI + Next.js)

```
Browser → Next.js (Vercel) → /api/* → FastAPI (Vercel Services) → serving.db (SQLite, read-only, ~12 MB)
```

Préparé (TOK-35, `vercel.json`, `docs/deploiement.md`), rien de déployé au 2026-11-18. Les 16 endpoints sont listés
dans `docs/api-contracts.md`.

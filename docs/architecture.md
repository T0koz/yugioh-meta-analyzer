# Architecture — Yu-Gi-Oh! Meta Analyzer

## Architecture Pattern

**Pipeline monolith** — data flows one-way through numbered phases. Each notebook is a self-contained transformation step that reads from SQLite, computes, and writes back. The Streamlit dashboard is a pure read layer (Phases 1–4). Phase 5 adds a Next.js public frontend + FastAPI backend.

```
YGOPRODeck API ──────────────────┐
yugiohmeta.com ──────────────────┤
Yugipedia (scraping) ────────────┤→ scripts/ (ETL) → yugioh.db → notebooks/ → app.py (Streamlit)
YouTube (transcripts) ───────────┤                                    │
Cardmarket prices (daily cron) ──┘                                    └→ FastAPI (TOK-31)
                                                                              ↑
                                                                     Next.js frontend (frontend/)
```

---

## Phase 5 — Frontend Architecture (2026-08-01)

### Stack

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Frontend | Next.js 15 + TypeScript | App Router, SSR/SSG, Vercel deploy |
| Styling | Tailwind CSS v4 + shadcn/ui | Composants (Table, Badge, Card, Input) |
| Charts | recharts | Line chart évolution méta |
| API client | `fetch` natif | `src/lib/api.ts` → `NEXT_PUBLIC_API_URL` |
| Mock data | `src/lib/mock.ts` | Données statiques en attendant FastAPI |
| Backend | FastAPI (TOK-31 — à faire) | Read-only sur yugioh.db (SQLite) |
| Deploy | Vercel (front) + Railway (back) | TOK-35 — à faire |

### Pages livrées (`frontend/src/app/`)

| Route | Composant | Données |
|-------|-----------|---------|
| `/tier-list` | Tiers colorés T0→Rogue, barre de score, trend | `mockTierList` |
| `/evolution` | Line chart interactif (filtre archétype) | `mockEvolution` |
| `/predictions` | Tableau current vs prédit + delta Δ | `mockPredictions` |
| `/boutique` | Signaux d'achat, badges banlist TCG ⚠ | `mockBoutique` |
| `/early-signals` | Score rings SVG, views/semaine | `mockEarlySignals` |
| `/graph` | SVG statique placeholder (vis-network = TOK-33) | Hardcodé |
| `/ban-simulator` | Formulaire → bridge score + archetypes impactés | `MOCK_RESULTS` |

### Brancher l'API (quand TOK-31 sera livré)

Dans chaque page, remplacer :
```typescript
// import { mockXxx } from "@/lib/mock";
import { api } from "@/lib/api";
const data = await api.tierList(); // ou api.boutique(), etc.
```

Variable d'env à ajouter dans Vercel :
```
NEXT_PUBLIC_API_URL=https://api.yugioh-meta.railway.app/api/v1
```

---

## Layer 1 — Data Ingestion (scripts/)

| Script | Source | Output tables | Frequency |
|--------|--------|---------------|-----------|
| `fetch_cards.py` | YGOPRODeck API v7 | `data/raw/cards.json` | On banlist update |
| `init_db.py` | cards.json | `cards`, `card_sets`, `card_prices` | After fetch_cards |
| `fetch_tournament_decks.py` | yugiohmeta.com (TCG) | `tournament_decks`, `deck_cards` | Weekly |
| `fetch_ocg_decks.py` | yugiohmeta.com (OCG) | `tournament_decks` (ocg=1), `deck_cards` | Weekly |
| `snapshot_prices.py` | YGOPRODeck bulk API | `card_price_history` | Daily 09:00 (cron) |
| `setup_impact_tables.py` | yugioh.db | `ban_impact`, `card_impact` | On demand |
| `explore_limitless.py` | Playwright | Diagnostic only | On demand |

**Key design decisions:**
- `snapshot_prices.py` uses a single bulk API call (~12s for 13,797 cards) instead of per-card requests
- OCG decks share the same `tournament_decks` table as TCG, differentiated by `ocg = 1` flag
- `cards` table includes `image_url` and `image_url_small` columns from YGOPRODeck CDN

---

## Layer 2 — Storage (SQLite)

Single SQLite file at `data/yugioh.db` (~150 MB). No ORM — raw SQL via Python `sqlite3`.

**Table groups:**

| Group | Tables | Purpose |
|-------|--------|---------|
| Raw data | `cards`, `card_sets`, `card_prices`, `card_price_history`, `tournament_decks`, `deck_cards`, `banlist_history`, `archetypes_official`, `archetype_mapping` | Source of truth |
| Co-occurrence | `card_cooccurrence`, `card_cooccurrence_90d`, `card_cooccurrence_side`, `card_cooccurrence_extra`, `card_cooccurrence_elite`, `card_cooccurrence_quarterly`, `archetype_extra_profile` | Synergy signals |
| Graph | `card_graph_metrics`, `graph_communities`, `deck_style_clusters` | Network analysis |
| Meta scoring | `meta_scores`, `meta_scores_regional`, `archetype_trend`, `meta_tier_list`, `meta_predictions`, `banlist_features`, `ban_impact`, `card_impact` | Ranking + forecasting |
| NLP | `text_synergies`, `card_mechanic_tags`, `combo_mentions`, `combo_edges`, `combo_edges_global`, `early_card_signals` | Semantic signals |
| Boutique | `boutique_alerts`, `boutique_card_alerts`, `boutique_buy_signals` | B2B shop intelligence |

**Key schema decisions:**
- Co-occurrence Jaccard weight = `(1/placement) × exp(-days/365)`, normalized per deck
- `card_price_history` primary key is `(card_id, snapshot_date)` — one row per card per day
- `ban_tcg` column in boutique tables: NULL = legal, 'Limited', 'Semi-Limited', 'Forbidden'
- `tcg_compat_ratio` in `boutique_alerts` adjusts OCG signal for TCG banlist reality

---

## Layer 3 — Analysis Pipeline (notebooks/)

Notebooks are numbered and must be executed in order to rebuild all DB tables from scratch.

| Notebook | Input tables | Output tables | Key algorithm |
|----------|-------------|---------------|---------------|
| `01_exploration.ipynb` | `cards`, `card_prices` | — | Exploratory only |
| `02_cooccurrence.ipynb` | `deck_cards`, `tournament_decks` | 6 co-occurrence tables + `archetype_extra_profile`, `deck_style_clusters` | Weighted Jaccard + K-Means |
| `03_graph.ipynb` | `card_cooccurrence` | `card_graph_metrics`, `graph_communities` | NetworkX Louvain + betweenness centrality |
| `04_meta_score.ipynb` | `tournament_decks`, `meta_tier_list` | `meta_scores`, `archetype_trend`, `meta_tier_list` | `sqrt(share × placement_norm)` |
| `05_meta_prediction.ipynb` | `meta_scores`, `banlist_features` | `meta_predictions` | Ridge + AR(1) + Naïf blend |
| `06_card_ban_impact.ipynb` | `deck_cards`, `meta_scores`, `banlist_history` | `ban_impact`, `card_impact` | Bridge score |
| `07_nlp_text_synergies.ipynb` | `cards` | `text_synergies`, `card_mechanic_tags` | TF-IDF + keyword Jaccard |
| `08_nlp_combos.ipynb` | YouTube transcripts | `combo_mentions`, `combo_edges`, `combo_edges_global` | ASR regex pipeline |
| `09_banlist_history.ipynb` | Yugipedia scraping | `banlist_history`, `banlist_features` | Web scraping + feature engineering |
| `09_ocg_tcg_correlation.ipynb` | `meta_scores` (ocg/tcg) | — | Pearson + lag analysis |
| `10_archetypes_official.ipynb` | YGOPRODeck `/archetypes.php` | `archetypes_official`, `archetype_mapping` | Fuzzy matching |
| `10_boutique_alert_score.ipynb` | `meta_scores`, `cards`, `boutique_*` | `boutique_alerts`, `boutique_card_alerts`, `boutique_buy_signals` | Alert score + TCG compat filter |
| `11_early_card_signal.ipynb` | `cards`, `text_synergies`, `meta_scores` | `early_card_signals` | Composite signal (views + text + OCG) |
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
Walk-forward CV (9-month window), Spearman ρ ≈ +0.65. Naïf = "no change from last month".

### OCG Alert Score (boutique)
```
alert_score = meta_score_ocg × log(1 + avg_views_week_core_cards)
alert_score_adjusted = alert_score × tcg_compat_ratio
tcg_compat_ratio = Σ(freq × ban_weight) / Σ(freq)
ban_weight: Forbidden=0, Limited=0.5, Semi-Limited=0.75, Legal=1.0
```

### Early Card Signal
```
early_score = 0.35 × signal_views + 0.35 × signal_text + 0.30 × signal_ocg
```
Scope: cards released in TCG since Jan 2026 OR OCG since Jun 2025.

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

## Phase 5 — Planned Architecture (FastAPI + React)

```
Browser → React (Vercel) → FastAPI (Railway/Render) → SQLite (read-only)
```

Planned endpoints (TOK-31):
- `GET /api/meta/tier-list` → meta_tier_list + meta_scores
- `GET /api/meta/evolution` → meta_scores time series
- `GET /api/predictions` → meta_predictions
- `GET /api/boutique/signals` → boutique_buy_signals
- `GET /api/graph/synergies` → card_cooccurrence
- `GET /api/early-signals` → early_card_signals
- `POST /api/simulate-ban` → simulate card removal from graph

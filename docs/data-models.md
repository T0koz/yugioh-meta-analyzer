# Data Models — Yu-Gi-Oh! Meta Analyzer

Single SQLite database: `data/yugioh.db` (~236 MB, 49 tables au 2026-11-18). All tables documented below; effectifs
relevés le 2026-11-18 sur la base de référence (ils changent à chaque job du lundi).
`data/serving.db` (~12 MB) is a generated subset holding only the 20 tables of `SERVED_TABLES`
(`scripts/build_serving_db.py`) ; leur fraîcheur est contrôlée par `scripts/check_freshness.py` (TOK-93).

---

## Group 1 — Raw Card Data

### `cards` — 14,084 rows
Primary card catalog from YGOPRODeck API v7.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | YGOPRODeck card ID |
| `name` | TEXT NOT NULL | Card name (unique) |
| `type` | TEXT | Card type (e.g. "Effect Monster", "Quick-Play Spell") |
| `frame_type` | TEXT | Visual frame (effect, spell, trap, fusion, synchro, xyz, link...) |
| `desc` | TEXT | Full card effect text |
| `archetype` | TEXT | Official archetype (from Konami) |
| `atk` | INTEGER | ATK value (null for non-monsters) |
| `def` | INTEGER | DEF value (null for link/non-monsters) |
| `level` | INTEGER | Level/Rank (null for link monsters) |
| `race` | TEXT | Monster type (Warrior, Spellcaster, Dragon...) |
| `attribute` | TEXT | Element (DARK, LIGHT, WATER, FIRE, WIND, EARTH, DIVINE) |
| `link_val` | INTEGER | Link rating (null for non-link) |
| `scale` | INTEGER | Pendulum scale (null for non-pendulum) |
| `ban_tcg` | TEXT | TCG banlist status: NULL=legal, 'Limited', 'Semi-Limited', 'Forbidden' |
| `ban_ocg` | TEXT | OCG banlist status (same values) |
| `ban_goat` | TEXT | GOAT format banlist status |
| `tcg_date` | TEXT | TCG release date (YYYY-MM-DD) |
| `ocg_date` | TEXT | OCG release date (YYYY-MM-DD) |
| `has_effect` | INTEGER | 1 if card has effect text |
| `views` | INTEGER | Total views on YGOPRODeck |
| `views_week` | INTEGER | Views in the past week (early signal) |
| `md_rarity` | TEXT | Master Duel rarity |
| `image_url` | TEXT | Full card image URL (YGOPRODeck CDN) |
| `image_url_small` | TEXT | Small card image URL |

### `card_sets` — 43,669 rows
Which booster set each card was printed in.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK (autoincrement) | |
| `card_id` | INTEGER FK→cards.id | |
| `set_name` | TEXT | Full set name |
| `set_code` | TEXT | Set code (e.g. "LEDE-EN001") |
| `set_rarity` | TEXT | Print rarity (Common, Rare, SR, UR...) |
| `set_price` | REAL | Price for this specific printing |

### `card_prices` — 14,084 rows
Static price snapshot from DB initialization (baseline 2026-06-13).

| Column | Type | Description |
|--------|------|-------------|
| `card_id` | INTEGER PK FK→cards.id | |
| `cardmarket_price` | REAL | Cardmarket price (€) |
| `tcgplayer_price` | REAL | TCGPlayer price ($) |
| `ebay_price` | REAL | eBay price |
| `amazon_price` | REAL | Amazon price |
| `coolstuffinc_price` | REAL | CoolStuffInc price |

### `card_price_history` — 166,882 (13 relevés au 2026-11-18) rows (grows daily)
Daily price snapshots via bulk API call (cron 09:00).

| Column | Type | Description |
|--------|------|-------------|
| `card_id` | INTEGER PK | |
| `card_name` | TEXT | Card name (denormalized for query convenience) |
| `snapshot_date` | TEXT PK | ISO date (YYYY-MM-DD) |
| `cardmarket_price` | REAL | Cardmarket price that day (€) |
| `tcgplayer_price` | REAL | TCGPlayer price that day ($) |

**Note:** `(card_id, snapshot_date)` is the composite primary key.

---

## Group 2 — Tournament Data

### `tournament_decks` — 23,948 rows
Tournament top-cut decklists from yugiohmeta.com.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | yugiohmeta deck ID |
| `author` | TEXT | Player name |
| `archetype` | TEXT | Archetype label (from yugiohmeta) |
| `tournament_type` | TEXT | Event type (YCS, Regional, Nationals, WCQ, Premiere Event, World Championship) |
| `tournament_location` | TEXT | Location (often NULL) |
| `placement` | INTEGER | Final placement (1 = winner) |
| `created` | TEXT | Tournament date |
| `uploaded` | TEXT | Upload timestamp |
| `ocg` | INTEGER | 0=TCG deck, 1=OCG deck |
| `illegal` | INTEGER | 1 if deck contains illegal cards |
| `incomplete` | INTEGER | 1 if deck is incomplete |

### `deck_cards` — 1,026,945 rows
Individual card entries per deck. One row per `(deck_id, card_name, zone)`,
enforced by a unique index — ingestion scripts purge a deck's rows before
reinserting, so re-running a fetch never duplicates.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK (autoincrement) | |
| `deck_id` | INTEGER FK→tournament_decks.id | |
| `card_name` | TEXT | Card name |
| `amount` | INTEGER | Copies (1–3) |
| `zone` | TEXT | Deck zone: 'main', 'extra', 'side' |

---

## Group 3 — Banlist & Archetypes

### `banlist_history` — 24,696 rows
Full TCG **and OCG** banlist history scraped from Yugipedia by
`scripts/fetch_banlist_history.py`. Rebuilt wholesale on every run.

| Column | Type | Description |
|--------|------|-------------|
| `list_name` | TEXT | Banlist identifier (Yugipedia page title) |
| `format` | TEXT | `TCG` (81 lists) / `OCG` (87 lists) |
| `effective_date` | TEXT | Date banlist became active |
| `end_date` | TEXT | Date it was superseded (NULL if in force) |
| `card_name` | TEXT | Card name |
| `status` | TEXT | Forbidden / Limited / Semi-Limited |

⚠ Filter on `format`, never on `list_name LIKE '%TCG%'` — Yugipedia names
pre-2021 TCG lists without a suffix ("September 2020 Lists"), so the LIKE
filter silently drops 33 lists.

### `ban_radar` — 966 rows
Ban-risk score per card, built by `scripts/build_ban_radar.py`. TCG only —
the API serves this table as-is and has no format dimension.

| Column | Type | Description |
|--------|------|-------------|
| `card_name` | TEXT | Card name |
| `ban_risk_score` | REAL | 0–100, rescaled on the dataset max |
| `risk_label` | TEXT | Critique / Élevé / Modéré / Faible |
| `current_status` | TEXT | Banlist status in force (Unlimited if none) |
| `ubiquity`, `carrier`, `copies`, `restriction`, `momentum`, `bridge` | REAL | Raw 0–1 criteria; the API reapplies the weights to return each one's contribution |
| `decks`, `deck_share`, `n_archetypes`, `mean_copies` | — | Supporting stats |
| `top_archetype` | TEXT | NULL when the card is a generic staple (archetype concentration < 50%) — drives the front-end filter |
| `archetype_concentration` | REAL | Share of the card's decks belonging to `top_archetype` |
| `format`, `as_of`, `n_decks_window` | — | Build provenance |

### `banlist_features` — 7,385 rows
Per-archetype per-month banlist feature engineering for ML.

| Column | Type | Description |
|--------|------|-------------|
| `month` | TEXT | YYYY-MM-01 |
| `archetype` | TEXT | Archetype name |
| `n_forbidden` | INTEGER | # of archetype cards forbidden |
| `n_limited` | INTEGER | # of archetype cards limited |
| `n_semi` | INTEGER | # of archetype cards semi-limited |
| `ban_severity` | INTEGER | Weighted severity score |
| `ban_severity_t1` | REAL | Severity at t−1 (lagged feature) |
| `was_hit_recent` | INTEGER | 1 if the archetype was hit recently |

Produite par `scripts/build_banlist_features.py` (chaîne `refresh_all.py`).

### `archetypes_official` — 640 rows
Official archetype list from YGOPRODeck `/archetypes.php`.

| Column | Type | Description |
|--------|------|-------------|
| `archetype_name` | TEXT PK | Official archetype name |

### `archetype_mapping` — 122 rows
Maps tournament archetype labels to official names.

| Column | Type | Description |
|--------|------|-------------|
| `tournament_archetype` | TEXT | Label used by yugiohmeta.com |
| `primary_official` | TEXT | Primary official archetype |
| `secondary_official` | TEXT | Secondary (for hybrid decks) |
| `is_hybrid` | INTEGER | 1 if spans multiple archetypes |

---

## Group 4 — Co-occurrence

All co-occurrence tables share the same base schema (with variations). Notebook 02 (chain `refresh_all.py`).

### Base Schema
| Column | Type | Description |
|--------|------|-------------|
| `card_a` | TEXT | First card name (alphabetically lower) |
| `card_b` | TEXT | Second card name |
| `jaccard` | REAL | Weighted Jaccard similarity score |
| `cooc_count` | INTEGER | Raw co-occurrence count |

### Tables

| Table | Filter | Rows | Notes |
|-------|--------|------|-------|
| `card_cooccurrence` | Legal decks (`deck_legality.legal = 1`), TCG+OCG, main deck, Jaccard ≥ 0.1 | 10,741 | Global, all time ; served (graph, `/simulate-ban`) ; no date column |
| `card_cooccurrence_90d` | Rolling 90-day window | 8,817 | Current meta signal |
| `card_cooccurrence_side` | Side deck only | 1,031 | Tech choices |
| `card_cooccurrence_extra` | Extra deck only | 7,166 | Win conditions |
| `card_cooccurrence_elite` | YCS/Nationals/WCQ/Premiere/World | 9,890 | High-level signal |
| `card_cooccurrence_quarterly` | `quarter` TEXT + cards + jaccard | 35,267 | Temporal evolution |

### `archetype_extra_profile` — 6,133 rows
Extra deck card profile per archetype.

| Column | Type | Description |
|--------|------|-------------|
| `archetype` | TEXT | Archetype name |
| `card_name` | TEXT | Extra deck card name |
| `freq` | REAL | Average copies per deck |
| `n_decks` | INTEGER | Number of decks containing it |
| `n_archetypes` | INTEGER | How many archetypes run this card |
| `is_generic` | INTEGER | 1 if n_archetypes ≥ 10 (staple extra) |

---

## Group 5 — Graph & Clustering

### `card_graph_metrics` — 663 rows
NetworkX graph centrality metrics.

| Column | Type | Description |
|--------|------|-------------|
| `card_name` | TEXT PK | |
| `betweenness` | REAL | Betweenness centrality (approximated, k=500) |
| `degree_centrality` | REAL | Degree centrality (0–1) |
| `closeness` | REAL | Closeness centrality |
| `degree_weighted` | REAL | Sum of edge weights |

### `graph_communities` — 63 rows
Louvain community detection results.

| Column | Type | Description |
|--------|------|-------------|
| `community_id` | INTEGER PK | |
| `n_cards` | INTEGER | Cards in this community |
| `lead_card` | TEXT | Card with highest weighted degree |
| `archetype_label` | TEXT | Auto-named from lead card |
| `top_archetypes` | TEXT | JSON list of top archetypes in community |
| `lead_degree` | REAL | Lead card's weighted degree |

### `deck_style_clusters` — 3,601 rows
K-Means clustering of decks by play style (k=4, silhouette=0.171).

| Column | Type | Description |
|--------|------|-------------|
| `deck_id` | INTEGER FK→tournament_decks.id | |
| `cluster` | INTEGER | Cluster ID (0–3) |
| `style` | TEXT | 'Combo', 'Control', 'OTK', or 'Midrange' |
| `confidence` | REAL | Distance to centroid (lower = more confident) |
| `archetype` | TEXT | Archetype of the deck |

---

## Group 6 — Meta Scoring & Prediction

### `meta_scores` — 1,316 rows
Monthly meta share and performance per archetype.

| Column | Type | Description |
|--------|------|-------------|
| `month` | TEXT | YYYY-MM-01 |
| `archetype` | TEXT | |
| `deck_count` | INTEGER | Decks this archetype this month |
| `total_decks` | INTEGER | Total decks this month |
| `share` | REAL | Market share (0–1) |
| `avg_placement` | REAL | Average final placement |
| `meta_score` | REAL | `sqrt(share × placement_score_norm)`, `placement_score_norm = 1 / log(1 + avg_placement)` (intermediate, not stored) |

TCG only since TOK-80, legal decks only (`deck_legality.legal = 1`). Notebook 04. The API computes the tier list on
the fly from this table (`backend/app/tiering.py`).

### `meta_scores_ocg` — 1,530 rows
Same schema as `meta_scores`, OCG decks (notebook 04). Served since TOK-116 (`ocg_history` of
`GET /archetypes/{slug}`); no date column, its computation date is `ocg_archetype_scores.computed_at`.

### `meta_scores_regional` — 2,838 rows
Regional split (OCG vs TCG) of meta scores.

| Column | Type | Description |
|--------|------|-------------|
| `region` | TEXT | 'OCG' or 'TCG' |
| `month` | TEXT | YYYY-MM-01 |
| `archetype` | TEXT | |
| `n_decks` | INTEGER | |
| `share` | REAL | |
| `avg_placement` | REAL | |
| `meta_score` | REAL | |

### `archetype_trend` — 90 rows
Trend indicators per archetype (recent vs past).

| Column | Type | Description |
|--------|------|-------------|
| `archetype` | TEXT PK | |
| `share_recent` | REAL | Share in last 3 months |
| `meta_score_recent` | REAL | Score in last 3 months |
| `meta_score_past` | REAL | Score in previous 3 months |
| `trend_ratio` | REAL | recent / past ratio |
| `trend_label` | TEXT | 'Rising', 'Stable', 'Falling' |

### `meta_tier_list` — 47 rows
Scraped from yugiohmeta.com `/api/v1/tier-list`.

| Column | Type | Description |
|--------|------|-------------|
| `archetype` | TEXT | |
| `format` | TEXT | 'TCG' or 'OCG' |
| `tier` | TEXT | 'T1', 'T2', 'T3', 'field' |
| `deck_count` | INTEGER | |
| `share_pct` | REAL | |
| `scraped_at` | TEXT | Timestamp |

### `meta_predictions` — 44 rows
Next-month predictions from the ensemble model.

| Column | Type | Description |
|--------|------|-------------|
| `archetype` | TEXT | |
| `data_month` | TEXT | Last month with data |
| `meta_score_current` | REAL | Current score |
| `pred_delta` | REAL | Predicted change |
| `pred_meta_score` | REAL | Predicted next score |
| `pred_direction` | TEXT | 'Rising', 'Stable', 'Declining' |
| `computed_at` | TEXT | Computation date (notebook 05) |

Model: 70 % naive + 30 % Ridge (notebook 05). Several `data_month` values coexist; the API serves the latest.

### `ban_impact` — 28 rows
Impact analysis of ban events on archetypes.

| Column | Type | Description |
|--------|------|-------------|
| `card` | TEXT | Banned/limited card name |
| `ban_status` | TEXT | Final status |
| `ban_month_inferred` | TEXT | Month restriction was applied |
| `peak_usage` | REAL | Max share before ban |
| `drop_ratio` | REAL | Share before / after ratio |
| `top_archetype` | TEXT | Most affected archetype |
| `delta_meta_score` | REAL | Change in meta score post-ban |
| `n_archetypes_affected` | INTEGER | |
| `total_appearances` | INTEGER | |

### `card_impact` — 966 rows
Bridge score for every card of the Ban Radar universe (`scripts/build_card_impact.py`, derived from `ban_radar`,
same window). Replaced the 35-card version of `setup_impact_tables.py`. TOK-132: the score measures a card's spread,
not the effect of a ban.

| Column | Type | Description |
|--------|------|-------------|
| `card_name` | TEXT | |
| `decks` | INTEGER | Decks of the window playing the card |
| `n_archetypes` | INTEGER | Archetypes playing it |
| `top_archetype` | TEXT | NULL for generic staples |
| `archetype_concentration` | REAL | Share of the card's decks in `top_archetype` |
| `as_of`, `n_decks_window` | — | Window provenance (same as `ban_radar`) |
| `bridge_score` | REAL | `n_archetypes × log(1 + decks)` |

---

## Group 7 — NLP & Signals

### `text_synergies` — 55,072 rows
Semantic synergy scores between card pairs from effect text.

| Column | Type | Description |
|--------|------|-------------|
| `card_a` | TEXT | |
| `card_b` | TEXT | |
| `ref_score` | REAL | Explicit reference score (0–1) |
| `kw_jaccard` | REAL | Mechanical keyword Jaccard (0–1) |
| `tfidf_sim` | REAL | TF-IDF cosine similarity (0–1) |
| `text_synergy_score` | REAL | `0.5×ref + 0.25×kw + 0.25×tfidf` |
| `shared_keywords` | TEXT | Shared mechanical keywords |
| `arch_a`, `arch_b` | TEXT | Archetypes of the two cards |

Notebook 07, outside `refresh_all.py`: does not cover recent cards (lot 20).

### `card_mechanic_tags` — 13,797 rows
Mechanical tags extracted from effect text per card.

| Column | Type | Description |
|--------|------|-------------|
| `card_name` | TEXT | |
| `archetype` | TEXT | |
| `tags` | TEXT | Comma-separated mechanical tags (Banish, Negate, Tuner, Search, GY...) |
| `n_tags` | INTEGER | Number of tags |

### `combo_mentions` — 598 rows
Card mentions in YouTube combo guide transcripts.

| Column | Type | Description |
|--------|------|-------------|
| `card` | TEXT | Card name detected |
| `start` | REAL | Timestamp in video (seconds) |
| `text` | TEXT | Surrounding transcript text |
| `video_id` | TEXT | YouTube video ID |

### `combo_edges` / `combo_edges_global` — 155 / 117 rows
Directed combo graph edges (A plays before B).

| Column | Type | Description |
|--------|------|-------------|
| `video_id` | TEXT | (combo_edges only) |
| `archetype` | TEXT | (both tables) |
| `card_from` | TEXT | First card in sequence |
| `card_to` | TEXT | Next card in sequence |
| `weight` | INTEGER | Co-mention count |
| `computed_at` | TEXT | (both tables) |

### `early_card_signals` — 263 rows
Composite early signal for new cards.

| Column | Type | Description |
|--------|------|-------------|
| `card_name` | TEXT | |
| `archetype` | TEXT | |
| `tcg_date` | TEXT | TCG release date |
| `ocg_date` | TEXT | OCG release date |
| `views_week` | INTEGER | Weekly views |
| `signal_views` | REAL | Normalized views signal (0–1) |
| `signal_text` | REAL | Text synergy signal (0–1) |
| `signal_ocg` | REAL | OCG meta signal (0–1) |
| `early_score` | REAL | `0.35×views + 0.35×text + 0.30×ocg` |
| `early_score_100` | REAL | Rescaled 0–100 |
| `max_meta_synergy`, `n_meta_connections`, `best_meta_match` | — | Text proximity to the cards of the meta |
| `as_of` | TEXT | Reference date = last TCG deck (lot 20, A1) |
| `computed_at` | TEXT | |

Produced by `scripts/build_early_signals.py` since lot 20 (replaces notebook 11): banlist in force at `as_of`, cards
already in the meta excluded. `views_week` is frozen at the 2026-06-13 snapshot; `text_synergies` does not cover
recent cards, so `signal_text` is 0 for all served cards (TOK-129).

---

## Group 8 — Boutique Intelligence

### `boutique_alerts` — 3 rows
Archetype-level buy alert for card shops.

| Column | Type | Description |
|--------|------|-------------|
| `archetype` | TEXT PK | |
| `alert_score` | REAL | TCG-adjusted score (0–100) |
| `meta_score_ocg` | REAL | OCG meta score |
| `share_ocg` | REAL | OCG market share |
| `avg_views_week` | REAL | Average weekly views of core cards |
| `n_key_cards` | INTEGER | Number of core cards (freq ≥ 0.3) |
| `n_ocg_decks` | INTEGER | OCG decks of the archetype |
| `n_unreleased` | INTEGER | Key cards not yet released in TCG |
| `ocg_first_seen` | TEXT | First OCG deck of the archetype |
| `tcg_window_start`, `tcg_window_end` | TEXT | TCG arrival window (80 % interval, real coverage 62–67 % in 2024-2025, lot 20) |
| `computed_at` | TEXT | |

Notebook 10. Only archetypes not yet in TCG (TOK-113 v3), hence few rows.

### `boutique_card_alerts` — 42 rows
Card-level buy recommendations.

| Column | Type | Description |
|--------|------|-------------|
| `archetype` | TEXT | |
| `card_name` | TEXT | |
| `frequency` | REAL | Average copies per OCG deck |
| `views_week` | INTEGER | Weekly views |
| `card_alert_score` | REAL | Individual card signal |
| `unreleased` | INTEGER | 1 if the card is not yet released in TCG |

### `boutique_buy_signals` — 12 rows
Combined buy signal with price opportunity scoring.

| Column | Type | Description |
|--------|------|-------------|
| `archetype` | TEXT | |
| `card_name` | TEXT | |
| `archetype_alert` | REAL | Archetype-level alert score |
| `card_alert_score` | REAL | Card-level signal |
| `cm_price` | REAL | Current Cardmarket price (€) |
| `tcp_price` | REAL | Current TCGPlayer price ($) |
| `alert_norm` | REAL | Normalized alert (0–100) |
| `price_opp` | REAL | Price opportunity score |
| `buy_score` | REAL | `0.7×alert_norm + 0.3×price_opp` |
| `buy_score_100` | REAL | Normalized buy score (0–100) |
| `buy_label` | TEXT | Relative label (no longer served: the API computes `signal_label` from `ocg_archetype_scores`) |
| `tcg_window_start`, `tcg_window_end` | TEXT | Copied from `boutique_alerts` |
| `computed_at` | TEXT | |
| `ban_tcg` | TEXT | Status in the TCG banlist in force (`banlist_history`, not `cards.ban_tcg`) |

Produced by `scripts/build_buy_signals.py` (cards banned in TCG excluded). One row per (archetype, card).

---

## Group 9 — Tables added since 2026-11 (lots of the 16-18/11)

Effectifs du 2026-11-18. Les tables marquées « servie » sont dans `SERVED_TABLES`.

### `deck_legality` — 23,948 rows
Legality of each deck against the banlist in force on the tournament date (`scripts/compute_deck_legality.py`,
step `legality` of `refresh_decks.py`). Every consumer filters on `legal = 1`.

| Column | Type | Description |
|--------|------|-------------|
| `deck_id` | TEXT | `tournament_decks.id` |
| `format` | TEXT | TCG \| OCG |
| `list_name` | TEXT | Banlist in force on the tournament date |
| `legal` | INTEGER | 1 legal, 0 illegal, NULL not evaluable (Genesys format: 915 decks) |
| `n_violations` | INTEGER | Cards in violation (NULL if not evaluable) |
| `days_to_boundary` | INTEGER | Days to the nearest banlist change |
| `method`, `computed_at` | TEXT | Provenance |

### `banlist_announcements` — 170 rows
Announcement dates of the banlists (`scripts/fetch_banlist_announcements.py`, TOK-121, last step of
`refresh_all.py`). Not served. `banlist_history` is unchanged. Every measurement cuts at `content_date` (cards public),
never at `announced_date` (Konami OCG publishes the list date ~10 days before its content).

| Column | Type | Description |
|--------|------|-------------|
| `format`, `list_name`, `effective_date` | TEXT | Key, same as `banlist_history` |
| `announced_date`, `announced_precision`, `announced_kind` | TEXT | First announcement and what it contained |
| `full_list_date`, `first_source_date` | TEXT | |
| `content_date`, `content_basis` | TEXT | Date the cards were public, and its basis |
| `source`, `source_url`, `cited_source`, `cited_url`, `evidence` | TEXT | Sources (Yugipedia + cited source) |
| `missing_reason` | TEXT | Why a date is empty (never guessed) |
| `fetched_at` | TEXT | |

### `ocg_archetype_scores` — 89 rows (servie)
OCG strength of each archetype (notebook 10). Basis of the absolute shop label (`backend/app/signal_label.py`: rank
among the archetypes, Fort ≤ 10 %, Modéré ≤ 25 %, provisional thresholds).

| Column | Type | Description |
|--------|------|-------------|
| `archetype` | TEXT | |
| `meta_score_ocg`, `share_ocg` | REAL | OCG meta score and share |
| `n_ocg_decks` | INTEGER | |
| `avg_views_week` | REAL | |
| `ocg_score` | REAL | Ranking score |
| `computed_at` | TEXT | |

### `boutique_price_history` — 113 rows (servie)
Cardmarket price history of the cards of the shop signal (`scripts/build_boutique_price_history.py`, TOK-103), from
`card_price_history`.

| Column | Type | Description |
|--------|------|-------------|
| `card_name` | TEXT | |
| `snapshot_date` | TEXT | Snapshot date (YYYY-MM-DD) |
| `cardmarket_price`, `tcgplayer_price` | REAL | |
| `computed_at` | TEXT | |

### `archetype_card_profile` — 4,309 rows (servie)
Per archetype and zone, share of the lists that play each card (`scripts/build_archetype_profiles.py`, TOK-114). Same
window and population as the tier list. Thresholds live in `backend/app/deck_profile.py`, not here.

| Column | Type | Description |
|--------|------|-------------|
| `archetype`, `zone`, `card_name` | TEXT | zone: main \| extra \| side |
| `n_lists` | INTEGER | Lists of the archetype containing the card in this zone |
| `n_decks` | INTEGER | Lists of the archetype in the window |
| `share` | REAL | `n_lists / n_decks` (0–1) |
| `median_copies` | REAL | Among the lists that play it |
| `window_start`, `window_end`, `n_decks_window` | — | Window (months) and its deck count |
| `computed_at` | TEXT | |

### `archetype_recent_decks` — 167 rows / `archetype_recent_deck_cards` — 7,303 rows (servies)
Five most recent lists per archetype and their cards (same script).

| Column | Type | Description |
|--------|------|-------------|
| `deck_id` | TEXT | `tournament_decks.id` |
| `archetype`, `position` | — | (decks) Archetype, rank of recency |
| `author`, `tournament_type`, `placement`, `created` | — | (decks) |
| `zone`, `card_name`, `amount` | — | (cards) |

### `ban_backtest_lists` — 164 rows / `ban_backtest_cards` — 667 rows (servies)
The Ban Radar replayed list by list, the day before each banlist came into force (`scripts/build_ban_history.py`,
TOK-55, through `build_ban_radar.backtest_lists`; not in `refresh_all.py`). Lists below 600 decks or 5 hit cards are kept
with `retained = 0` and `skip_reason`.

| Column | Type | Description |
|--------|------|-------------|
| `format`, `effective_date`, `as_of` | TEXT | List and cutoff date |
| `n_decks`, `n_hits`, `n_cards`, `n_hits_ranked`, `n_hits_missing` | INTEGER | Sizes |
| `retained`, `skip_reason`, `sample` | — | Kept or not, why, position vs. the weight calibration (2026-08-14) |
| `median_rank`, `random_rank`, `random_low`, `random_high` | INTEGER | Median rank of the hit cards and the random band (90 %) |
| `top_n`, `top_n_hits`, `top10pct_hits`, `top25pct_hits` | INTEGER | |
| `baseline_median_rank`, `baseline_top_n_hits` | INTEGER | « most played staples » baseline |
| `min_decks`, `min_hits`, `computed_at` | — | Thresholds and date |
| (cards) `card_name`, `rank`, `ban_risk_score`, `baseline_rank`, `hit`, `in_top`, `generic`, `top_archetype`, `status_before`, `status_after` | — | One row per hit card or top-25 card |

### `prediction_log` — 4,689 rows
Append-only log of the predictions (`scripts/log_predictions.py`); dated proof in `data/prediction_log.jsonl`,
committed by Thomas only.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `kind`, `subject` | TEXT | Prediction type and subject (archetype, card) |
| `made_at`, `logged_at`, `provenance` | TEXT | Dates and `live` \| `backfill` |
| `target_date` | TEXT | |
| `predicted_value`, `baseline_value`, `predicted_label` | — | |
| `model_version`, `payload` | TEXT | |

### `prediction_validation` — 1,392 rows
Predictions of `prediction_log` confronted with what happened (`scripts/validate_predictions.py`): `status`, deltas,
direction, ranks, shares and price changes, `validated_on`. 24 columns, see the script.

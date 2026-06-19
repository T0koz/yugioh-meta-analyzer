# Data Models — Yu-Gi-Oh! Meta Analyzer

Single SQLite database: `data/yugioh.db` (~150 MB). All tables documented below.

---

## Group 1 — Raw Card Data

### `cards` — 13,797 rows
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

### `card_sets` — 43,145 rows
Which booster set each card was printed in.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK (autoincrement) | |
| `card_id` | INTEGER FK→cards.id | |
| `set_name` | TEXT | Full set name |
| `set_code` | TEXT | Set code (e.g. "LEDE-EN001") |
| `set_rarity` | TEXT | Print rarity (Common, Rare, SR, UR...) |
| `set_price` | REAL | Price for this specific printing |

### `card_prices` — 13,797 rows
Static price snapshot from DB initialization (baseline 2026-06-13).

| Column | Type | Description |
|--------|------|-------------|
| `card_id` | INTEGER PK FK→cards.id | |
| `cardmarket_price` | REAL | Cardmarket price (€) |
| `tcgplayer_price` | REAL | TCGPlayer price ($) |
| `ebay_price` | REAL | eBay price |
| `amazon_price` | REAL | Amazon price |
| `coolstuffinc_price` | REAL | CoolStuffInc price |

### `card_price_history` — 27,620+ rows (grows daily)
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

### `tournament_decks` — 19,888 rows
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

### `deck_cards` — 852,405 rows
Individual card entries per deck.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK (autoincrement) | |
| `deck_id` | INTEGER FK→tournament_decks.id | |
| `card_name` | TEXT | Card name |
| `amount` | INTEGER | Copies (1–3) |
| `zone` | TEXT | Deck zone: 'main', 'extra', 'side' |

---

## Group 3 — Banlist & Archetypes

### `banlist_history` — 11,890 rows
Full TCG banlist history scraped from Yugipedia.

| Column | Type | Description |
|--------|------|-------------|
| `list_name` | TEXT | Banlist identifier |
| `effective_date` | TEXT | Date banlist became active |
| `end_date` | TEXT | Date it was superseded |
| `card_name` | TEXT | Card name |
| `status` | TEXT | Forbidden / Limited / Semi-Limited |

### `banlist_features` — 3,660 rows
Per-archetype per-month banlist feature engineering for ML.

| Column | Type | Description |
|--------|------|-------------|
| `month` | TEXT | YYYY-MM-01 |
| `archetype` | TEXT | Archetype name |
| `n_forbidden` | INTEGER | # of archetype cards forbidden |
| `n_limited` | INTEGER | # of archetype cards limited |
| `n_semi` | INTEGER | # of archetype cards semi-limited |
| `ban_severity` | REAL | Weighted severity score |
| `months_on_banlist` | INTEGER | Cumulative months on any restriction |
| `bl_n_limited` | INTEGER | (alias for n_limited, used in features) |

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

All co-occurrence tables share the same base schema (with variations):

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
| `card_cooccurrence` | All TCG+OCG decks | 5,489 | Global, all time |
| `card_cooccurrence_90d` | Rolling 90-day window | 8,797 | Current meta signal |
| `card_cooccurrence_side` | Side deck only | 739 | Tech choices |
| `card_cooccurrence_extra` | Extra deck only | 5,583 | Win conditions |
| `card_cooccurrence_elite` | YCS/Nationals/WCQ/Premiere/World | 4,796 | High-level signal |
| `card_cooccurrence_quarterly` | `quarter` TEXT + cards + jaccard | 9,851 | Temporal evolution |

### `archetype_extra_profile` — 2,961 rows
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

### `meta_scores` — 462 rows
Monthly meta share and performance per archetype.

| Column | Type | Description |
|--------|------|-------------|
| `month` | TEXT | YYYY-MM-01 |
| `archetype` | TEXT | |
| `deck_count` | INTEGER | Decks this archetype this month |
| `total_decks` | INTEGER | Total decks this month |
| `share` | REAL | Market share (0–1) |
| `avg_placement` | REAL | Average final placement |
| `meta_score` | REAL | `sqrt(share × placement_score_norm)` |
| `placement_score_norm` | REAL | `1 / log(1 + avg_placement)` |

### `meta_scores_regional` — 678 rows
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

### `archetype_trend` — 86 rows
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

### `meta_predictions` — 45 rows
Next-month predictions from the ensemble model.

| Column | Type | Description |
|--------|------|-------------|
| `archetype` | TEXT | |
| `data_month` | TEXT | Last month with data |
| `meta_score_current` | REAL | Current score |
| `pred_delta` | REAL | Predicted change |
| `pred_meta_score` | REAL | Predicted next score |
| `pred_direction` | TEXT | 'Rising', 'Stable', 'Falling' |

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

### `card_impact` — 35 rows
Bridge score for new cards entering the meta.

| Column | Type | Description |
|--------|------|-------------|
| `card_name` | TEXT | |
| `release_month` | TEXT | |
| `n_archetypes_3m` | INTEGER | Archetypes using it within 3 months |
| `total_decks_3m` | INTEGER | |
| `bridge_score` | REAL | `n_archetypes × log(total_decks_3m)` |
| `top_archetype` | TEXT | Primary archetype |
| `delta_meta_score_top_arch` | REAL | Impact on top archetype's score |

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
| `archetype` | TEXT | (combo_edges_global only) |
| `card_from` | TEXT | First card in sequence |
| `card_to` | TEXT | Next card in sequence |
| `weight` | INTEGER | Co-mention count |
| `computed_at` | TEXT | (combo_edges_global only) |

### `early_card_signals` — 467 rows
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

---

## Group 8 — Boutique Intelligence

### `boutique_alerts` — 69 rows
Archetype-level buy alert for card shops.

| Column | Type | Description |
|--------|------|-------------|
| `archetype` | TEXT PK | |
| `alert_score` | REAL | TCG-adjusted score (0–100) |
| `alert_score_raw` | REAL | Pre-adjustment score |
| `meta_score_ocg` | REAL | OCG meta score |
| `share_ocg` | REAL | OCG market share |
| `avg_views_week` | REAL | Average weekly views of core cards |
| `n_key_cards` | INTEGER | Number of core cards (freq ≥ 0.3) |
| `tcg_compat_ratio` | REAL | Banlist compatibility (0–1) |
| `tcg_entry_estimated` | TEXT | Estimated TCG meta entry date |
| `computed_at` | TEXT | |

### `boutique_card_alerts` — 167 rows
Card-level buy recommendations.

| Column | Type | Description |
|--------|------|-------------|
| `archetype` | TEXT | |
| `card_name` | TEXT | |
| `frequency` | REAL | Average copies per OCG deck |
| `views_week` | INTEGER | Weekly views |
| `card_alert_score` | REAL | Individual card signal |
| `ban_tcg` | TEXT | TCG ban status (NULL=legal) |

### `boutique_buy_signals` — 137 rows
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
| `buy_label` | TEXT | 'Fort', 'Modéré', or 'Faible' |
| `ban_tcg` | TEXT | TCG ban status flag |
| `tcg_entry_estimated` | TEXT | |
| `computed_at` | TEXT | |

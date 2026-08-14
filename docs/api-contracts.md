# API Contracts — Yu-Gi-Oh! Meta Analyzer

## Current APIs (Consumed)

### 1. YGOPRODeck v7
**Base URL:** `https://db.ygoprodeck.com/api/v7/`

| Endpoint | Method | Params | Used by | Output |
|----------|--------|--------|---------|--------|
| `cardinfo.php` | GET | `misc=yes&format=tcg` | `fetch_cards.py`, `snapshot_prices.py` | All 13,797 TCG cards with prices |
| `archetypes.php` | GET | — | `10_archetypes_official.ipynb` | 640 official archetype names |

**Response shape (cardinfo.php):**
```json
{
  "data": [{
    "id": 80181649,
    "name": "Labrynth Cooclock",
    "type": "Effect Monster",
    "archetype": "Labrynth",
    "card_images": [{"image_url": "...", "image_url_small": "..."}],
    "card_prices": [{"cardmarket_price": "0.17", "tcgplayer_price": "0.18"}],
    "misc_info": [{"views": 12345, "viewsweek": 234, "tcg_date": "2023-01-01"}],
    "banlist_info": {"ban_tcg": "Limited"}
  }]
}
```

### 2. yugiohmeta.com (unofficial)
**Base URL:** `https://www.yugiohmeta.com/api/v1/`

| Endpoint | Method | Key params | Used by |
|----------|--------|-----------|---------|
| `top-decks` | GET | `ocg[$ne]=true`, `limit=100`, `skip=N` | `fetch_tournament_decks.py` |
| `top-decks` | GET | `ocg=true`, `limit=100`, `skip=N` | `fetch_ocg_decks.py` |
| `tier-list` | GET | — | `10_boutique_alert_score.ipynb` |

**Headers required:**
```python
{"Referer": "https://www.yugiohmeta.com/", "User-Agent": "Mozilla/5.0"}
```

**Response shape (top-decks):**
```json
{
  "decks": [{
    "_id": "abc123",
    "author": "PlayerName",
    "archetype": "Kewl Tune",
    "tournament_type": "YCS",
    "placement": 1,
    "created": "2026-05-15T00:00:00Z",
    "ocg": false,
    "cards": {
      "main": [{"id": 12345, "name": "Card Name", "amount": 3}],
      "extra": [...],
      "side": [...]
    }
  }]
}
```

---

## API (Phase 5 — FastAPI) — implemented

`TOK-31` ✅. Read-only FastAPI over SQLite, routers in `backend/app/routers/`.

**Base URL (dev):** `http://localhost:8000/api/v1/`
**Base URL (production):** not decided — see TOK-35. The served database is
~9 MB read-only (`build_serving_db.py`), so a dedicated backend host may not be
needed.

The API only ever reads precomputed tables. Adding an endpoint that queries a new
table means adding it to `SERVED_TABLES` in `scripts/build_serving_db.py`, whose
guard fails the build otherwise.

### Core Endpoints

#### `GET /meta/tier-list`
Returns current tier list merged with meta scores.
```json
{
  "data": [
    {"archetype": "Kewl Tune", "tier": "T1", "meta_score": 0.82, "share": 0.28, "trend": "Rising"},
    ...
  ],
  "generated_at": "2026-06-19"
}
```

#### `GET /meta/evolution`
Historical meta score time series.

**Query params:** `archetypes` (comma-separated), `from_month`, `to_month`
```json
{
  "data": {
    "Kewl Tune": [
      {"month": "2026-01", "meta_score": 0.65, "share": 0.18},
      ...
    ]
  }
}
```

#### `GET /meta/predictions`
Next-month predictions.
```json
{
  "data": [
    {"archetype": "Kewl Tune", "current": 0.82, "predicted": 0.85, "direction": "Rising"},
    ...
  ],
  "model": "Ridge + Naïf blend (ρ≈+0.65)"
}
```

#### `GET /boutique/signals`
Shop buy signals with banlist compatibility.

**Query params:** `min_score` (default: 0), `label` ('Fort'|'Modéré'|'Faible')
```json
{
  "data": [
    {
      "archetype": "Kewl Tune",
      "card_name": "Kewl Tune Reco",
      "buy_score": 99.7,
      "buy_label": "Fort",
      "cm_price": 5.01,
      "ban_tcg": null,
      "tcg_entry_estimated": "2026-10"
    }
  ]
}
```

#### `GET /early-signals`
New cards entering the meta (signal score > threshold).
```json
{
  "data": [
    {"card_name": "Fydraulis Harmonia", "archetype": "Kewl Tune", "early_score": 0.92, "views_week": 19844}
  ]
}
```

#### `GET /graph/synergies`
Co-occurrence data for graph visualization.

**Query params:** `archetype` (filter), `min_jaccard` (default: 0.1), `limit` (default: 200)
```json
{
  "nodes": [{"id": "Card A", "archetype": "...", "community": 0}],
  "edges": [{"from": "Card A", "to": "Card B", "jaccard": 0.45}]
}
```

#### `POST /simulate-ban`
Simulate removing a card from the graph.

**Body:** `{"card_name": "Ash Blossom & Joyous Spring"}`
```json
{
  "removed_card": "Ash Blossom & Joyous Spring",
  "affected_archetypes": ["Branded", "Tenpai Dragon"],
  "community_impact": {"community_id": 5, "fragmentation": 0.23},
  "bridge_score": 0.00504
}
```

#### `GET /ban-radar`
Cards most exposed to the next TCG banlist (`TOK-53`).

**Query params:** `limit` (default 50, max 200), `min_score` (0–100),
`status` (Unlimited|Limited|Semi-Limited), `kind` (`generic`|`archetype`)

`kind` splits generic staples (no home deck) from archetype engine pieces; it
filters on `top_archetype IS NULL` in SQL, so the `limit` applies to the filtered
set rather than truncating a global top.

```json
{
  "data": [
    {
      "card_name": "Fydraulis Harmonia",
      "ban_risk_score": 76.3,
      "risk_label": "Critique",
      "current_status": "Unlimited",
      "deck_share": 13.44,
      "decks": 271,
      "n_archetypes": 7,
      "mean_copies": 2.88,
      "top_archetype": "Kewl Tune",
      "image_url": "https://images.ygoprodeck.com/images/cards_small/12345.jpg",
      "criteria": {"ubiquity": 12.1, "carrier": 21.4, "copies": 36.1,
                   "restriction": 0.0, "momentum": 4.2, "bridge": 2.5}
    }
  ],
  "as_of": "2026-08-09",
  "n_decks_window": 2018,
  "weights": {"ubiquity": 0.3, "carrier": 0.25, "copies": 0.2,
              "restriction": 0.1, "momentum": 0.1, "bridge": 0.05}
}
```

`criteria` holds each criterion's contribution **in points of the final score**
(already weighted and rescaled, so they sum to `ban_risk_score`). The weights are
duplicated between the router and `scripts/build_ban_radar.py` — keep them aligned.

#### `GET /cards/search`
Autocomplete for the global search bar.

**Query params:** `q` (min 2 chars), `limit` (default 8, max 25)
```json
{"data": [{"name": "Ash Blossom & Joyous Spring", "archetype": null,
           "image_url": "https://images.ygoprodeck.com/images/cards_small/14558127.jpg"}]}
```

⚠ Registered **before** `/cards/{name}` in `cards.py`, otherwise FastAPI matches
`search` as the `{name}` path param.

#### `GET /cards/{card_name}`
Card details with price history.
```json
{
  "id": 12345,
  "name": "Kewl Tune Mix",
  "image_url": "https://images.ygoprodeck.com/images/cards/12345.jpg",
  "ban_tcg": null,
  "price_history": [
    {"date": "2026-06-13", "cardmarket": 4.50},
    {"date": "2026-06-19", "cardmarket": 4.71}
  ]
}
```

---

## Streamlit Internal "API" (app.py loaders)

Current cached data loaders — these become the FastAPI endpoints in Phase 5:

| Loader function | SQL query | TTL | Maps to endpoint |
|----------------|-----------|-----|-----------------|
| `load_meta_scores()` | `meta_scores` | 300s | `GET /meta/evolution` |
| `load_tier_list()` | `meta_tier_list` | 300s | `GET /meta/tier-list` |
| `load_predictions()` | `meta_predictions` | 300s | `GET /meta/predictions` |
| `load_early_signals()` | `early_card_signals` | 300s | `GET /early-signals` |
| `load_buy_signals()` | `boutique_buy_signals` | 300s | `GET /boutique/signals` |
| `load_combos()` | `combo_edges_global` | 300s | — |
| `load_banlist_history()` | `banlist_history` | 300s | — |
| `load_price_history()` | `card_price_history` | 300s | `GET /cards/{name}` |

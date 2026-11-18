# API Contracts — Yu-Gi-Oh! Meta Analyzer

## Current APIs (Consumed)

### 1. YGOPRODeck v7
**Base URL:** `https://db.ygoprodeck.com/api/v7/`

| Endpoint | Method | Params | Used by | Output |
|----------|--------|--------|---------|--------|
| `cardinfo.php` | GET | `misc=yes&format=tcg` | `fetch_cards.py` (JSON brut), `fetch_new_cards.py` (ajout des cartes absentes de `cards`), `snapshot_prices.py` | ≈ 14 000 cartes TCG avec prix (14 084 dans `cards` au 2026-11-18) |
| `archetypes.php` | GET | — | `10_archetypes_official.ipynb` | 640 official archetype names |
| images `cards/{id}.jpg`, `cards_cropped/{id}.jpg` | GET | — | `download_card_images.py` (incrémental, TOK-92) | 3 tailles WebP dans `data/card-images/` |

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
| `top-decks` | GET | `ocg[$ne]=true`, `limit=100`, `skip=N` | `fetch_tournament_decks.py` ; santé contrôlée par `check_freshness.py` (TOK-93) |
| `top-decks` | GET | `ocg=true`, `limit=100`, `skip=N` | `fetch_ocg_decks.py` |
| `tier-list` | GET | — | plus appelé par le code actuel (`meta_tier_list`, relevée le 2026-06-17) |

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

`TOK-31` ✅. Lecture seule, FastAPI + `sqlite3`, routeurs dans `backend/app/routers/`, schémas de réponse dans
`backend/app/schemas.py` (font foi en cas de doute ; la liste à jour est aussi dans `/docs` OpenAPI du serveur).

**Base URL (dev):** `http://localhost:8000/api/v1/`
**Base URL (production):** `/api/v1` derrière le front sur Vercel (Services, `vercel.json`, TOK-35), base embarquée
`serving.db` (~12 Mo) ouverte en `mode=ro` — rien de déployé au 2026-11-18 (`docs/deploiement.md`).

L'API ne lit que des tables précalculées. Un endpoint qui lit une table nouvelle exige de l'ajouter à
`SERVED_TABLES` (`scripts/build_serving_db.py`), dont la garde échoue sinon ; et une règle de fraîcheur dans
`scripts/check_freshness.py` (TOK-93). Tout GET est appelé par le test de fumée `backend/tests/test_endpoints.py`
(route à paramètre obligatoire : à ajouter à `EXPLICIT_GETS`).

**Images** : les champs `image_url` renvoient encore l'adresse YGOPRODeck (`…/cards_small/{id}.jpg`) ; le front n'en
garde que l'identifiant et sert l'image depuis son propre hébergement (`frontend/src/lib/card-images.ts`, TOK-92).

**Slugs** : `slug` / `archetype_slug` sont calculés par l'API (`backend/app/slugs.py`) ; le front ne les recalcule
jamais. La résolution d'un slug est insensible à la casse.

### Endpoints (16)

| Méthode | Chemin | Paramètres | Tables lues | Ticket |
|---|---|---|---|---|
| GET | `/meta/tier-list` | — | `meta_scores`, `cards` | TOK-97, lot 20 |
| GET | `/meta/evolution` | — | `meta_scores`, `cards` | TOK-99, lot 15 |
| GET | `/meta/predictions` | — | `meta_predictions`, `meta_prediction_intervals` (si présente), `cards` | lot 20, TOK-131 |
| GET | `/archetypes/{slug}` | `slug` | `meta_scores`, `meta_scores_ocg`, `ocg_archetype_scores`, `ban_radar`, `boutique_buy_signals`, `cards` | TOK-101, TOK-116 |
| GET | `/decks` | — | `archetype_card_profile`, `meta_scores`, `cards` | TOK-114 |
| GET | `/decks/{slug}` | `slug` | `archetype_card_profile`, `archetype_recent_decks`, `archetype_recent_deck_cards`, `meta_scores`, `cards` | TOK-114 |
| GET | `/boutique/signals` | — (100 lignes au plus) | `boutique_buy_signals`, `ocg_archetype_scores`, `cards` | TOK-113 |
| GET | `/boutique/prices` | — | `boutique_price_history` | TOK-103 |
| GET | `/early-signals` | — (50 cartes) | `early_card_signals`, `cards` | lot 20 (A1) |
| GET | `/ban-radar` | `limit` (50, ≤ 200), `min_score` (0-100), `status`, `kind` (`generic`\|`archetype`) | `ban_radar`, `cards` | TOK-53 |
| GET | `/ban-radar/history` | — | `ban_backtest_lists`, `ban_backtest_cards`, `cards` | TOK-55 |
| GET | `/card-impact` | `limit` (50, ≤ 200), `kind` | `card_impact`, `cards` | — |
| GET | `/graph/synergies` | `limit` (150, ≤ 500), `min_jaccard` (0,15, 0-1) | `card_graph_metrics`, `card_cooccurrence`, `cards` | — |
| GET | `/cards/search` | `q` (≥ 1 caractère), `limit` (8, ≤ 25) | `cards` | TOK-49 |
| GET | `/cards/{name}` | `name` | `cards` | — |
| POST | `/simulate-ban` | corps `{"card_name": "…"}` | `cards`, `card_graph_metrics`, `graph_communities`, `card_impact`, `card_cooccurrence` | — |

`archetype_trend` et `meta_tier_list` sont dans `SERVED_TABLES` mais lues par aucun routeur (TOK-93).

### Formes de réponse (champs principaux)

#### `GET /meta/tier-list`
Calculée à la volée sur `meta_scores` (`backend/app/tiering.py`) : fenêtre = mois récents cumulés jusqu'à un effectif
minimal, tendance contre la fenêtre précédente (Benjamini-Hochberg, lot 20).
```json
{
  "data": [{"archetype": "Elfnote", "slug": "elfnote", "tier": "T1", "meta_score": 0.1498,
            "share": 0.207, "decks": 82, "trend": "Rising", "image_url": "…"}],
  "window_start": "2026-10", "window_end": "2026-11", "n_decks": 396,
  "tier_thresholds": [{"tier": "T0", "share": 0.4}, {"tier": "T1", "share": 0.15},
                      {"tier": "T2", "share": 0.07}, {"tier": "T3", "share": 0.03}],
  "tier_min_decks": 5
}
```

#### `GET /meta/evolution`
15 archétypes au plus ; `decks` (k) et `decks_by_month` (n) servent à la bande de Wilson du front.
```json
{"data": {"Kewl Tune": [{"month": "2026-01", "meta_score": 0.08, "share": 0.18, "decks": 27}]},
 "images": {"Kewl Tune": "…"}, "decks_by_month": {"2026-01": 152}}
```

#### `GET /meta/predictions`
```json
{"data": [{"archetype": "Kewl Tune", "current": 0.11, "predicted": 0.12, "direction": "Stable",
           "image_url": "…", "interval_lo": null, "interval_hi": null}],
 "model": "70 % naïf + 30 % Ridge", "data_month": "2026-10", "computed_at": "2026-11-16",
 "direction_threshold": 0.003, "interval_level": null, "interval_method": null}
```
`interval_*` restent nuls tant que `meta_prediction_intervals` n'est pas dans la base servie (TOK-131, formulaire).

#### `GET /archetypes/{slug}`
`archetype`, `slug`, `image_url`, `tcg_window` (`start`, `end`, `n_decks`), `tcg` (tier, tendance, rang, part, decks,
fenêtre précédente ; nul sans deck dans la fenêtre), `history` et `ocg_history` (`month`, `decks`, `total_decks`,
`share`), `ocg_history_computed_at`, `key_cards` (12 cartes de `ban_radar`, `deck_share` en %), `ocg`, `boutique`
(libellé, rang, règle, fenêtre d'arrivée, signaux). 404 si le slug est inconnu.

#### `GET /decks`, `GET /decks/{slug}`
Index : `data[]` (`archetype`, `slug`, `tier`, `decks`, `share`, `has_profile`, `base_cards`, `base_copies`,
`preview[]`), `window`, `rule` (`base_min_share` 0,8, `flex_min_share` 0,2, `min_decks` 8, `backend/app/deck_profile.py`),
`computed_at`. Fiche : mêmes en-têtes + `zones[]` (`zone`, `cards[]` : `card_name`, `n_lists`, `share` 0-1,
`median_copies`, `role` `base`\|`appoint`) et `recent_decks[]` (5 listes : auteur, tournoi, `placement`, `date`,
`zones`). Profil vide sous 8 listes.

#### `GET /boutique/signals`
```json
{"data": [{"archetype": "…", "archetype_slug": "…", "card_name": "…", "buy_score": 100.0,
           "signal_label": "Fort", "archetype_rank": 3, "cm_price": 5.01, "ban_tcg": null, "image_url": "…",
           "tcg_window_start": "2026-11-19", "tcg_window_end": "…"}],
 "label_rule": {"population": 89, "strong_max_rank": 8, "moderate_max_rank": 22, "provisional": true, "note": "…"},
 "computed_at": "2026-11-16"}
```
`buy_score` est un ordre d'affichage (le premier vaut 100), pas une force de signal ; le libellé est le rang de
l'archétype parmi les archétypes OCG (`backend/app/signal_label.py`, seuils provisoires). `buy_label` et
`tcg_entry_estimated` ne sont plus servis.

#### `GET /boutique/prices`
`cards[]` (`card_name`, `points[]` `{date, price}`, `gaps[]` `{start, end, days}`, `sparse`), `period_start`,
`period_end`, `snapshot_count`, `max_step_days` (10), `min_points` (3), `source`, `computed_at`
(`backend/app/price_history.py`).

#### `GET /early-signals`
`data[]` (`card_name`, `archetype` nullable, `early_score`, `views_week`, `image_url`), `computed_at`, `as_of`,
`cards_scored`, `text_signal_cards`.

#### `GET /ban-radar`
`kind` sépare les staples génériques (`top_archetype IS NULL`) des pièces d'archétype, en SQL : `limit` porte sur
l'ensemble filtré.
```json
{
  "data": [{"card_name": "…", "ban_risk_score": 76.3, "risk_label": "Critique", "current_status": "Unlimited",
            "deck_share": 13.44, "decks": 271, "n_archetypes": 7, "mean_copies": 2.88, "top_archetype": "…",
            "image_url": "…",
            "criteria": {"ubiquity": 12.1, "carrier": 21.4, "copies": 36.1, "restriction": 0.0,
                         "momentum": 4.2, "bridge": 2.5}}],
  "as_of": "2026-11-14", "n_decks_window": 1883,
  "weights": {"ubiquity": 0.3, "carrier": 0.25, "copies": 0.2, "restriction": 0.1, "momentum": 0.1, "bridge": 0.05}
}
```
`deck_share` est en **pourcentage** (les autres parts de l'API sont dans [0 ; 1]). `criteria` donne chaque critère en
points du score final (somme = `ban_risk_score`). Les poids sont dupliqués entre le routeur et
`scripts/build_ban_radar.py` : les garder alignés (contrôlé par `check.py`).

#### `GET /ban-radar/history`
`lists[]` (une banlist rejouée la veille de son entrée en vigueur : `format`, `effective_date`, `as_of`, `retained`,
`skip_reason`, `sample` `calage`\|`validation`\|`retrospective`\|`prospective`, effectifs, `median_rank`,
bande du hasard `random_low`/`random_high`, `top_n_hits`, base staples `baseline_*`, `cards[]`), `computed_at`,
`top_n` (25), `min_decks` (600), `min_hits` (5).

#### `GET /card-impact`
`data[]` (`card_name`, `bridge_score`, `n_archetypes`, `decks`, `top_archetype`, `image_url`), `as_of`,
`n_decks_window`. Le score de pont mesure la diffusion d'une carte, pas l'effet d'un ban (TOK-132).

#### `GET /graph/synergies`
```json
{"nodes": [{"id": "Card A", "group": "…", "size": 0.4, "image_url": "…"}],
 "edges": [{"source": "Card A", "target": "Card B", "weight": 0.45}]}
```
Graphe du notebook 03, périmé (663 nœuds contre 1 402, TOK-136).

#### `GET /cards/search`
```json
{"data": [{"name": "Ash Blossom & Joyous Spring", "archetype": null, "image_url": "…"}]}
```
⚠ Déclarée **avant** `/cards/{name}` dans `cards.py`, sinon FastAPI prend `search` pour `{name}`.

#### `GET /cards/{name}`
La ligne de `cards` telle quelle (toutes les colonnes, sans schéma de réponse) ; 404 si le nom est inconnu.

#### `POST /simulate-ban`
```json
{"removed_card": "Ash Blossom & Joyous Spring", "image_url": "…",
 "affected_archetypes": ["Branded", "Tenpai Dragon"],
 "community_impact": {"community_id": 5, "fragmentation": 0.23}, "bridge_score": 0.00504}
```
Approximation : `fragmentation` = betweenness normalisée sur le maximum ; archétypes voisins = archétypes des 30
cartes les plus co-jouées (10 au plus). Aucune prévision validée (TOK-132).

---

## Streamlit Internal "API" (app.py loaders)

Loaders du tableau de bord Streamlit historique (`app.py`, toujours lancé par `run.sh`). La correspondance avec
l'API est indicative : `/meta/tier-list` ne lit plus `meta_tier_list` (calcul à la volée sur `meta_scores`, TOK-97).

| Loader function | SQL query | TTL | Maps to endpoint |
|----------------|-----------|-----|-----------------|
| `load_meta_scores()` | `meta_scores` | 300s | `GET /meta/evolution` |
| `load_tier_list()` | `meta_tier_list` | 300s | — (table figée au 2026-06-17) |
| `load_predictions()` | `meta_predictions` | 300s | `GET /meta/predictions` |
| `load_early_signals()` | `early_card_signals` | 300s | `GET /early-signals` |
| `load_buy_signals()` | `boutique_buy_signals` | 300s | `GET /boutique/signals` |
| `load_combos()` | `combo_edges_global` | 300s | — |
| `load_banlist_history()` | `banlist_history` | 300s | — |
| `load_price_history()` | `card_price_history` | 300s | `GET /cards/{name}` |

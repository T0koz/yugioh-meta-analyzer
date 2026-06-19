# Yugioh Meta Analyzer — Context

## Projet
Outil d'analyse et de prédiction de la méta Yu-Gi-Oh! via IA.
Problème : pas d'outil structuré pour préparer ses decks et anticiper l'impact d'une nouvelle carte ou d'une banlist sur la méta.
Potentiel B2B : vente aux boutiques (150€/mois) pour anticiper les achats de stock avec 4 mois d'avance sur la méta TCG.
Réplicable sur d'autres TCG (Pokémon, Magic...) une fois le modèle Yu-Gi-Oh! validé.

## Profil
Thomas Cozian — ex consultant e-commerce ZeTrace, ex PO refonte B2B headless.
Formation Le Wagon Data Science & IA débutant le 12 octobre 2026.
Objectif : produit V2 fini avant Le Wagon.

---

## Stack
- Python 3.13 (Homebrew), VS Code, Git, GitHub
- Venv : `.venv` à la racine du projet
- Libs : requests, pandas, numpy, jupyter, ipykernel, networkx, pyvis, playwright, matplotlib, scipy, python-dateutil, scikit-learn, streamlit, plotly, youtube-transcript-api, statsmodels
- SQLite pour le stockage local (`data/yugioh.db`, ~150 MB)
- Dashboard : `streamlit run app.py` ou `bash run.sh`
- Cron quotidien : `snapshot_prices.py` à 9h (via Claude Scheduled Tasks)

---

## Vision produit
La méta Yu-Gi-Oh! moderne est structurée autour des combos : un deck est fort parce qu'il enchaîne 5-6+ cartes en un tour pour construire un board imbattable.
Le produit permet de :
1. Identifier les combos dominants dans les decks gagnants
2. Mesurer la complexité et la robustesse de chaque combo
3. Détecter automatiquement quand une nouvelle carte s'insère comme raccourci dans un combo existant — le signal méta le plus puissant
4. Visualiser tout ça dans un dashboard (Streamlit → React)
5. **Signal boutiques** : OCG → TCG avec 4 mois d'avance (r=0.771, p<0.0001)

---

## Roadmap
- Phase 1 : API YGOPRODeck + base SQLite + exploration Pandas ✅
- Phase 2 : Decklists tournoi + co-occurrence + graphe synergies + OCG ✅
- Phase 3 : Score méta + modèle prédictif (sklearn) + détection impact banlist ✅
- Phase 4 : Dashboard Streamlit + NLP transcripts YouTube ✅
- Signal boutiques : OCG + views_week → score d'alerte ✅
- Données supplémentaires : banlist historique, archetypes officiels, images, prix historique ✅
- Phase 5 : Front-end web (React + FastAPI) — en cours

---

## Phase 1 ✅ — Données cartes (YGOPRODeck)

**Scripts**
- `scripts/fetch_cards.py` : appel bulk à l'API YGOPRODeck v7 (`misc=yes&format=tcg`) → `data/raw/cards.json` (13 797 cartes TCG)
- `scripts/init_db.py` : chargement dans SQLite → tables `cards`, `card_sets`, `card_prices` + colonnes `image_url` / `image_url_small`

**Tables créées**
- `cards` : 13 797 cartes (id, name, type, frame_type, desc, archetype, atk, def, level, race, attribute, link_val, scale, ban_tcg, ban_ocg, ban_goat, tcg_date, ocg_date, has_effect, views, views_week, md_rarity, image_url, image_url_small)
- `card_sets` : 43 145 entrées
- `card_prices` : prix statiques (snapshot de départ)

**TOK-10 ✅** — `image_url` + `image_url_small` ajoutés à `cards` (URLs YGOPRODeck : `https://images.ygoprodeck.com/images/cards/{id}.jpg`)

**TOK-7 ✅** — `archetypes_official` (640 archetypes) + `archetype_mapping` (122 mappings tournament → official)

**TOK-8 ✅** — `banlist_history` (11 890 entrées, scraping Yugipedia)

**TOK-9 ✅** — `card_price_history` : backfill baseline 2026-06-13 (13 753 cartes) + cron quotidien bulk (1 appel API, ~12s) couvrant toutes les cartes TCG

---

## Phase 2 ✅ — Decklists tournoi + co-occurrence + graphe

**Collecte**
- `scripts/fetch_tournament_decks.py` : 9 330 decklists TCG depuis 2024-01-01
- `scripts/fetch_ocg_decks.py` : 10 558 decklists OCG (`ocg=1`) — même table `tournament_decks`
- Total : **19 888 decklists**, **852 405 entrées deck_cards**

**Co-occurrence (02_cooccurrence.ipynb)**

| Table | Description | Lignes |
|-------|-------------|--------|
| `card_cooccurrence` | Jaccard pondéré global (placement × temps) | 5 489 |
| `card_cooccurrence_90d` | Fenêtre glissante 90j (TOK-11) | 8 797 |
| `card_cooccurrence_side` | Side deck séparé | 739 |
| `card_cooccurrence_extra` | Extra deck (TOK-14) | 5 583 |
| `card_cooccurrence_elite` | YCS/Nationals/WCQ uniquement (TOK-19) | 4 796 |
| `card_cooccurrence_quarterly` | Par trimestre, Jaccard > 0.2 (TOK-18) | 9 851 |
| `archetype_extra_profile` | Profil extra deck par archetype (TOK-14) | 2 961 |

Formule Jaccard pondéré : `poids = (1/placement) × exp(-jours/365)`, amount normalisé à 1 pour l'extra deck.

**TOK-13 ✅** — Pondération co-occurrence par placement (`1/placement`)
**TOK-14 ✅** — Extra deck analysé séparément, `is_generic` flag (carte dans ≥10 archetypes)
**TOK-15 ✅** — `deck_style_clusters` : K-Means k=4, 19 features (ratios + tags mécaniques + extra_size), silhouette=0.171 → styles : Combo / Control / OTK / Midrange
**TOK-18 ✅** — Co-occurrence par trimestre : 10 quarters (2024-Q1 → 2026-Q2)
**TOK-19 ✅** — Filtre élite : 776 decks élite sur 3 601 total
**TOK-20 ✅** — Segmentation OCG/TCG via flag `ocg` → `meta_scores_regional` (678 lignes). Kewl Tune +13% OCG, Dracotail +12% TCG

**Graphe (03_graph.ipynb)**
- NetworkX : ~660 nœuds, arêtes Jaccard > 0.1, 63 communautés (Louvain)
- Fichiers HTML Pyvis pour visualisation interactive
- Classification : `staple_format`, `tech_pont`, `piece_niche`

**TOK-16 ✅** — `card_graph_metrics` : betweenness centrality approximée (k=500), degree, closeness (663 cartes). Top ponts : Albion the Shrouded Dragon (0.00575), Triple Tactics Thrust (0.00549), Called by the Grave (0.00504)
**TOK-17 ✅** — `graph_communities` : 63 communautés nommées par lead card (max degré pondéré). Ex : Branded (43 cartes), Kewl Tune (19), Labrynth (18)

**Corrélation OCG→TCG (09_ocg_tcg_correlation.ipynb)**
- **Lag optimal : 4 mois**
- **r = 0.771, p < 0.0001, n = 43 paires archetype/mois**

---

## Phase 3 ✅ — Score méta + modèle prédictif

**Score méta (04_meta_score.ipynb)**
- `meta_score = sqrt(share × placement_score_norm)` (moyenne géométrique volume × performance)
- `meta_scores` : 462 lignes (29 mois × ~16 archetypes/mois)
- `archetype_trend` : 86 archetypes avec trend_ratio, trend_label
- `meta_tier_list` : 47 archetypes scrappés depuis yugiohmeta.com (TOK-12)

**Modèle prédictif (05_meta_prediction.ipynb)**

Walk-forward CV (fenêtre 9 mois), Spearman ρ comme métrique principale.

**Features (20 au total)** :
- Lags temporels T-1/T-2/T-3, delta_1m, accel, roll_mean_3m, rank_month (TOK-21)
- Banlist historique : n_forbidden, n_limited, n_semi, ban_severity, months_on_banlist (TOK-22)
- `trend_ratio_monthly` = (n_limited + n_semi) / (n_cards + 1) par mois (TOK-23)
- `months_since_debut` = mois depuis la 1ère apparition en méta (TOK-24)

**Résultats** :
- Méta 2026 "sticky" → naïf "no change" = ρ +0.508
- Ensemble optimal : 70% naïf + 30% Ridge(α=50, δ) → ρ ≈ +0.65
- Prédictions filtrées aux archetypes actifs dans les 4 derniers mois
- `meta_predictions` : 45 lignes (archetype, data_month, meta_score_current, pred_delta, pred_meta_score, pred_direction)

**TOK-25 ✅** — AR(1) par archetype (AutoReg statsmodels). AR(1) seul < naïf (ρ +0.141 vs +0.212) dans méta sticky 2026. Blend 20% AR1 + 10% Ridge + 70% Naïf → ρ = +0.6504 vs +0.6413 → gain marginal, production inchangée.

**Banlist (06_card_ban_impact.ipynb + 09_banlist_history.ipynb)**
- `ban_impact` : 28 cartes analysées (drop_ratio, delta_meta_score)
- `card_impact` : 35 cartes (bridge_score, n_archetypes_3m)
- `banlist_history` : 11 890 entrées (scraping Yugipedia, TOK-8)
- `banlist_features` : 3 660 lignes (archetype × mois × statuts banlist, TOK-22)

---

## Phase 4 ✅ — Dashboard Streamlit + NLP

**Dashboard (app.py) — 9 pages**
1. 📊 Tier List (meta_tier_list + meta_scores)
2. 📈 Évolution (méta historique par archetype)
3. 🔮 Prédictions (meta_predictions)
4. 🚨 Signal précoce (early_card_signals)
5. 🛒 Signal boutique (boutique_alerts + boutique_card_alerts)
6. 🎮 Combos NLP (combo_edges_global)
7. 📜 Banlist historique (banlist_history)
8. 🕸️ Graphe synergies (card_cooccurrence → vis-network)
9. 🚫 Simulateur ban

**NLP texte effets (07_nlp_text_synergies.ipynb) — TOK-6 ✅**
- 3 signaux : références explicites (guillemets), tags mécaniques (Banish/Negate/Tuner…), TF-IDF cosine
- Score composite : `0.5 × ref_score + 0.25 × kw_jaccard + 0.25 × tfidf_sim`
- `text_synergies` : 55 072 paires, `card_mechanic_tags` : 13 797 cartes taguées

**NLP combos YouTube (08_nlp_combos.ipynb) — TOK-26/27/28 ✅**
- `youtube_transcript_api` v1.x, blacklist 64 termes, ASR corrections (Cool Tune → Kewl Tune)
- 3 vidéos agrégées : 528 mentions, 117 arêtes globales
- `combo_mentions` (598), `combo_edges` (155), `combo_edges_global` (117)

**Signal précoce nouvelles cartes (11_early_card_signal.ipynb) — TOK-5 ✅**
- `early_score = 0.35 × signal_views + 0.35 × signal_text + 0.30 × signal_ocg`
- Scope : cartes TCG sorties depuis jan 2026 OU OCG depuis juin 2025
- `early_card_signals` : 467 cartes. Top juin 2026 : Kewl Tune (triple signal), Elfnote #2

---

## Signal boutiques ✅ — TOK-29/30

**Score d'alerte (10_boutique_alert_score.ipynb)**
- `alert_score = meta_score_ocg × log(1 + avg_views_week_cartes_core)`
- Cartes core = présentes dans ≥30% des decks OCG pour l'archetype
- Staples format exclues (>20% tous decks TCG), cartes bannies TCG exclues
- `boutique_alerts` (69 archetypes), `boutique_card_alerts` (167 cartes), `boutique_buy_signals` (137)

**Dashboard boutique (TOK-30 ✅)** — page dédiée B2B dans Streamlit

**Résultats juin 2026** — entrée TCG estimée : octobre 2026
- #1 Kewl Tune 100/100 : Fydraulis Harmonia 19 844 views/week, présent 89% decks

---

## Structure du projet

```
yugioh-meta-analyzer/
├── app.py                              # Dashboard Streamlit (9 pages)
├── run.sh                              # Lance streamlit avec venv
├── context.md                          # Ce fichier
├── README.md                           # Vue d'ensemble projet
├── BACKLOG.md                          # Backlog (tout done sauf Phase 5)
├── scripts/
│   ├── fetch_cards.py                  # YGOPRODeck API → data/raw/cards.json
│   ├── init_db.py                      # cards.json → yugioh.db (cards + images)
│   ├── fetch_tournament_decks.py       # yugiohmeta.com TCG → yugioh.db
│   ├── fetch_ocg_decks.py              # yugiohmeta.com OCG → yugioh.db (ocg=1)
│   ├── snapshot_prices.py              # Cron quotidien 9h — prix bulk toutes cartes
│   ├── explore_limitless.py            # Outil diagnostic Playwright
│   └── setup_impact_tables.py          # Génère ban_impact + card_impact
├── notebooks/
│   ├── 01_exploration.ipynb            # Exploration initiale cartes
│   ├── 02_cooccurrence.ipynb           # Co-occurrence (6 variantes) + extra deck
│   ├── 03_graph.ipynb                  # Graphe synergies + centralité + communautés
│   ├── 04_meta_score.ipynb             # Score méta + tier list
│   ├── 05_meta_prediction.ipynb        # Modèle prédictif (Ridge + AR1 + Naïf)
│   ├── 06_card_ban_impact.ipynb        # Bridge score + impact bans
│   ├── 07_nlp_text_synergies.ipynb     # NLP texte effets
│   ├── 08_nlp_combos.ipynb             # NLP combos YouTube
│   ├── 09_banlist_history.ipynb        # Scraping historique banlist Yugipedia
│   ├── 09_ocg_tcg_correlation.ipynb    # Corrélation OCG→TCG (r=0.771, lag=4 mois)
│   ├── 10_archetypes_official.ipynb    # Archetypes officiels YGOPRODeck
│   ├── 10_boutique_alert_score.ipynb   # Score alerte boutiques
│   ├── 11_early_card_signal.ipynb      # Signal précoce nouvelles cartes
│   └── 12_deck_clustering.ipynb        # Clustering decks (Combo/Control/OTK/Midrange)
└── data/
    ├── raw/cards.json                  # ~31 MB, non tracké Git
    ├── yugioh.db                       # ~150 MB, non tracké Git
    └── SOURCES.md
```

---

## Schema SQLite (data/yugioh.db)

### Données brutes
| Table | Lignes | Clé |
|-------|--------|-----|
| `cards` | 13 797 | id (INTEGER) |
| `card_sets` | 43 145 | autoincrement |
| `card_prices` | 13 797 | card_id |
| `card_price_history` | 27 620+ | (card_id, snapshot_date) |
| `tournament_decks` | 19 888 | id |
| `deck_cards` | 852 405 | id |
| `banlist_history` | 11 890 | — |
| `archetypes_official` | 640 | archetype_name |
| `archetype_mapping` | 122 | tournament_archetype |

### Co-occurrence
| Table | Lignes | Description |
|-------|--------|-------------|
| `card_cooccurrence` | 5 489 | Global pondéré |
| `card_cooccurrence_90d` | 8 797 | Fenêtre 90j |
| `card_cooccurrence_side` | 739 | Side deck |
| `card_cooccurrence_extra` | 5 583 | Extra deck |
| `card_cooccurrence_elite` | 4 796 | YCS/Nationals/WCQ |
| `card_cooccurrence_quarterly` | 9 851 | Par trimestre |
| `archetype_extra_profile` | 2 961 | Profil extra deck |

### Graphe & clustering
| Table | Lignes | Description |
|-------|--------|-------------|
| `card_graph_metrics` | 663 | Betweenness / degree / closeness |
| `graph_communities` | 63 | Communautés nommées |
| `deck_style_clusters` | 3 601 | Style Combo/Control/OTK/Midrange |

### Score méta & prédiction
| Table | Lignes | Description |
|-------|--------|-------------|
| `meta_scores` | 462 | Score mensuel par archetype |
| `meta_scores_regional` | 678 | OCG vs TCG par mois |
| `archetype_trend` | 86 | trend_ratio par archetype |
| `meta_tier_list` | 47 | Tier list scrapée yugiohmeta.com |
| `meta_predictions` | 45 | Prédictions mois suivant |
| `banlist_features` | 3 660 | Features banlist par archetype/mois |
| `ban_impact` | 28 | Impact detections bans |
| `card_impact` | 35 | Bridge score nouvelles cartes |

### NLP & signal
| Table | Lignes | Description |
|-------|--------|-------------|
| `text_synergies` | 55 072 | Score synergies textuelles |
| `card_mechanic_tags` | 13 797 | Tags mécaniques par carte |
| `combo_mentions` | 598 | Mentions cartes dans vidéos |
| `combo_edges` | 155 | Arêtes combos par vidéo |
| `combo_edges_global` | 117 | Arêtes combos agrégées |
| `early_card_signals` | 467 | Signal précoce nouvelles cartes |

### Signal boutiques
| Table | Lignes | Description |
|-------|--------|-------------|
| `boutique_alerts` | 69 | Score alerte par archetype |
| `boutique_card_alerts` | 167 | Score alerte par carte |
| `boutique_buy_signals` | 137 | Signaux d'achat combinés |

---

## APIs

### YGOPRODeck v7
- Base URL : `https://db.ygoprodeck.com/api/v7/cardinfo.php`
- Paramètres utiles : `misc=yes`, `format=tcg`, `archetype=X`
- Autres endpoints : `/archetypes.php`, `/cardsets.php`
- Rate limit : 20 req/s
- Images : `https://images.ygoprodeck.com/images/cards/{id}.jpg`

### yugiohmeta.com (non officielle)
- Base URL : `https://www.yugiohmeta.com/api/v1/top-decks`
- TCG : `ocg[$ne]=true`, OCG : `ocg=true`
- Paramètres : `uploaded[$gte]=YYYY-MM-DD`, `limit=100`, `skip=N`
- Tier list : `/api/v1/tier-list` (scrapé dans TOK-12)

### Cardmarket / TCGPlayer
- Prix via YGOPRODeck (champ `card_prices` dans cardinfo.php)
- Snapshot quotidien bulk → `card_price_history`

---

## Prochaines étapes — Phase 5

| TOK | Description |
|-----|-------------|
| TOK-31 | Définir les endpoints FastAPI |
| TOK-32 | Front React — tier list dynamique |
| TOK-33 | Front React — graphe synergies interactif |
| TOK-34 | Front React — simulateur de ban |
| TOK-35 | Déploiement (Vercel + Railway/Render) |
| TOK-36 | Alertes email/Discord (signal précoce) |
| TOK-37 | Affiliation Cardmarket |

*Dernière mise à jour : 2026-06-19*

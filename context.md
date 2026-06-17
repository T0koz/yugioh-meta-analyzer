# Yugioh Meta Analyzer — Context

## Projet
Outil d'analyse et de prédiction de la méta Yu-Gi-Oh! via IA.
Problème : pas d'outil structuré pour préparer ses decks et anticiper l'impact d'une nouvelle carte sur la méta.
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
- Libs installées : requests, pandas, numpy, jupyter, ipykernel, networkx, pyvis, playwright, matplotlib, scipy, python-dateutil
- SQLite pour le stockage local
- Dashboard : `streamlit run app.py` ou `bash run.sh`

---

## Vision produit
La méta Yu-Gi-Oh! moderne est structurée autour des combos : un deck est fort parce qu'il enchaîne 5-6+ cartes en un tour pour construire un board imbattable.
Le produit doit permettre de :
1. Identifier les combos dominants dans les decks gagnants
2. Mesurer la complexité et la robustesse de chaque combo (nombre de cartes requises, chemins alternatifs)
3. Détecter automatiquement quand une nouvelle carte s'insère comme raccourci dans un combo existant — c'est le signal méta le plus puissant
4. Visualiser tout ça dans une interface claire (Streamlit → React)
5. **Signal boutiques** : OCG → TCG avec 4 mois d'avance (r=0.771, p<0.0001)

---

## Roadmap
- Phase 1 : API YGOPRODeck + base SQLite + exploration Pandas ✅
- Phase 2 : Decklists tournoi + co-occurrence + graphe de synergies ✅ + OCG ✅
- Phase 3 : Score méta + modèle prédictif (sklearn) + détection impact nouvelle carte ✅
- Phase 4 : Interface Streamlit + NLP transcripts YouTube (Whisper) ✅
- Signal boutiques : OCG + views_week → score d'alerte ✅
- Phase 5 : Front-end web (React) — visualisation des combos, score méta, impact banlists

---

## Phase 1 ✅ — Données cartes (YGOPRODeck)

### Ce qui a été fait
- Environnement configuré (Python 3.13 Homebrew, venv, VS Code, Git/GitHub)
- `scripts/fetch_cards.py` : appel unique à l'API YGOPRODeck v7 (`misc=yes&format=tcg`) → `data/raw/cards.json`
  - 13 797 cartes TCG récupérées avec stats complètes, archetype, banlist, prix, dates de sortie, popularité
- `scripts/init_db.py` : chargement dans SQLite → 3 tables : `cards`, `card_sets`, `card_prices`
  - 13 797 cartes, 43 145 entrées de sets, 13 797 entrées de prix
- `notebooks/01_exploration.ipynb` : exploration Pandas
  - Distribution des types et attributs
  - Top 20 archetypes en nombre de cartes
  - Cartes bannies / limitées / semi-limitées (banlist TCG)
  - Stats ATK/DEF par type
  - Cartes les plus chères (cardmarket + tcgplayer)
  - Archetypes les plus représentés dans les boosters

### Ce qu'on n'a pas exploité (à revisiter)
- **Texte des effets (`desc`)** : chaque carte a un texte d'effet complet. NLP pour détecter synergies textuelles → P1-B
- **Endpoint `/archetypes.php`** : liste officielle de tous les archetypes Konami → P1-F
- **Historique de banlist** : l'API ne donne que le statut actuel → P1-C
- **Prix dans le temps** : snapshot instantané, pas d'historique → P1-D
- **Images des cartes** : URLs disponibles, non récupérées → P1-E

---

## Phase 2 ✅ — Decklists tournoi + co-occurrence + graphe + OCG

### Ce qui a été fait

**Collecte des données de tournoi**
- `scripts/fetch_tournament_decks.py` : fetch paginé `ocg[$ne]=true` depuis 2024-01-01
  - 9 330 decklists TCG, 395 006 entrées de cartes
  - Tables SQLite : `tournament_decks`, `deck_cards`
- `scripts/fetch_ocg_decks.py` : fetch paginé `ocg=true` depuis 2024-01-01
  - ~10 558 decklists OCG insérées (même table, `ocg=1`)

**Co-occurrence (notebooks/02_cooccurrence.ipynb)**
- Poids par deck = `(1 / placement) × exp(-jours / 365)` → normalisé
- Jaccard pondéré : 4 444 paires → table `card_cooccurrence`
- Side deck analysé séparément → table `card_cooccurrence_side`

**Graphe de synergies (notebooks/03_graph.ipynb)**
- Graphe NetworkX : 520 nœuds, 2 326 arêtes, 38 composantes, 46 communautés
- `simulate_ban()` fonctionnel
- Fichiers HTML Pyvis : `data/graph_*.html`
- Classification : `staple_format` (8 cartes), `tech_pont` (148), `piece_niche` (1531)

**Corrélation OCG→TCG (notebooks/09_ocg_tcg_correlation.ipynb)** ✅
- **Lag optimal : 4 mois**
- **r = 0.771, p < 0.0001, n = 43 paires archetype/mois**
- Signal validé : OCG est un prédicteur fiable de la méta TCG avec 4 mois d'avance
- Les boutiques peuvent acheter le stock 4 mois avant l'explosion TCG

---

## Phase 3 ✅ — Score méta + modèle prédictif

### Ce qui a été fait

**Score méta (notebooks/04_meta_score.ipynb)**
- `meta_score = sqrt(share × placement_score_norm)`
- Table `meta_scores` : 462 lignes (29 mois × ~16 archetypes/mois)
- Table `archetype_trend` : 86 archetypes avec trend_ratio
- Résultats clés : DoomZ trend_ratio 4.217, Blue-Eyes pic fév 2025 puis disparu

**Modèle prédictif (notebooks/05_meta_prediction.ipynb)**
- 3 modèles (Ridge, RF, GB), R² ≈ -37 à -41 → distribution shift 2024→2026
- Feature importance : avg_placement (42%), share (33%), meta_score (15%)
- À corriger : features lag temporelles (P3-R), banlist historique (P3-V)

**Détection impact (notebooks/06_card_ban_impact.ipynb)**
- `bridge_score`, `delta_meta_score` → tables `ban_impact`, `card_impact`

---

## Phase 4 ✅ — Interface Streamlit + NLP combos

### Dashboard Streamlit (app.py)
- 6 pages : Tier List, Évolution temporelle, Graphe synergies, Simulateur ban, Cartes bridge, Prédictions RF
- Lancement : `streamlit run app.py` ou `bash run.sh`

### NLP Combos (notebooks/08_nlp_combos.ipynb)
- `youtube_transcript_api` v1.x, matching sur 13 791 noms de cartes
- Graphe orienté A→B→C, tables `combo_mentions`, `combo_edges`
- **Blacklist à appliquer** : `{'NEXT', 'Fine', 'Return', 'Question', 'Last Turn', 'Honest', 'Typhoon', 'Recycle'}`
- **Prochaine étape NLP** : vidéos combo guide (ex: "Kewl Tune combo guide 2026")

---

## NLP texte des effets ✅ — TOK-6 (notebooks/07_nlp_text_synergies.ipynb)

- **3 signaux** : références explicites entre cartes (guillemets), tags mécaniques (Banish/Negate/Tuner…), TF-IDF cosine similarity
- **Score composite** : `0.5 × ref_score + 0.25 × kw_jaccard + 0.25 × tfidf_sim`
- Tables DB : `text_synergies` (55 072 paires), `card_mechanic_tags` (13 797 cartes taguées)
- Graphes HTML : `data/graph_text_kewl_tune.html`, `graph_text_branded.html`, `graph_text_tenpai_dragon.html`

## Signal précoce nouvelles cartes ✅ — TOK-5 + TOK-6 + SB-Z (notebooks/11_early_card_signal.ipynb)

- **Formule** : `early_score = 0.35 × signal_views + 0.35 × signal_text + 0.30 × signal_ocg`
- Scope : cartes TCG sorties depuis jan 2026 OU OCG depuis juin 2025 (467 cartes)
- **Bug à éviter** : `ban_tcg IS NULL` = carte légale en SQLite — ne pas utiliser `!= 'Forbidden'` seul
- Table DB : `early_card_signals` (467 lignes, recomputer périodiquement)
- Résultats juin 2026 : Kewl Tune domine (triple signal), Elfnote #2, Nervedo Power Patron détecté via text_synergy seul

---

## Signal boutiques ✅ — SB-Z

**Score d'alerte (notebooks/10_boutique_alert_score.ipynb)**
- **Formule** : `alert_score = meta_score_ocg × log(1 + avg_views_week_cartes_core)`
- Cartes core = présentes dans ≥30% des decks OCG pour l'archetype
- **Filtres appliqués** :
  - Staples format exclues (cartes dans >20% de tous les decks TCG) : ~Ash Blossom, Mulcharmy, etc.
  - Cartes bannies TCG exclues (`ban_tcg = 'Forbidden'`) : Maxx "C" etc.
- Tables DB créées : `boutique_alerts` (par archetype), `boutique_card_alerts` (par carte)

**Résultats actuels (juin 2026)**
- Entrée TCG estimée : **octobre 2026**
- **#1 Kewl Tune — score 100/100** : archetype OCG dominant
  - Fydraulis Harmonia : 19 844 views/week, présent dans 89% des decks → signal d'achat fort
  - Kewl Tune Reco / Rotary / Cue / Synchro / Mix : 7 000-9 000 views/week
  - Synchro Overtake, Kewl Tune Clip, JJ "Kewl Tune"
  - Note : Pot of Desires présent car en dessous du seuil 20% staple cross-format
- Fydraulis Harmonia est un bridge card : présente dans Kewl Tune (89%) ET Chaos Ritual (89%) → double signal

---

## Structure du projet
```
yugioh-meta-analyzer/
├── app.py                              # Dashboard Streamlit (6 pages)
├── run.sh                              # Lance streamlit run app.py avec venv
├── BACKLOG.md                          # Backlog priorisé (P2-G ✅, SB-Z ✅)
├── context.md                          # Ce fichier
├── scripts/
│   ├── fetch_cards.py                  # YGOPRODeck API → data/raw/cards.json
│   ├── init_db.py                      # cards.json → yugioh.db
│   ├── fetch_tournament_decks.py       # yugiohmeta.com TCG → yugioh.db
│   ├── fetch_ocg_decks.py              # yugiohmeta.com OCG → yugioh.db (ocg=1)
│   ├── explore_limitless.py            # outil diagnostic Playwright
│   └── setup_impact_tables.py         # génère ban_impact + card_impact
├── data/
│   ├── raw/cards.json                  # ~31 MB, 13 797 cartes TCG (non tracké Git)
│   ├── yugioh.db                       # base SQLite principale (non trackée Git)
│   ├── boutique_alert_score.png        # graphe OCG alert score
│   ├── ocg_tcg_correlation.png        # graphe corrélation OCG→TCG
│   ├── graph_maliss.html
│   ├── graph_tenpai.html
│   ├── graph_ryzeal.html
│   ├── graph_branded.html
│   ├── graph_combo_MsZb_dJAGHo.html
│   └── SOURCES.md
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_cooccurrence.ipynb
│   ├── 03_graph.ipynb
│   ├── 04_meta_score.ipynb
│   ├── 05_meta_prediction.ipynb
│   ├── 06_card_ban_impact.ipynb
│   ├── 08_nlp_combos.ipynb
│   ├── 09_ocg_tcg_correlation.ipynb   # Corrélation OCG→TCG, lag 4 mois ✅
│   └── 10_boutique_alert_score.ipynb  # Score alerte boutiques ✅
└── .venv/
```

---

## Schema SQLite (data/yugioh.db)
- `cards` : id, name, type, frame_type, desc, archetype, atk, def, level, race, attribute, ban_tcg, ban_ocg, ban_goat, tcg_date, ocg_date, views, views_week, md_rarity
- `card_sets` : card_id, set_name, set_code, set_rarity, set_price
- `card_prices` : card_id, cardmarket_price, tcgplayer_price, ebay_price, amazon_price, coolstuffinc_price
- `tournament_decks` : id, author, archetype, tournament_type, tournament_location, placement, created, uploaded, ocg, illegal, incomplete
- `deck_cards` : id, deck_id, card_name, amount, zone (main/extra/side)
- `card_cooccurrence` : card_a, card_b, jaccard, cooc_count
- `card_cooccurrence_side` : card_a, card_b, jaccard, cooc_count
- `meta_scores` : month, archetype, meta_score, share, avg_placement, placement_score_norm
- `archetype_trend` : archetype, meta_score_recent, meta_score_past, trend_ratio, label
- `ban_impact` : card, ban_status, ban_month_inferred, peak_usage, drop_ratio, top_archetype, delta_meta_score, n_archetypes_affected, total_appearances
- `card_impact` : card_name, release_month, n_archetypes_3m, total_decks_3m, bridge_score, top_archetype, delta_meta_score_top_arch
- `combo_mentions` : video_id, card_name, mention_count
- `combo_edges` : video_id, card_a, card_b, weight
- `boutique_alerts` : archetype, alert_score, meta_score_ocg, share_ocg, avg_views_week, n_key_cards, tcg_entry_estimated, computed_at
- `boutique_card_alerts` : archetype, card_name, frequency, views_week, card_alert_score

---

## APIs

### YGOPRODeck v7
- Base URL : `https://db.ygoprodeck.com/api/v7/cardinfo.php`
- Paramètres utiles : `misc=yes`, `format=tcg`, `archetype=X`, `banlist=tcg`, `sort=X`
- Autres endpoints : `/archetypes.php`, `/cardsets.php`, `/randomcard.php`
- Rate limit : 20 req/s

### yugiohmeta.com (non officielle)
- Base URL : `https://www.yugiohmeta.com/api/v1/top-decks`
- TCG : `ocg[$ne]=true`, OCG : `ocg=true`
- Paramètres : `uploaded[$gte]=YYYY-MM-DD`, `limit=100`, `skip=N`, `sort[uploaded]=-1`
- Pas de clé requise, headers Referer recommandés
- Autres endpoints à explorer : `/api/v1/tier-list` (non confirmé)

---

## Prochaines priorités (backlog)
1. **P1-B** — NLP sur texte des effets `desc` (synergies textuelles, notebook 07)
2. **P2-H** — Co-occurrence sur fenêtre glissante 90j
3. **P2-Q** — Récupérer la tier list yugiohmeta.com
4. **P3-R** — Features lag temporelles pour corriger le R²≈-37
5. **P4-W** — Appliquer la blacklist NLP dans notebook 08

*Dernière mise à jour : juin 2026*

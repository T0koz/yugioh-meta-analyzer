# Yu-Gi-Oh! Meta Analyzer

Outil d'analyse et de prédiction de la méta Yu-Gi-Oh! via IA.

**Problème :** aucun outil structuré pour préparer ses decks et anticiper l'impact d'une nouvelle carte ou d'une banlist sur la méta.

**Vision B2B :** signal OCG→TCG validé (r=0.771, lag=4 mois) — les boutiques peuvent acheter le stock 4 mois avant l'explosion TCG.

---

## Roadmap

| Phase | Statut | Description |
|-------|--------|-------------|
| 1 | ✅ | API YGOPRODeck + base SQLite + images + prix historique |
| 2 | ✅ | Decklists tournoi (19 888) + co-occurrence (6 variantes) + graphe synergies |
| 3 | ✅ | Score méta + banlist historique + modèle prédictif (Ridge + AR(1) + Naïf) |
| 4 | ✅ | Dashboard Streamlit (9 pages) + NLP combos YouTube + signal précoce |
| Signal boutiques | ✅ | OCG + views_week → score d'alerte. Kewl Tune 100/100 pour oct 2026 |
| 5 | 🔜 | Front-end React + API FastAPI + déploiement |

---

## Stack

- **Python 3.13**, VS Code, Git
- **Libs :** pandas, numpy, scikit-learn, networkx, pyvis, streamlit, plotly, statsmodels, youtube-transcript-api
- **DB :** SQLite (`data/yugioh.db`, ~150 MB, non trackée Git) — 35+ tables
- **Cron :** snapshot quotidien des prix (toutes cartes, 1 appel bulk API)

---

## Structure

```
yugioh-meta-analyzer/
├── app.py                              # Dashboard Streamlit (9 pages)
├── scripts/
│   ├── fetch_cards.py                  # YGOPRODeck API → data/raw/cards.json
│   ├── init_db.py                      # cards.json → yugioh.db
│   ├── fetch_tournament_decks.py       # yugiohmeta.com TCG → yugioh.db
│   ├── fetch_ocg_decks.py              # yugiohmeta.com OCG → yugioh.db
│   └── snapshot_prices.py              # Cron quotidien — prix toutes cartes
├── notebooks/
│   ├── 01_exploration.ipynb            # Exploration cartes
│   ├── 02_cooccurrence.ipynb           # Co-occurrence (6 variantes) + extra deck
│   ├── 03_graph.ipynb                  # Graphe synergies + centralité + communautés
│   ├── 04_meta_score.ipynb             # Score méta + tier list
│   ├── 05_meta_prediction.ipynb        # Modèle prédictif (Ridge + AR(1) + Naïf)
│   ├── 06_card_ban_impact.ipynb        # Bridge score + impact bans
│   ├── 07_nlp_text_synergies.ipynb     # NLP texte effets (TF-IDF + tags mécaniques)
│   ├── 08_nlp_combos.ipynb             # NLP combos YouTube (transcripts)
│   ├── 09_banlist_history.ipynb        # Historique banlist (Yugipedia)
│   ├── 09_ocg_tcg_correlation.ipynb    # Corrélation OCG→TCG
│   ├── 10_archetypes_official.ipynb    # Archetypes officiels YGOPRODeck
│   ├── 10_boutique_alert_score.ipynb   # Score alerte boutiques
│   ├── 11_early_card_signal.ipynb      # Signal précoce nouvelles cartes
│   └── 12_deck_clustering.ipynb        # Clustering decks (Combo/Control/OTK/Midrange)
└── context.md                          # Contexte technique complet
```

---

## Installation

```bash
git clone https://github.com/thomascozian/yugioh-meta-analyzer.git
cd yugioh-meta-analyzer

python3 -m venv .venv
source .venv/bin/activate

pip install pandas numpy jupyter ipykernel networkx pyvis scikit-learn \
            streamlit plotly statsmodels youtube-transcript-api requests
```

## Reconstruire la base de données

```bash
# 1. Cartes (YGOPRODeck) + images
python scripts/fetch_cards.py
python scripts/init_db.py

# 2. Decklists tournoi
python scripts/fetch_tournament_decks.py
python scripts/fetch_ocg_decks.py

# 3. Tables d'impact
python scripts/setup_impact_tables.py

# 4. Snapshot prix initial
python scripts/snapshot_prices.py

# 5. Lancer les notebooks dans l'ordre (01 → 12)
```

## Lancer le dashboard

```bash
source .venv/bin/activate
streamlit run app.py
# → http://localhost:8501
```

---

## Données clés

- **13 797 cartes TCG** avec effets, stats, archetypes, banlist, images, prix (YGOPRODeck v7)
- **19 888 decklists** de tournois TCG+OCG 2024-2026 (yugiohmeta.com)
- **Score méta :** `sqrt(share × placement_score_norm)` — 29 mois d'historique
- **Modèle prédictif :** Spearman ρ ≈ +0.65 (walk-forward CV, 9 mois de fenêtre)
- **Graphe synergies :** ~660 nœuds, 63 communautés, centralité betweenness approximée
- **Corrélation OCG→TCG :** r=0.771, p<0.0001, lag=4 mois (n=43 paires archetype/mois)

Voir [`context.md`](context.md) pour le détail technique complet de chaque phase.

# Yu-Gi-Oh! Meta Analyzer

Outil d'analyse et de prédiction de la méta Yu-Gi-Oh! via IA.

**Problème :** aucun outil structuré pour préparer ses decks et anticiper l'impact d'une nouvelle carte ou d'une banlist sur la méta.

**Vision :** modéliser les combos dominants des decks gagnants, détecter automatiquement quand une nouvelle carte bouleverse la méta, et visualiser tout ça dans une interface claire.

---

## Roadmap

| Phase | Statut | Description |
|-------|--------|-------------|
| 1 | ✅ | API YGOPRODeck + base SQLite + exploration Pandas |
| 2 | ✅ | Decklists tournoi (yugiohmeta.com) + co-occurrence + graphe synergies |
| 3 | ✅ | Score méta + trends + modèle prédictif sklearn |
| 4 | ✅ | Dashboard Streamlit + NLP combos (transcripts YouTube) |
| 5 | 🔜 | Front-end React + API FastAPI |

---

## Stack

- **Python 3.13** (Homebrew), VS Code, Git
- **Libs :** pandas, numpy, networkx, pyvis, scikit-learn, streamlit, plotly, youtube-transcript-api
- **DB :** SQLite (`data/yugioh.db`, ~70 MB, non trackée Git)

---

## Structure

```
yugioh-meta-analyzer/
├── app.py                          # Dashboard Streamlit (6 pages)
├── scripts/
│   ├── fetch_cards.py              # YGOPRODeck API → data/raw/cards.json
│   ├── init_db.py                  # cards.json → yugioh.db
│   ├── fetch_tournament_decks.py   # yugiohmeta.com → yugioh.db (9 330 decklists)
│   ├── explore_limitless.py        # Exploration Playwright (diagnostic)
│   └── setup_impact_tables.py      # Génère ban_impact + card_impact dans yugioh.db
├── data/
│   ├── yugioh.db                   # Base SQLite principale (~70 MB, gitignored)
│   ├── graph_maliss.html           # Graphes de synergies interactifs (pyvis)
│   ├── graph_tenpai.html
│   ├── graph_ryzeal.html
│   ├── graph_branded.html
│   ├── graph_combo_*.html          # Graphes combos NLP
│   └── SOURCES.md                  # Documentation des sources de données
├── notebooks/
│   ├── 01_exploration.ipynb        # Exploration cartes (types, archetypes, prix, banlist)
│   ├── 02_cooccurrence.ipynb       # Co-occurrence pondérée + Jaccard + side deck
│   ├── 03_graph.ipynb              # Graphe NetworkX (520 nœuds, 46 communautés)
│   ├── 04_meta_score.ipynb         # Score méta sqrt(share × placement_norm) + trends
│   ├── 05_meta_prediction.ipynb    # Modèle prédictif sklearn (Ridge, RF, GB)
│   ├── 06_card_ban_impact.ipynb    # Bridge score nouvelles cartes + détection bans
│   └── 08_nlp_combos.ipynb         # NLP combos via transcripts YouTube
└── context.md                      # Contexte technique détaillé (à lire avant de coder)
```

---

## Installation

```bash
git clone https://github.com/thomascozian/yugioh-meta-analyzer.git
cd yugioh-meta-analyzer

python3 -m venv .venv
source .venv/bin/activate

pip install pandas numpy jupyter ipykernel networkx pyvis scikit-learn \
            streamlit plotly youtube-transcript-api
```

## Reconstruire la base de données

```bash
# 1. Cartes (YGOPRODeck)
python scripts/fetch_cards.py
python scripts/init_db.py

# 2. Decklists tournoi (yugiohmeta.com)
python scripts/fetch_tournament_decks.py

# 3. Tables d'impact (ban_impact + card_impact)
python scripts/setup_impact_tables.py
```

Ensuite lancer les notebooks dans l'ordre (01 → 06) pour reconstruire toutes les tables analytiques.

## Lancer le dashboard

```bash
source .venv/bin/activate
streamlit run app.py
# → http://localhost:8501
```

---

## Données clés

- **13 797 cartes TCG** avec effets, stats, archetypes, banlist, prix (YGOPRODeck v7)
- **9 330 decklists** de tournois TCG 2024-2026 (yugiohmeta.com)
- **Score méta** : `sqrt(share × placement_score_norm)` — moyenne géométrique volume × performance
- **Bridge score** : `n_archetypes × log(total_decks_3m)` — mesure l'impact d'une nouvelle carte
- **Graphe synergies** : 520 nœuds, 2 326 arêtes, 46 communautés (Jaccard pondéré > 0.1)

---

## Contexte détaillé

Voir [`context.md`](context.md) pour le détail technique complet de chaque phase, les choix de modélisation, les erreurs rencontrées et les pistes d'amélioration.

# Yu-Gi-Oh! Meta Analyzer

Outil d'analyse et de prédiction de la méta Yu-Gi-Oh! via IA.

**Problème :** aucun outil structuré pour préparer ses decks et anticiper l'impact d'une nouvelle carte ou d'une banlist sur la méta.

**Vision B2B :** la part d'un archétype en OCG annonce en partie sa part en TCG quelques mois plus tard (r ≈ 0,53 à 4 mois,
IC 95 % [0,43 ; 0,59], 105 archétypes, plateau de 2 à 6 mois ; TOK-73, [`docs/evaluation-prediction.md`](docs/evaluation-prediction.md)).
L'ancien r = 0,771 (n = 43) n'est pas reproductible (cible mélangée TCG + OCG).

---

## Roadmap

| Phase | Statut | Description |
|-------|--------|-------------|
| 1 | ✅ | API YGOPRODeck + base SQLite + images + prix historique |
| 2 | ✅ | Decklists tournoi (23 948 au 2026-11-16) + co-occurrence (6 variantes) + graphe synergies |
| 3 | ✅ | Score méta + banlist historique + modèle prédictif (70 % naïf + 30 % Ridge ; AR(1) testé, écarté) |
| 4 | ✅ | Dashboard Streamlit (9 pages) + NLP combos YouTube + signal précoce |
| Signal boutiques | ✅ | Archétypes OCG pas encore en TCG, libellé = rang parmi les archétypes OCG (seuils provisoires, TOK-113) |
| 5 | 🏗️ | Front-end Next.js (12 pages) + API FastAPI (16 endpoints) livrés ; déploiement Vercel préparé, non fait (TOK-35) |

---

## Stack

- **Python 3.13**, VS Code, Git
- **Libs :** pandas, numpy, scikit-learn, networkx, pyvis, streamlit, plotly, statsmodels, youtube-transcript-api
- **Front :** Next.js 16, React 19, TypeScript, Tailwind CSS v4, graphiques SVG calculés avec D3 (voir `frontend/AGENTS.md`)
- **DB :** SQLite (`data/yugioh.db`, ~236 MB, non trackée Git) — 49 tables au 2026-11-18
  - `data/serving.db` (~12 MB) : les 20 tables de `SERVED_TABLES`, pour le déploiement
- **Job du lundi :** `scripts/refresh_decks.py` (decks, banlists, légalité, tables dérivées, base de service, fraîcheur)

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
│   ├── fetch_new_cards.py              # cartes nouvelles → cards (sans réécrire l'existant)
│   ├── fetch_banlist_history.py        # Yugipedia TCG + OCG → banlist_history
│   ├── compute_deck_legality.py        # légalité de chaque deck à sa date → deck_legality
│   ├── refresh_decks.py                # job du lundi (appelle refresh_all.py)
│   ├── refresh_all.py                  # tables dérivées (--list pour l'ordre)
│   ├── build_ban_radar.py              # Score de risque de ban (+ --backtest)
│   ├── build_*.py                      # autres tables dérivées (voir docs/architecture.md)
│   ├── build_serving_db.py             # yugioh.db → serving.db (déploiement)
│   ├── check_freshness.py              # fraîcheur des tables servies (TOK-93)
│   ├── check.py                        # vérifications avant push
│   └── snapshot_prices.py              # relevé de prix (dans refresh_all.py)
├── backend/                            # API FastAPI (lecture seule, 16 endpoints)
├── frontend/                           # Next.js — 12 pages
├── moteur_combos/                      # moteur de combos (TOK-84, base à part data/combos.db)
├── notebooks/
│   ├── 01_exploration.ipynb            # Exploration cartes
│   ├── 02_cooccurrence.ipynb           # Co-occurrence (6 variantes) + extra deck
│   ├── 03_graph.ipynb                  # Graphe synergies + centralité + communautés
│   ├── 04_meta_score.ipynb             # Score méta TCG + OCG
│   ├── 05_meta_prediction.ipynb        # Modèle prédictif (70 % naïf + 30 % Ridge)
│   ├── 06_card_ban_impact.ipynb        # Bridge score + impact bans
│   ├── 07_nlp_text_synergies.ipynb     # NLP texte effets (TF-IDF + tags mécaniques)
│   ├── 08_nlp_combos.ipynb             # NLP combos YouTube (transcripts)
│   ├── 09_banlist_history.ipynb        # Historique banlist (Yugipedia)
│   ├── 09_ocg_tcg_correlation.ipynb    # Corrélation OCG→TCG
│   ├── 10_archetypes_official.ipynb    # Archetypes officiels YGOPRODeck
│   ├── 10_boutique_alert_score.ipynb   # Score alerte boutiques
│   ├── 11_early_card_signal.ipynb      # Signal précoce (calcul repris par scripts/build_early_signals.py)
│   └── 12_deck_clustering.ipynb        # Clustering decks (Combo/Control/OTK/Midrange)
└── context.md                          # Contexte technique complet
```

---

## Installation

```bash
git clone https://github.com/T0koz/yugioh-meta-analyzer.git
cd yugioh-meta-analyzer

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt   # versions figées (scripts, notebooks, API, tests)
```

## Reconstruire la base de données

```bash
# 1. Cartes (YGOPRODeck), une seule fois : init_db.py écrase views_week, ne jamais le mettre dans la chaîne
python scripts/fetch_cards.py
python scripts/init_db.py

# 2. Graphe (notebook 03) et NLP (notebooks 07, 08) : hors chaîne, à lancer à la main
#    (03 dépend de card_cooccurrence, produite par le notebook 02 dans l'étape suivante)

# 3. Chaîne hebdomadaire : cartes nouvelles, decks TCG + OCG, banlists, légalité,
#    tables dérivées (refresh_all.py), base de service, contrôle de fraîcheur
python scripts/refresh_decks.py

# 4. Historique du Ban Radar (hors chaîne), puis base de service
python scripts/build_ban_history.py
python scripts/build_serving_db.py

# Toute retouche du scoring : backtest obligatoire
python scripts/build_ban_radar.py --backtest
```

## Préparer le déploiement

```bash
# Base réduite aux 20 tables servies (SERVED_TABLES) : ~12 Mo au lieu de 236
python scripts/build_serving_db.py

# Le backend la lit via YGO_DB_PATH
YGO_DB_PATH=/app/data/serving.db uvicorn app.main:app

# Déploiement Vercel (voie 2, Thomas seul) : voir docs/deploiement.md
python scripts/deploy_prebuilt.py
```

## Lancer le dashboard

```bash
source .venv/bin/activate
streamlit run app.py
# → http://localhost:8501
```

---

## Données clés

Effectifs relevés le 2026-11-18 sur la base de référence.

- **14 084 cartes** avec effets, stats, archetypes, banlist, images, prix (YGOPRODeck v7)
- **23 948 decklists** de tournois (11 618 TCG, 12 330 OCG, 2023-2026, yugiohmeta.com), dernier deck relevé le 2026-11-14
- **Score méta :** `sqrt(share × placement_score_norm)`, decks légaux à la date du tournoi
- **Modèle prédictif :** 70 % naïf + 30 % Ridge ; ρ de rang 0,688 contre 0,679 pour le naïf (écart +0,009,
  IC 95 % [+0,003 ; +0,016]), MAE de la variation −4 % contre la persistance (TOK-73, `docs/evaluation-prediction.md`)
- **Graphe synergies :** 663 nœuds, 63 communautés (notebook 03, périmé : le graphe recalculé en compte 1 402, TOK-136)
- **Corrélation OCG→TCG :** r ≈ 0,53 à 4 mois, IC 95 % [0,43 ; 0,59], 105 archétypes, plateau de 2 à 6 mois (TOK-73)

Voir [`context.md`](context.md) pour le détail technique complet de chaque phase.

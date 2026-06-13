# Yu-Gi-Oh! Meta Analyzer

Outil d'analyse et de prédiction de la méta Yu-Gi-Oh! via IA.

**Problème :** pas d'outil structuré pour préparer ses decks et anticiper l'impact d'une nouvelle carte sur la méta.

**Vision :** modéliser les combos dominants des decks gagnants, détecter automatiquement quand une nouvelle carte bouleverse la méta, et visualiser tout ça dans une interface claire.

## Roadmap
- **Phase 1** ✅ — API YGOPRODeck + base SQLite + exploration Pandas
- **Phase 2** — Scraping decklists tournoi (Limitless TCG) + graphe de synergies (NetworkX)
- **Phase 3** — Score méta + modèle prédictif (sklearn)
- **Phase 4** — NLP transcripts YouTube (Whisper) + interface Streamlit
- **Phase 5** — Front-end web

## Stack
Python 3.13, Pandas, SQLite, NetworkX, Sklearn, Streamlit

## Structure
```
yugioh-meta-analyzer/
├── scripts/
│   ├── fetch_cards.py      # Fetch toutes les cartes TCG via API YGOPRODeck
│   └── init_db.py          # Charge les cartes en base SQLite
├── data/
│   └── yugioh.db           # Base SQLite (13 797 cartes, non trackée par Git)
├── notebooks/
│   └── 01_exploration.ipynb
└── context.md              # Contexte détaillé du projet
```

## Lancer le projet
```bash
# Créer et activer le venv
python3 -m venv .venv
.venv/bin/pip install requests pandas jupyter ipykernel

# Récupérer les données
python3 scripts/fetch_cards.py
python3 scripts/init_db.py
```

# Yugioh Meta Analyzer — Context

## Projet
Outil d'analyse et de prédiction de la méta Yu-Gi-Oh! via IA.
Problème : pas d'outil structuré pour préparer ses decks et anticiper l'impact d'une nouvelle carte sur la méta.

## Profil
Thomas Cozian — ex consultant e-commerce ZeTrace, ex PO refonte B2B headless.
Formation Le Wagon Data Science & IA débutant le 12 octobre.

## Stack
- Python 3.13 (Homebrew), VS Code, Git, GitHub
- Venv : `.venv` à la racine du projet
- Libs installées : requests, pandas, jupyter, ipykernel
- SQLite pour le stockage local

## Vision produit
L'objectif est d'avoir un produit fini V2 avant Le Wagon (début octobre).
La méta Yu-Gi-Oh! moderne est structurée autour des combos : un deck est fort parce qu'il enchaîne 5-6+ cartes en un tour pour construire un board imbattable.
Le produit doit permettre de :
1. Identifier les combos dominants dans les decks gagnants
2. Mesurer la complexité et la robustesse de chaque combo (nombre de cartes requises, chemins alternatifs)
3. Détecter automatiquement quand une nouvelle carte s'insère comme raccourci dans un combo existant — c'est le signal méta le plus puissant
4. Visualiser tout ça dans une interface Streamlit claire

## Roadmap révisée
- Phase 1 (S1-S3) : API YGOPRODeck + base SQLite + exploration Pandas ✅
- Phase 2 (S4-S6) : Scraping decklists tournoi (Limitless TCG) + co-occurrence cartes + graphe de synergies (NetworkX)
- Phase 3 (S7-S8) : Score méta + modèle prédictif (sklearn) + détection d'impact d'une nouvelle carte
- Phase 4 (S9-S10) : Interface Streamlit + NLP transcripts YouTube (Whisper) pour extraire séquences de combo
  - Les noms de cartes sont très spécifiques → extractibles avec regex dans un premier temps
  - Chaque combo modélisé comme graphe orienté : carte A → carte B → carte C → board final
- Phase 5 : Front-end web pour présenter le produit fini (React ou autre) — visualisation des combos, score méta, impact des nouvelles cartes

## Sources de data identifiées
- YGOPRODeck API v7 : infos cartes, banlist, prix ✅
- Limitless TCG : decklists de tournoi avec placements (à scraper)
- YGOPRODeck site : meta decks TCG (à scraper)
- YouTube / Master Duel replays : séquences de combo (Phase 4, via Whisper)

## Ce qui est fait
- Environnement installé et configuré (Python 3.13 Homebrew, venv, VS Code)
- Repo GitHub créé : yugioh-meta-analyzer
- Structure de dossiers : scripts/, data/raw/, notebooks/
- `scripts/fetch_cards.py` : fetch toutes les cartes TCG via API YGOPRODeck v7 (misc=yes)
- `scripts/init_db.py` : charge cards.json dans SQLite (3 tables : cards, card_sets, card_prices)
- Base peuplée : 13 797 cartes, 43 145 sets, 13 797 prix
- `notebooks/01_exploration.ipynb` : exploration Pandas (types, attributs, archetypes, banlist, prix)

## Structure du projet
```
yugioh-meta-analyzer/
├── scripts/
│   ├── fetch_cards.py      # fetch API → data/raw/cards.json
│   └── init_db.py          # cards.json → data/yugioh.db (SQLite)
├── data/
│   ├── raw/cards.json      # ~31 MB, 13 797 cartes TCG
│   └── yugioh.db           # base SQLite principale
├── notebooks/
│   └── 01_exploration.ipynb
└── .venv/                  # environnement virtuel Python
```

## Schema SQLite (data/yugioh.db)
- `cards` : id, name, type, frame_type, desc, archetype, atk, def, level, race, attribute, link_val, scale, ban_tcg, ban_ocg, ban_goat, tcg_date, ocg_date, has_effect, views, views_week, md_rarity
- `card_sets` : id, card_id, set_name, set_code, set_rarity, set_price
- `card_prices` : card_id, cardmarket_price, tcgplayer_price, ebay_price, amazon_price, coolstuffinc_price

## API YGOPRODeck v7
- Base URL : `https://db.ygoprodeck.com/api/v7/cardinfo.php`
- Paramètres utiles : misc=yes, format=tcg, archetype=X, banlist=tcg, sort=X
- Autres endpoints : /archetypes.php, /cardsets.php, /cardsets.php, /randomcard.php
- Rate limit : 20 req/s, cache 2 jours côté serveur

## Prochaine étape
- Récupérer les données de méta tournoi (archetypes dominants, decks top)
- Croiser avec banlist et popularité pour construire un premier score méta

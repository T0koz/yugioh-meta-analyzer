# Yugioh Meta Analyzer — Context

## Projet
Outil d'analyse et de prédiction de la méta Yu-Gi-Oh! via IA.
Problème : pas d'outil structuré pour préparer ses decks et anticiper l'impact d'une nouvelle carte sur la méta.

## Profil
Thomas Cozian — ex consultant e-commerce ZeTrace, ex PO refonte B2B headless.
Formation Le Wagon Data Science & IA débutant le 12 octobre 2026.
Objectif : produit V2 fini avant Le Wagon.

---

## Stack
- Python 3.13 (Homebrew), VS Code, Git, GitHub
- Venv : `.venv` à la racine du projet
- Libs installées : requests, pandas, numpy, jupyter, ipykernel, networkx, pyvis, playwright
- SQLite pour le stockage local

---

## Vision produit
La méta Yu-Gi-Oh! moderne est structurée autour des combos : un deck est fort parce qu'il enchaîne 5-6+ cartes en un tour pour construire un board imbattable.
Le produit doit permettre de :
1. Identifier les combos dominants dans les decks gagnants
2. Mesurer la complexité et la robustesse de chaque combo (nombre de cartes requises, chemins alternatifs)
3. Détecter automatiquement quand une nouvelle carte s'insère comme raccourci dans un combo existant — c'est le signal méta le plus puissant
4. Visualiser tout ça dans une interface claire (Streamlit → React)

---

## Roadmap
- Phase 1 : API YGOPRODeck + base SQLite + exploration Pandas ✅
- Phase 2 : Decklists tournoi + co-occurrence + graphe de synergies ✅
- Phase 3 : Score méta + modèle prédictif (sklearn) + détection impact nouvelle carte
- Phase 4 : Interface Streamlit + NLP transcripts YouTube (Whisper) pour séquences de combo
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
- **Texte des effets (`desc`)** : chaque carte a un texte d'effet complet. On pourrait faire du NLP pour détecter des synergies textuelles ("si cette carte est invoquée...") sans avoir besoin de decklists. À explorer en Phase 3 ou 4.
- **Popularité Master Duel (`views`, `views_week`)** : l'API retourne le nombre de vues sur le site YGOPRODeck, qui reflète l'intérêt des joueurs. Une carte dont les vues explosent = signal précoce d'entrée en méta, avant même les tournois. Pas utilisé.
- **Dates de sortie (`tcg_date`, `ocg_date`)** : chaque carte a ses dates de sortie TCG et OCG. Couplé à l'analyse de co-occurrence temporelle (Phase 2), on pourrait tracer l'histoire méta d'un archetype. Pas utilisé.
- **Images des cartes** : l'API fournit des URLs d'images (small/normal/cropped). Non récupérées. Utiles pour le front-end Phase 5.
- **Rareté Master Duel (`md_rarity`)** : la rareté dans le jeu en ligne. Pas utilisée. Pourrait indiquer des cartes "premium" dans Master Duel.
- **Endpoint `/archetypes.php`** : liste officielle de tous les archetypes reconnus par Konami. Non utilisé. Permettrait un matching plus propre entre les archetypes qu'on détecte et les noms officiels.
- **Historique de banlist** : l'API ne donne que le statut actuel. Il faudrait une source externe pour l'historique (ex: yugiohmeta.com ou scraping de wiki) pour voir comment une carte a bougé dans la banlist au fil du temps.
- **Prix dans le temps** : les prix sont un snapshot instantané. Une intégration avec TCGPlayer History ou Cardmarket Price History permettrait de corréler l'évolution du prix avec l'entrée en méta.

---

## Phase 2 ✅ — Decklists tournoi + co-occurrence + graphe

### Ce qui a été fait

**Collecte des données de tournoi**
- `scripts/explore_limitless.py` : exploration via Playwright pour intercepter les appels réseau de yugiohmeta.com → API non documentée découverte à `https://www.yugiohmeta.com/api/v1/top-decks`
- `scripts/fetch_tournament_decks.py` : fetch paginé avec filtres `ocg[$ne]=true` et `uploaded[$gte]=2024-01-01`
  - 9 330 decklists TCG (2024-2026), 395 006 entrées de cartes
  - Tables SQLite créées : `tournament_decks`, `deck_cards`
  - Top archetypes : Maliss (829 decks), Dracotail (537), Snake-Eye (515), Ryzeal (468), Tenpai Dragon (454)

**Co-occurrence (notebooks/02_cooccurrence.ipynb) — v2 pondérée**
- Chargement toutes zones (main + extra + side) : 84 859 lignes, 2 008 decks légaux
- Poids par deck = `(1 / placement) × exp(-jours / 365)` → normalisé (mean=1, range [0.009, 4.394])
- Score par carte = `(amount / 3) × deck_weight` (quantités réelles, max 3 exemplaires)
- Matrice pondérée : 2 008 decks × 567 cartes (filtre : présente dans ≥ 10 decks)
- Jaccard pondéré : 4 444 paires (Jaccard > 0.1) → table `card_cooccurrence`
- Staples repondérées (>20%) : Ash Blossom (75%), Mulcharmy Fuwalos (73%), Forbidden Droplet (36%), Infinite Impermanence (33%), The Fallen & The Virtuous (32%), Ghost Belle (30%)
- **Side deck analysé séparément** → table `card_cooccurrence_side` (750 paires)
  - Top side deck : Mulcharmy Purulia (47%), Droll & Lock Bird (36%), Retaliating "C" (25%), Nibiru (23%), Lightning Storm (21%)
  - Signal : la méta est dominée par des combos de recherche → les joueurs sident des interrupteurs de recherche

**Graphe de synergies (notebooks/03_graph.ipynb)**
- Graphe NetworkX : 520 nœuds, 2 326 arêtes, 38 composantes, 46 communautés
- Cartes les plus centrales (weighted degree) : Lunalight, Monarchs — archetypes très "serrés"
- `simulate_ban()` : Ash Blossom → 5 connexions supprimées (ubiquité = faible Jaccard individuel) ; Maliss P March Hare → 14 connexions, fort impact core
- Visualisation Pyvis : Maliss (17c/108s), Tenpai (6c/15s), Ryzeal (12c/44s), Branded (39c/185s)
- Fichiers générés : `data/graph_*.html`
- **Classification des cartes** (fréquence globale × dispersion cross-archetype) :
  - `staple_format` (8 cartes, freq >25% ET >5 archetypes) : Ash Blossom (77%, 92 archetypes), Mulcharmy Fuwalos (71%, 87), Called by the Grave (49%, 87), Infinite Impermanence (40%, 75), Forbidden Droplet (38%, 77)
  - `tech_pont` (148 cartes, freq ≤25% ET >5 archetypes) : Nibiru (24%, 64), Droll & Lock Bird (24%, 59), Effect Veiler (25%, 46), Pot of Prosperity (18%, 39)
  - `piece_niche` (1531 cartes) : spécifiques à un archetype
  - Note : `staple_archetype` vide → méta diversifiée, aucun archetype ne domine suffisamment seul
  - À tuner : seuil fréquence à 10% pour capturer les cores d'archetypes dominants ; seuil à 20% pour inclure Nibiru/Droll dans staple_format

### Ce qu'on n'a pas exploité (à revisiter)

**Relation play style ↔ deck (à explorer en Phase 3)**
Les archetypes ne sont pas juste des listes de cartes — ils correspondent à des styles de jeu distincts :
- **Combo** : enchaîne 5-6+ cartes pour construire un board imbattable
- **Control/Stax** : floddgates + disruption (Gozen Match, Rivalry, Dimensional Fissure)
- **Midrange** : hand traps + lignes de combo modérées
- **OTK** : burst damage direct, peu de défense

Idée : clustériser les decks (pas les cartes) selon leur composition pour assigner automatiquement un style de jeu. Signaux existants : communauté 8 du graphe = clairement Stax (Card of Demise, Dimensional Fissure, Gozen Match), side deck révèle les styles adverses craints. Une fois le style assigné à chaque deck, on peut filtrer les staples par style ("quelles cartes jouent tous les decks Combo ?" vs "quelles cartes jouent tous les decks Control ?").

**Sur les données de tournoi**
- **Placements non pondérés** : dans la co-occurrence, un deck 1er place pèse autant qu'un deck 50e. Pondérer par `1 / placement` donnerait plus de poids aux decks qui ont vraiment gagné. Signal méta plus précis.
- **Side deck ignoré** : on a analysé uniquement le main deck. Le side deck est pourtant une mine d'info : il révèle quelles menaces le joueur anticipait (hate cards), ce qui reflète directement la méta perçue au moment du tournoi.
- **Extra deck ignoré** : même logique, l'extra deck révèle les win conditions (boss monsters). À analyser séparément.
- **Quantités ignorées** : on a traité la matrice en binaire (carte présente ou absente). Jouer 3 exemplaires d'une carte vs 1 est une information de design deck importante — ignorer ça atténue les vrais combos.
- **Dimension temporelle absente** : tous les decks 2024-2026 sont traités à égalité. Un archetype qui dominait il y a 18 mois pollue l'analyse actuelle. Ajouter une fenêtre glissante (ex: 3 mois) ou un poids exponentiel décroissant selon l'ancienneté.
- **`tournamentLocation` non utilisé** : certaines régions ont des métas différentes (Amérique du Nord vs Europe). On pourrait filtrer ou segmenter par région.
- **`tournament_type` non utilisé** : un Regional et un YCS n'ont pas le même niveau de compétition. Filtrer sur les gros tournois donnerait une méta de haut niveau plus pure.

**Sur le graphe**
- **Betweenness centrality non calculée** : identifie les cartes "pont" entre deux archetypes — souvent des staples ou des cartes en train d'émerger. Plus coûteux à calculer mais très informatif.
- **PageRank non utilisé** : variante de centralité qui tient compte du poids des voisins. Pourrait mieux identifier les cartes "moteurs" d'un combo.
- **61 communautés non nommées automatiquement** : on identifie les clusters mais on doit les nommer à la main. On pourrait nommer automatiquement chaque communauté par la carte avec le plus grand degré ou par matching avec les noms d'archetypes officiels (endpoint `/archetypes.php`).
- **Évolution du graphe dans le temps** : construire un graphe par trimestre et comparer → voir quand un archetype monte ou tombe.
- **Graphes générés seulement pour 4 archetypes** : Maliss, Tenpai, Ryzeal, Branded. Tous les autres archetypes sont visualisables avec la même fonction.

**Sources de données non encore utilisées**
- **yugiohmeta.com tier list** : il existe probablement un endpoint `/api/v1/tier-list` (à confirmer via Playwright). Donnerait le classement S/A/B/C des archetypes mis à jour régulièrement.
- **YGOPRODeck forums / communauté** : discussions sur les nouvelles cartes. Source textuelle potentielle pour détecter l'émergence d'un nouvel archetype.
- **Konami official banlist archive** : historique complet des banlists depuis 2002. Permettrait d'entraîner un modèle sur "quelles cartes ont été bannies et pourquoi".
- **Master Duel usage rates** : Konami publie parfois des stats d'utilisation en tournoi Master Duel. Complément aux données TCG physique.

---

## Phase 3 ✅ — Score méta + modèle prédictif

### Ce qui a été fait

**Score méta (notebooks/04_meta_score.ipynb)**
- `placement_score = 1 / avg_placement` par (archetype, mois)
- `placement_score_norm` : normalisé par le max du mois (0 → 1)
- `meta_score = sqrt(share × placement_score_norm)` — moyenne géométrique qui pénalise les archetypes qui jouent beaucoup mais ne gagnent pas
- Table `meta_scores` créée : 462 lignes (29 mois × ~16 archetypes/mois)
- **Trend** : fenêtre 60 jours récente vs 60 jours précédente → `trend_ratio = meta_score_recent / meta_score_past`
- Labels : ⬇️ chute forte / ↘️ déclin / ➡️ stable / ↗️ montée / ⬆️ émergence
- Table `archetype_trend` : 86 archetypes
- Résultats clés : DoomZ trend_ratio 4.217 (plus forte émergence), Blue-Eyes pic à 0.569 en fév 2025 puis disparu

**Modèle prédictif (notebooks/05_meta_prediction.ipynb)**
- Dataset : paires (T, T+1) pour 247 exemples (split temporel : train 2024-2025 / test 2026)
- 11 features : `meta_score`, `share`, `avg_placement`, `trend_ratio`, `n_banned`, `n_limited`, `n_semilimited`, `n_staples`, `avg_jaccard`, `n_pairs`, `max_jaccard`
- 3 modèles : Ridge (α=1.0), RandomForest (200 arbres, depth=5), GradientBoosting (200 arbres, depth=3, lr=0.05)
- Feature importance RF : avg_placement (42%), share (33%), meta_score (15%) — les features statiques (banlist, co-occurrence) sont marginales
- **Performances :** RMSE ~0.21 pour les 3 modèles, **R² ≈ -37 à -41** (très négatif)

### Ce qu'on n'a pas exploité (à revisiter)

**Problème central du modèle — Distribution shift**
Le R² fortement négatif révèle un problème de distribution shift : la méta 2026 est structurellement différente de 2024-2025. Le modèle régresse vers la moyenne d'entraînement au lieu de capturer la dynamique réelle. Causes identifiées :
- **Features statiques** : banlist, co-occurrence et trend_ratio sont calculés sur toute la période, pas par mois → pas de signal temporel fin
- **Manque de momentum** : il faudrait des features glissantes (meta_score des 3 derniers mois, momentum à court terme, accélération) pour capturer la dynamique
- **Trop peu de données** : 99 exemples d'entraînement sur 29 mois pour 86 archetypes → underfitting sévère

**Améliorations prioritaires du modèle**
- Ajouter des features lag temporelles : `meta_score_t-1`, `meta_score_t-2`, `meta_score_t-3` par archetype au moment de la prédiction
- Calculer trend_ratio par fenêtre glissante mensuelle (pas sur toute la période)
- Ajouter une feature `months_since_debut` (âge de l'archetype dans la méta)
- Utiliser un modèle séquentiel (LSTM ou ARIMA par archetype) plutôt qu'une régression cross-sectionnelle
- Banlist historique : encoder les changements de banlist dans le temps, pas seulement l'état actuel

**Notebook 06 — Détection impact nouvelle carte / ban (à faire)**
- Simuler l'insertion d'une nouvelle carte dans le graphe de co-occurrence
- Mesurer le raccourci créé : si la carte A se connecte à 3+ archetypes distincts avec Jaccard > 0.2, elle est "pont stratégique"
- Simuler un ban : supprimer un nœud du graphe, recalculer les composantes et mesurer la chute de méta_score prédite
- Source de signal : views_week (YGOPRODeck) comme signal précoce avant tournoi

**Sur la qualité des données**
- Les features de co-occurrence (`avg_jaccard`, `n_pairs`) sont calculées sur l'ensemble du corpus 2024-2026, pas dynamiquement par mois → bruit temporel
- Le `trend_ratio` est une feature globale alors qu'on cherche à prédire mois par mois
- Une version dynamique des features (calculées uniquement sur les 90 jours précédant T) améliorerait significativement le signal

## Phase 4 — Interface Streamlit + NLP combos
*(à venir)*
- Dashboard Streamlit : score méta, graphe interactif, simulation de ban
- YouTube / Whisper : transcrire les commentaires de gameplay pour extraire les séquences de combo
  - Noms de cartes très spécifiques → extractibles avec regex dans un premier temps
  - Chaque combo modélisé comme graphe orienté : carte A → carte B → carte C → board final

## Phase 5 — Front-end React
*(à venir)*
- Interface web complète pour présenter le produit V2
- Visualisation des combos, score méta, impact des nouvelles cartes et banlists

---

## Structure du projet
```
yugioh-meta-analyzer/
├── scripts/
│   ├── fetch_cards.py              # YGOPRODeck API → data/raw/cards.json
│   ├── init_db.py                  # cards.json → yugioh.db
│   ├── fetch_tournament_decks.py   # yugiohmeta.com → yugioh.db
│   └── explore_limitless.py        # outil d'exploration Playwright (diagnostic)
├── data/
│   ├── raw/cards.json              # ~31 MB, 13 797 cartes TCG (non tracké Git)
│   ├── yugioh.db                   # base SQLite principale (non trackée Git)
│   ├── graph_maliss.html           # graphe interactif Maliss
│   ├── graph_tenpai.html
│   ├── graph_ryzeal.html
│   ├── graph_branded.html
│   └── SOURCES.md                  # documentation des sources de data
├── notebooks/
│   ├── 01_exploration.ipynb        # exploration cartes
│   ├── 02_cooccurrence.ipynb       # co-occurrence + Jaccard
│   └── 03_graph.ipynb              # graphe NetworkX + Pyvis
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

---

## API YGOPRODeck v7
- Base URL : `https://db.ygoprodeck.com/api/v7/cardinfo.php`
- Paramètres utiles : `misc=yes`, `format=tcg`, `archetype=X`, `banlist=tcg`, `sort=X`
- Autres endpoints : `/archetypes.php`, `/cardsets.php`, `/randomcard.php`
- Rate limit : 20 req/s

## API yugiohmeta.com (non officielle)
- Base URL : `https://www.yugiohmeta.com/api/v1/top-decks`
- Paramètres utiles : `ocg[$ne]=true`, `uploaded[$gte]=YYYY-MM-DD`, `limit=100`, `skip=N`, `sort[uploaded]=-1`
- Pas de clé requise, headers Referer recommandés
- Autres endpoints à explorer : `/api/v1/tier-list` (non confirmé)

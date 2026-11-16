# Onboarding — Yu-Gi-Oh! Meta Analyzer

> Pour une data scientist qui rejoint le projet. Temps de lecture : ~15 min.
> État des chiffres : 16 novembre 2026 (après nettoyage du backlog fiabilité). En cas de doute, `context.md` fait foi (c'est la
> mémoire du projet, mise à jour après chaque fonctionnalité).

## 1. En cinq lignes

- **Quoi :** un outil qui analyse la méta compétitive de Yu-Gi-Oh! (quels decks gagnent,
  quelles cartes montent) et essaie de **l'anticiper**.
- **Pour qui :** à terme, les boutiques de cartes (B2B, abonnement) qui doivent commander
  leur stock des mois avant que la demande n'explose ; et les joueurs (site public).
- **Thèse centrale :** le format japonais (OCG) précède le format occidental (TCG) d'environ
  **4 mois** (annoncé : r = 0,771, n = 43 ; **recalculé le 2026-11-16 : r ≈ 0,53 à 4 mois, IC95 [0,43 ; 0,59]**, voir §4). Un archétype qui domine
  l'OCG aujourd'hui dominera probablement le TCG dans quatre mois : signal d'achat.
- **Second produit :** le **Ban Radar**, un score 0-100 du risque qu'une carte soit bannie à
  la prochaine liste.
- **Où on en est :** pipeline de données, modèles, API et site (Next.js) existent et tournent
  sur de vraies données. Ce qui manque surtout, c'est de la **rigueur statistique** : voir §5.

Thomas (le fondateur) apprend la data science en parallèle (bootcamp). Il veut comprendre
*pourquoi* un choix est fait : documente et explique tes décisions de modélisation.

## 2. Les données

| Source | Contenu | Volume | Fragilité |
|---|---|---|---|
| **YGOPRODeck** (API v7) | Cartes, effets, archétypes, banlist courante, prix, popularité (`views_week`) | 13 797 cartes | API publique, stable |
| **yugiohmeta.com** (API *non officielle*) | Decklists des top-coupes de tournois, TCG + OCG, depuis 2024 | ~21 200 decks, ~850 000 lignes `deck_cards` | **Point de défaillance unique** : endpoint non documenté, sans clé, qui peut être coupé. Les données y sont collectées par un réseau communautaire (soumissions de joueurs/organisateurs), pas par un flux officiel |
| **Yugipedia** (scraping) | Historique des banlists TCG + OCG | ~24 000 lignes | Wiki : amende les listes passées rétroactivement, donc la table est reconstruite intégralement à chaque run |
| **YouTube** (transcripts) | Séquences de cartes citées dans des combo guides | quelques centaines de lignes | Transcription automatique qui déforme les noms japonais (« Kewl Tune » → « Cool Tune ») |

Stockage : **SQLite** (`data/yugioh.db`, ~236 Mo, 36 tables). Les tables dérivées
(scores, prédictions, graphe…) sont produites par les notebooks et scripts, pas par l'API.
Schéma complet : [`data-models.md`](data-models.md).

## 3. Architecture

```
 scripts/fetch_*.py ──► data/yugioh.db ──► notebooks 01→12 + scripts/build_*.py
 (YGOPRODeck,            (tables brutes)        │ (tables dérivées : meta_scores,
  yugiohmeta, Yugipedia)                        │  meta_predictions, boutique_*, ban_radar…)
                                                ▼
                        scripts/build_serving_db.py ──► data/serving.db (9 Mo, 12 tables)
                                                                 │ lecture seule
                                                                 ▼
                                              backend/ (FastAPI) ──► frontend/ (Next.js 16)
```

- L'API ne calcule rien : elle sert des tables **précalculées**. Toute la science est en
  amont, dans `notebooks/` et `scripts/`.
- Un dashboard Streamlit historique (`app.py`) existe encore ; le site Next.js est la cible.
- **Il n'y a aucun test automatisé dans le dépôt.** Le seul garde-fou *statistique* est le
  backtest du Ban Radar (§7) ; côté API, `build_serving_db.py --check` vérifie seulement
  que les tables servies existent.

## 4. Ce que font les modèles — et leurs réserves

Chiffres **recalculés le 2026-11-16** sur des données rafraîchies (23 948 decks, jusqu'au 14 novembre) et
filtrées par `deck_legality`. Détail et code : [`evaluation-prediction.md`](evaluation-prediction.md).

| Composant | Méthode | Résultat mesuré (2026-11-16) | Réserve |
|---|---|---|---|
| **Score méta** (`meta_scores`, `meta_scores_ocg`) | `sqrt(share × placement_score_norm)` par archétype et mois (mois = date du tournoi, decks légaux) | `meta_scores` = TCG pur : 1 316 lignes, 211 archétypes ; `meta_scores_ocg` : 1 530 lignes, 227 archétypes (TOK-80) | Formule heuristique ; ~30 decks par archétype et par mois : bruitée. Genesys exclu (légalité par points) |
| **Prédiction** (`meta_predictions`) | 70 % naïf + 30 % Ridge (α = 50, ~20 features), walk-forward 9 mois | Sur la **variation**, TCG pur : ρ = +0,42 [+0,25 ; +0,57], MAE −6 % vs persistance (ancienne table mixte : +0,35 et −4 %) | Une régression à une variable fait aussi bien (ρ +0,40) ; ensemble − naïf en niveau : +0,012 [−0,014 ; +0,041], indistinguable de zéro ; ne prédit jamais l'entrée d'un nouvel archétype ; W = 0,3 non validé |
| **Signal OCG → TCG** | Corrélation OCG(t) / TCG(t+L) | r ≈ **0,53** à 4 mois (n = 652 paires, 105 archétypes, IC95 [0,43 ; 0,59]) ; plateau de 2 à 6 mois ; survit à la permutation par archétype, au décalage circulaire, à la baseline autorégressive, à la validation par archétype | **r = 0,771 (n = 43) non reproductible** : il était mesuré contre une cible mêlant OCG et TCG (r = 0,92 à lag 0). Depuis TOK-80, le notebook 09 donne r = 0,574 (lag 2) et 0,475 (lag 4) sur un TCG pur. « 4 mois » est un artefact du choix du max, pas un pic |
| **Score d'alerte boutique** | `meta_score_ocg × log(1 + vues)` hors staples et cartes bannies TCG | Le 17 juin, « Kewl Tune 100/100 » ; 34 cartes du signal : **−35 %** de prix (marché −1 %), IC95 de l'écart [−50 % ; +1 %] | Kewl Tune pesait déjà 22-32 % du TCG avant le signal, puis a été banni ; une seule date de signal. Le `buy_score` v2 (TOK-81) intègre le prix sur 0-100, non validé sur des ventes |
| **Ban Radar** | Score 0-100, 6 critères pondérés à la main | Backtest sur decks légaux : TCG 2026-05-18 rang médian 84/889, OCG 2026-07-01 19/1236 ; 10 listes TCG et 10 OCG évaluables | Les deux dernières listes TCG sont mauvaises au rang médian (206 et 308, hasard ≈ 450-490), alors que le haut du classement tient (voir `context.md`) ; poids non appris, calés sur la liste de mai 2026 |
| **Graphe de synergies** | Co-occurrence pondérée → NetworkX, 63 communautés | Non recalculé le 2026-11-16 | Descriptif |
| **Clustering de decks** | K-Means k = 4 | Silhouette 0,171, non recalculé | Faible |
| **NLP** | TF-IDF, combos YouTube | — | Bruit d'ASR |
| **Journal des prédictions** | `prediction_log` append-only + jsonl | 3 781 lignes dont les lots `live` du 2026-11-16 ; `scripts/validate_predictions.py` compare à la réalité | Aucune prévision `live` n'est échue avant décembre 2026 ; les lots `backfill` ne prouvent rien |

> Les libellés « AR(1) » encore présents dans certains documents sont trompeurs : l'AR(1) a été testé puis
> écarté (notebook 05). TOK-25 a été renommé dans Linear.

## 5. Là où ton expertise change vraiment la donne

Classés par impact. Les trois premiers touchent à la **validité** de ce qu'on affiche.

1. **Biais de survie dans les données (le plus urgent).** Le drapeau `illegal` de l'API
   yugiohmeta est évalué contre une banlist *postérieure* au tournoi. Avant février 2026
   (TCG) et avril 2026 (OCG), 90 à 100 % des decks sont jugés illégaux ; le filtre
   `illegal = 0` des notebooks 02, 03, 04, 09, 10, 12 et de `build_ban_radar.py` jette donc
   l'essentiel de l'historique, **en priorité les decks qui jouaient des cartes bannies
   ensuite**. L'étape 1 est faite (`scripts/compute_deck_legality.py` → table
   `deck_legality`, 20 220 decks légaux sur ~21 200). **L'étape 2 est faite (2026-11-16)** : consommateurs rebranchés,
   tout recalculé (`scripts/refresh_all.py`), backtest relancé. Les chiffres de vitrine (r = 0,771…)
   ont changé : voir §4.
2. ~~**Évaluer la prédiction sur ce qu'elle prétend prédire.**~~ *(fait : `evaluation-prediction.md`)* Mesurer la corrélation des
   *variations* prédites et réalisées, ajouter des intervalles de confiance (bootstrap par
   mois), et comparer systématiquement à la baseline de persistance. Aujourd'hui le gain du
   modèle sur le naïf est indiscernable du bruit.
3. ~~**Robustesse du signal OCG → TCG.**~~ *(fait ; reste à séparer TCG et OCG dans `meta_scores`)* Test de permutation, validation croisée *par
   archétype*, balayage des lags avec correction pour comparaisons multiples, intervalle de
   confiance. C'est la thèse du produit B2B : c'est elle qui doit tenir.
4. **Apprendre les poids du Ban Radar** au lieu de les fixer : régression logistique
   (`class_weight="balanced"`, les cartes touchées sont ~1 % de l'univers), precision@k /
   recall@k, importance par permutation. Attention : avec ~11 positifs par liste, le risque
   de surapprentissage est maximal ; la validation doit rester temporelle.
5. **Pollution Genesys.** Le format Genesys (légalité par points) représente ~11 % du TCG
   depuis février 2026 et l'API le juge « légal » : le méta TCG actuel en est
   contaminé : **mesuré le 2026-11-16 à 27-44 % des decks TCG depuis juillet** (`tok-77-genesys.md`) ; le pipeline actuel les exclut. 388 decks sont marqués « non évaluables » dans `deck_legality`.
6. ~~**Script de validation du `prediction_log`**~~ *(fait : `scripts/validate_predictions.py`)*
7. **Clustering** (silhouette 0,171) : revoir les features, le scaling, le choix de k.

## 6. Mise en route

### Accès au code et aux données

- Code : `git clone https://github.com/T0koz/yugioh-meta-analyzer.git` (accès à confirmer
  avec Thomas).
- **La base `data/yugioh.db` n'est pas dans Git** (236 Mo). Trois voies :
  - **Demander la base à Thomas** (lien privé) : le plus rapide, et le seul moyen d'avoir
    exactement les mêmes chiffres que lui. Les données viennent de sources tierces
    (yugiohmeta, Yugipedia) : ne les republie pas publiquement.
  - **La reconstruire** : ~20 min de récupération + les notebooks dans l'ordre. Dépend de
    l'API yugiohmeta (qui peut ne plus répondre).
  - **`data/serving.db`** (9 Mo) suffit pour lancer l'API et le site, **pas** pour les notebooks.

### Installation

Python 3.13. Il n'y a pas de `requirements.txt` à la racine (seulement `backend/`) : la liste
est dans le README.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pandas numpy jupyter ipykernel networkx pyvis scikit-learn streamlit plotly \
            statsmodels youtube-transcript-api requests scipy
pip install -r backend/requirements.txt
```

### Reconstruire la base (ordre à respecter)

```bash
python scripts/fetch_cards.py && python scripts/init_db.py
python scripts/fetch_tournament_decks.py          # TCG, ~10 min, idempotent
python scripts/fetch_ocg_decks.py                 # OCG, ~10 min, idempotent
python scripts/fetch_banlist_history.py           # reconstruit la table à chaque run
python scripts/compute_deck_legality.py           # table deck_legality
# ou, pour tout rafraîchir d'un coup : scripts/refresh_decks.py puis scripts/refresh_all.py
python scripts/setup_impact_tables.py
python scripts/snapshot_prices.py
# puis les notebooks, dans l'ordre : 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09_banlist
#   → 10_archetypes → 10_boutique → 11 → 12   (01 et 09_ocg_tcg_correlation : lecture seule)
python scripts/build_ban_radar.py && python scripts/build_ban_radar.py --backtest
python scripts/build_card_impact.py               # dérive de ban_radar : à lancer après
python scripts/build_serving_db.py                # produit serving.db pour l'API
```

### Lancer le projet

```bash
cd backend  && ../.venv/bin/uvicorn app.main:app --reload --port 8000   # → :8000/api/v1
cd frontend && npm install && npm run dev                                # → :3000
cd frontend && npx tsc --noEmit                                          # vérif types
```

## 7. Règles du jeu et pièges

- **Tout changement de scoring du Ban Radar passe par**
  `python scripts/build_ban_radar.py --backtest`. Les `WEIGHTS` sont **dupliqués** entre
  `scripts/build_ban_radar.py` et `backend/app/routers/ban_radar.py` : les garder alignés.
  **Ne jamais baisser `BACKTEST_MIN_DECKS` (600)** : en dessous, le classement ne vaut rien
  (la liste OCG d'avril 2026, 416 decks, tombe exactement au niveau du hasard).
- **`deck_cards`** a un index unique `(deck_id, card_name, zone)` : purger les lignes d'un
  deck et agréger les cartes éclatées avant toute réinsertion, sinon `IntegrityError`.
- Les champs yugiohmeta (`author`, `deckType`…) sont tantôt une chaîne, tantôt un objet
  `{_id, name}` : toujours passer par `extract_name`, sinon le deck est avalé en silence.
- `banlist_history` : filtrer sur la colonne `format`, **jamais** sur `list_name LIKE '%TCG%'`.
- `ban_tcg IS NULL` signifie **légal** : ne pas tester `!= 'Forbidden'` seul.
- Jointure `cards` ↔ noms issus de `deck_cards` :
  `REPLACE(REPLACE(c.name,'<',''),'>','')` (les noms officiels portent `<P>`, `<C>`, `<Q>`).
- Nouvel endpoint → ajouter ses tables à `SERVED_TABLES` dans
  `scripts/build_serving_db.py`, puis `python scripts/build_serving_db.py --check`.
- Après chaque recalcul d'un modèle : `python scripts/log_predictions.py`, puis committer
  `data/prediction_log.jsonl` (le commit date la prédiction).
- **Ne jamais faire de split aléatoire** : tout est temporel (walk-forward). Surveiller les
  fuites (lags, `trend_ratio`, banlist) et ne fitter les scalers que sur le passé.
- Le détail des autres pièges (SQLite multi-thread, cache Next.js 16, design system…) est
  dans `context.md` et `CLAUDE.md`.

## 8. Façon de travailler

- Commits conventionnels : `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`.
- Thomas valide chaque commit et fait lui-même les `push`.
- Le suivi est dans [`BACKLOG.md`](../BACKLOG.md) (tickets `TOK-xx`, miroir de Linear).
  Après chaque fonctionnalité : mettre à jour `context.md` (pièges, résultats) et `BACKLOG.md`.
- *À définir avec Thomas :* branches + pull requests, ou autre ; accès Linear.

## 9. Pour une première semaine

1. Lire `context.md`, puis `docs/architecture.md` et `docs/data-models.md`.
2. Lancer le backend et le site, parcourir `/tier-list`, `/predictions`, `/ban`.
3. Rejouer `python scripts/build_ban_radar.py --backtest` et le notebook 05 : comprendre
   d'où sortent les chiffres du §4.
4. Choisir un chantier du §5 avec Thomas (le 1 est le plus structurant, le 2 le plus rapide).

## 10. Pour aller plus loin

[`context.md`](../context.md) · [`BACKLOG.md`](../BACKLOG.md) · [`architecture.md`](architecture.md) ·
[`data-models.md`](data-models.md) · [`development-guide.md`](development-guide.md) ·
[`../data/SOURCES.md`](../data/SOURCES.md)

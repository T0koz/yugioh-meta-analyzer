# Onboarding — Yu-Gi-Oh! Meta Analyzer

> Pour une data scientist qui rejoint le projet. Temps de lecture : ~15 min.
> **Pressée ? Lis le §8 « Travailler à deux » : c'est la page qui dit comment ne rien casser.**
> État des chiffres : 16 novembre 2026 (après nettoyage du backlog fiabilité). En cas de doute, `context.md` fait foi (c'est la
> mémoire du projet, mise à jour après chaque fonctionnalité).

## 1. En cinq lignes

- **Quoi :** un outil qui analyse la méta compétitive de Yu-Gi-Oh! (quels decks gagnent,
  quelles cartes montent) et essaie de **l'anticiper**.
- **Pour qui :** à terme, les boutiques de cartes (B2B, abonnement) qui doivent commander
  leur stock des mois avant que la demande n'explose ; et les joueurs (site public).
- **Thèse centrale :** le format japonais (OCG) précède le format occidental (TCG) de quelques mois
  (**recalculé le 2026-11-16 : r ≈ 0,53 à 4 mois, IC95 [0,43 ; 0,59], plateau de 2 à 6 mois** ; l'ancien r = 0,771,
  n = 43, n'est pas reproductible, voir §4). Un archétype fort en OCG a plus de chances d'être fort en TCG
  quelques mois plus tard : c'est la base du signal boutique.
- **Second produit :** le **Ban Radar**, un score 0-100 du risque qu'une carte soit bannie à
  la prochaine liste.
- **Où on en est :** pipeline de données, modèles, API et site (Next.js) existent et tournent
  sur de vraies données. Ce qui manque surtout, c'est de la **rigueur statistique** : voir §5.

Thomas (le fondateur) apprend la data science en parallèle (bootcamp). Il veut comprendre
*pourquoi* un choix est fait : documente et explique tes décisions de modélisation.

## 2. Les données

| Source | Contenu | Volume | Fragilité |
|---|---|---|---|
| **YGOPRODeck** (API v7) | Cartes, effets, archétypes, banlist courante, prix, popularité (`views_week`, figée au 13/06/2026) | 14 084 cartes (2026-11-18) | API publique, stable |
| **yugiohmeta.com** (API *non officielle*) | Decklists des top-coupes de tournois, TCG + OCG, depuis mai 2023 | 23 948 decks (11 618 TCG, 12 330 OCG), 1 026 945 lignes `deck_cards` (2026-11-18) | **Point de défaillance unique** : endpoint non documenté, sans clé, qui peut être coupé. Les données y sont collectées par un réseau communautaire (soumissions de joueurs/organisateurs), pas par un flux officiel |
| **Yugipedia** (scraping) | Historique des banlists TCG + OCG ; dates d'annonce (`banlist_announcements`, TOK-121) | 24 696 lignes ; 170 listes datées | Wiki : amende les listes passées rétroactivement, donc la table est reconstruite intégralement à chaque run |
| **YouTube** (transcripts) | Séquences de cartes citées dans des combo guides | quelques centaines de lignes | Transcription automatique qui déforme les noms japonais (« Kewl Tune » → « Cool Tune ») |

Stockage : **SQLite** (`data/yugioh.db`, ~275 Mo, 49 tables au 2026-11-18). Les tables dérivées
(scores, prédictions, graphe…) sont produites par les notebooks et scripts, pas par l'API.
Schéma complet : [`data-models.md`](data-models.md).

## 3. Architecture

```
 scripts/fetch_*.py ──► data/yugioh.db ──► notebooks 01→12 + scripts/build_*.py
 (YGOPRODeck,            (tables brutes)        │ (tables dérivées : meta_scores,
  yugiohmeta, Yugipedia)                        │  meta_predictions, boutique_*, ban_radar…)
                                                ▼
                        scripts/build_serving_db.py ──► data/serving.db (~12 Mo, 20 tables)
                                                                 │ lecture seule
                                                                 ▼
                                              backend/ (FastAPI) ──► frontend/ (Next.js 16)
```

- L'API ne calcule rien : elle sert des tables **précalculées**. Toute la science est en
  amont, dans `notebooks/` et `scripts/`.
- Un dashboard Streamlit historique (`app.py`) existe encore ; le site Next.js est la cible.
- Le job du lundi (`scripts/refresh_decks.py`) se termine par `scripts/check_freshness.py` (TOK-93) : une règle de
  fraîcheur par table servie, plus la santé de l'endpoint yugiohmeta `/top-decks`.
- **Peu de tests automatisés.** `python scripts/check.py` regroupe ce qui existe (§8) : test
  de fumée de l'API (tous les endpoints répondent 200, plus les tests de `backend/tests/`),
  `build_serving_db.py --check` (les tables servies existent), tsc + eslint + test du calcul de
  Wilson du front, les textes du site (`check_copy.py`), les tests du moteur de combos, le garde-fou
  des commandes, et le backtest du Ban Radar (§7), seul garde-fou *statistique*. Aucun test ne vérifie qu'un chiffre affiché est juste : c'est un chantier
  pour toi (voir [`collaboration/avis-stack.md`](collaboration/avis-stack.md)).

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
   `deck_legality` : 22 422 decks légaux, 611 illégaux et 915 non évaluables sur 23 948 au 2026-11-18). **L'étape 2 est faite (2026-11-16)** : consommateurs rebranchés,
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
   contaminé : **mesuré le 2026-11-16 à 27-44 % des decks TCG depuis juillet** (`tok-77-genesys.md`) ; le pipeline actuel les exclut. 915 decks sont marqués « non évaluables » dans `deck_legality` (2026-11-18).
6. ~~**Script de validation du `prediction_log`**~~ *(fait : `scripts/validate_predictions.py`)*
7. **Clustering** (silhouette 0,171) : revoir les features, le scaling, le choix de k.

## 6. Mise en route

### Accès au code et aux données

- **Code** : Thomas t'invite sur GitHub avec les droits d'**écriture** sur
  `T0koz/yugioh-meta-analyzer`. Le dépôt est **public** : tout ce que tu pousses est visible
  de tous, immédiatement.
  `git clone git@github.com:T0koz/yugioh-meta-analyzer.git` (ou en HTTPS).
- **La base `data/yugioh.db` n'est pas dans Git** (~270 Mo, données de tiers et pseudos de
  joueurs). Thomas te la partage en privé (dossier Google Drive à ton nom, ~50 Mo compressée,
  avec un `.json` qui dit de quand elle date). Installation et mise à jour :
  [`collaboration/transmission-base.md`](collaboration/transmission-base.md). **Ne la
  republie nulle part.**
- `data/serving.db` (~12 Mo) suffit pour lancer l'API et le site, **pas** pour les notebooks.
  Elle se régénère : `python scripts/build_serving_db.py`.
- En dernier recours, la base se reconstruit (~20 min + les notebooks), mais tu n'auras pas
  exactement les mêmes chiffres que Thomas, et ça dépend de l'API yugiohmeta.

### Installation

Python 3.13. `requirements.txt` (racine) fige les versions du venv de Thomas : mêmes
versions, mêmes chiffres.

```bash
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt                 # scripts, notebooks, API, tests
git config core.hooksPath .githooks             # optionnel : vérifications avant chaque push
```

### Reconstruire la base (ordre à respecter)

```bash
python scripts/fetch_cards.py && python scripts/init_db.py   # une fois : init_db.py écrase views_week
python scripts/refresh_decks.py   # cartes nouvelles, decks TCG + OCG (idempotents), banlists, légalité,
                                  # puis refresh_all.py (notebooks 02, 04, 05, 10 et scripts build_*),
                                  # serving.db et contrôle de fraîcheur ; `refresh_all.py --list` : l'ordre
# hors chaîne, à la main : notebooks 03 (graphe), 07 (texte), 08 (combos), 10_archetypes, 12 (clustering)
python scripts/build_ban_history.py && python scripts/build_serving_db.py   # onglet Historique du Ban Radar
python scripts/build_ban_radar.py --backtest      # à chaque retouche du scoring
```

### Lancer le projet

```bash
cd backend  && ../.venv/bin/uvicorn app.main:app --reload --port 8000   # → :8000/api/v1
cd frontend && npm install && npm run dev                                # → :3000
python scripts/check.py --all                                            # tout doit être vert
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

## 8. Travailler à deux

Deux personnes poussent **directement sur `main`, sans revue**, sur un dépôt **public**. Ce
qui protège le projet, ce sont les quelques règles ci-dessous. Les mêmes règles sont écrites
pour les agents IA dans [`CLAUDE.md`](../CLAUDE.md) : si tu utilises Claude Code, il les
applique ; avec un autre agent, pointe-le vers ce fichier.

### Avant chaque push : une commande

```bash
git pull --rebase                # l'autre a peut-être poussé entre-temps
python scripts/check.py          # vérifie ce qui a changé depuis origin/main
git push
```

`scripts/check.py` choisit seul ce qu'il lance selon les fichiers modifiés (~3 s en général,
~30 s avec le front et le backtest) :

| Vérification | Quand | Bloque |
|---|---|---|
| Fichiers interdits (`.env`, `*.db`, clés, `HANDOFF.md`) et identifiants dans le code | toujours | oui |
| `WEIGHTS` identiques dans `build_ban_radar.py` et l'API | toujours | oui |
| `tsc --noEmit` + `eslint` | `frontend/` modifié | oui |
| `build_serving_db.py --check` + test de fumée sur `yugioh.db` **et** `serving.db` | `backend/` ou `scripts/` modifié | oui |
| Test du calcul de Wilson du front (`npm run test:stats`) | `frontend/` modifié | oui |
| Garde-fou des commandes (`.claude/hooks/test_garde_fou.py`) | toujours (0,2 s) | oui |
| Textes du site (`check_copy.py --strict`) | `frontend/src/` modifié, ou `--all` | oui |
| Tests du moteur de combos (`moteur_combos/tests`) | `moteur_combos/` ou fichiers du jeu de tests modifiés | oui |
| Tests visuels (51 captures) | seulement avec `--visuel` | oui |
| Backtest du Ban Radar | scoring modifié | non : il affiche les rangs médians, **à comparer à `context.md`** |

Une étape « ignorée » (base ou `node_modules` absents) n'est **pas** réussie : lance-la, ou
dis pourquoi tu ne l'as pas fait dans le message de commit.

Trois filets supplémentaires, sans action de ta part :
- le **hook pre-push** (si tu l'as activé : `git config core.hooksPath .githooks`) lance
  `check.py` à chaque `git push` ; `git push --no-verify` le contourne, en connaissance de cause ;
- la **CI GitHub** (`.github/workflows/verifications.yml`, gratuite) relance la partie sans base
  (secrets, `WEIGHTS`, tsc, eslint) après chaque push et prévient par e-mail en cas d'échec ;
- la **protection de push de GitHub** refuse les clés des grands fournisseurs (AWS, GitHub…).

### Les données

- **Une seule base de référence** : celle de Thomas, mise à jour chaque lundi à 8 h 30 par
  `scripts/refresh_decks.py` (decks, banlists, légalité, puis tout `refresh_all.py`).
- **Ta copie est un bac à sable** : recalcule, casse, expérimente. Ce qui devient officiel
  passe par du **code commité** (un script dans `scripts/`), que le job du lundi rejoue sur la
  base de référence. On ne s'échange jamais de tables recalculées.
- **Un calcul qui écrit en base va dans `scripts/`**, pas dans un notebook : un `.ipynb` est du
  JSON, on ne peut ni le relire ni le fusionner à deux. Les notebooks servent à explorer et à
  expliquer.
- **`data/prediction_log.jsonl`** (la preuve datée des prédictions) n'est commité **que par
  Thomas**, depuis la base de référence. Ne lance pas `log_predictions.py` sur ta copie.
- **Identifiants** (base hébergée un jour, API…) : dans un fichier `.env`, exclu par
  `.gitignore`. S'il t'arrive d'en pousser un : **le révoquer** immédiatement, l'effacer du code
  ne suffit pas (il reste dans l'historique public).

### Conventions

- Commits conventionnels en français : `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`,
  suivis du ticket quand il y en a un : `fix(TOK-95): …`.
- Petits commits, poussés souvent : moins de conflits.
- Après chaque fonctionnalité : `context.md` (pièges, résultats chiffrés) et `BACKLOG.md`
  (statut du ticket). Ce sont les deux fichiers les plus édités : `git pull --rebase` avant
  d'y toucher, et ajoute ta section plutôt que de réécrire celle de l'autre.
- Les tickets `TOK-xx` vivent dans Linear (équipe Tokoz, Thomas t'y invite) ; `BACKLOG.md` en
  est le miroir. Avec Claude Code, connecte Linear dans les réglages de l'app pour qu'il lise
  les tickets.
- Changement du **Ban Radar** : backtest obligatoire (§7), et l'agent `data-scientist-ygo` si tu
  utilises Claude Code. Script qui **écrit en base** ou nouvel **endpoint** : l'agent
  `gardien-donnees`.

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

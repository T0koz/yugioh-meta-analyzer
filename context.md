# Yugioh Meta Analyzer — Context

## Projet
Outil d'analyse et de prédiction de la méta Yu-Gi-Oh! via IA.
Potentiel B2B : vente aux boutiques (150€/mois) pour anticiper les achats de stock avec 4 mois d'avance sur la méta TCG.
Réplicable sur d'autres TCG (Pokémon, Magic...) une fois le modèle Yu-Gi-Oh! validé.

## Profil
Thomas Cozian — ex consultant e-commerce ZeTrace, ex PO refonte B2B headless.
Formation Le Wagon Data Science & IA débutant le 12 octobre 2026.
Objectif : produit V2 fini avant Le Wagon.

---

## Stack
- Python 3.13 (Homebrew), VS Code, Git, GitHub
- Venv : `.venv` à la racine du projet (partagé par les notebooks ET le backend FastAPI)
- Libs : requests, pandas, numpy, jupyter, ipykernel, networkx, pyvis, playwright, matplotlib, scipy, python-dateutil, fastapi, uvicorn
- SQLite pour le stockage local
- Dashboard Streamlit (historique, toujours valide) : `cd ~/code/yugioh-meta-analyzer && bash run.sh`
- Backend FastAPI (nouveau, TOK-31) : `backend/`, voir Phase 5
- Frontend Next.js (TOK-32) : `frontend/`, voir Phase 5

## Environnement de travail
- **Claude Code** : installé et actif, tourne dans l'app Claude Desktop (Cowork) — pas de terminal CLI classique, connecteurs gérés via les réglages de l'app
- **Linear** : MCP connecté (reco : "Linear" dans réglages > Connectors si déconnecté), tickets TOK-5 à TOK-67 créés et à jour
- **BMad** : installé via `claude plugin install bmad@bmad-method`, docs dans `docs/`
- **Brainstorming site public (2026-08-05)** : `_bmad-output/brainstorming/brainstorming-session-2026-08-05-1.md` (28 idées → TOK-46 à 67, cf. BACKLOG.md)

---

## État du projet — Phases 1 à 4 : ✅ TOUTES TERMINÉES

### Ce qui existe en DB (yugioh.db)
| Table | Lignes | Source |
|-------|--------|--------|
| cards | 13 797 | YGOPRODeck API |
| tournament_decks | 19 888 | yugiohmeta.com (TCG + OCG) |
| deck_cards | 852 405 | yugiohmeta.com |
| meta_scores | 462 | notebook 04 |
| meta_tier_list | 47 | notebook (tier list yugiohmeta) |
| text_synergies | 55 072 | notebook 07 (NLP sur desc) |
| card_mechanic_tags | 13 797 | notebook 07 |
| early_card_signals | 467 | notebook 11 (views_week signal) |
| banlist_history | 11 890 | notebook 09 |
| banlist_features | 3 660 | notebook 09 |
| archetypes_official | 640 | notebook 10 (endpoint /archetypes.php) |
| archetype_mapping | 122 | notebook 10 |
| card_price_history | 41 395 | notebook (snapshot quotidien) |
| card_cooccurrence | 5 489 | notebook 02 |
| card_cooccurrence_90d | 8 797 | notebook 02 (fenêtre 90j) |
| card_cooccurrence_extra | 5 583 | notebook 02 (extra deck) |
| card_cooccurrence_elite | 4 796 | notebook 02 (YCS/Nationals) |
| card_cooccurrence_quarterly | 9 851 | notebook 02 (trimestriel) |
| card_cooccurrence_side | 739 | notebook 02 |
| card_graph_metrics | 663 | notebook 03 (betweenness) |
| graph_communities | 63 | notebook 03 |
| deck_style_clusters | 3 601 | notebook 12 (K-Means k=4) |
| meta_predictions | 45 | notebook 05 (AR(1)) |
| boutique_alerts | 69 | notebook 10 |
| boutique_card_alerts | 167 | notebook 10 |
| boutique_buy_signals | 137 | notebook 10 |
| combo_edges_global | 117 | notebook 08 (NLP combos) |
| meta_scores_regional | 678 | notebook (OCG vs TCG) |

### Notebooks existants
- `01_exploration.ipynb` — exploration cartes
- `02_cooccurrence.ipynb` — co-occurrence pondérée (toutes variantes)
- `03_graph.ipynb` — graphe NetworkX + Pyvis + betweenness
- `04_meta_score.ipynb` — score méta + trends
- `05_meta_prediction.ipynb` — modèle AR(1) par archetype
- `06_card_ban_impact.ipynb` — bridge score + impact ban
- `07_nlp_text_synergies.ipynb` — NLP sur texte des effets (desc)
- `08_nlp_combos.ipynb` — NLP combos YouTube (blacklist appliquée ✅)
- `09_banlist_history.ipynb` — historique banlist complet
- `09_ocg_tcg_correlation.ipynb` — corrélation OCG→TCG (r=0.771, lag 4 mois)
- `10_archetypes_official.ipynb` — matching archetypes officiels Konami
- `10_boutique_alert_score.ipynb` — score alerte boutiques (Kewl Tune 100/100)
- `11_early_card_signal.ipynb` — signal précoce views_week
- `12_deck_clustering.ipynb` — clustering style de jeu K-Means

### Signal boutiques ✅
- **Corrélation OCG→TCG : r=0.771, p<0.0001, lag 4 mois**
- Formule : `alert_score = meta_score_ocg × log(1 + avg_views_week_cartes_core)`
- Filtres : staples >20% decks TCG exclues + cartes bannies TCG exclues
- **Kewl Tune : score 100/100** — Fydraulis Harmonia (19 844 views/week) signal d'achat fort
- Entrée TCG estimée : octobre 2026

### NLP Combos (notebook 08) — état actuel
- Blacklist appliquée : 49 termes exclus (NEXT, Fine, Return, Prohibition, Contact, Surface, Storm...)
- Problème identifié : transcription YouTube déforme les noms OCG/japonais (ex: "Kewl Tune" → "Cool Tune")
- Fonctionne bien sur archetypes aux noms anglais classiques (Branded, Snake-Eye...)
- **P4-X en cours** : test sur vidéo Branded 101 (`DSYkfk5u_uA`) — pas encore lancé

---

## Phase 5 — Front-end + API : 🏗️ En cours

### ✅ Backend FastAPI — Livré (TOK-31, 2026-08-05)

**Stack :** FastAPI + sqlite3 stdlib (pas d'ORM), lecture directe de `data/yugioh.db`
**Dossier :** `backend/app/`
**Dev :** `.venv/bin/uvicorn app.main:app --reload --port 8000` (lancé depuis `backend/`, config dans `.claude/launch.json` nom `"backend"`) → `http://localhost:8000/api/v1`

**Structure :**
```
backend/app/
├── main.py            # FastAPI app + CORS (ouvert *) + include_routers, prefix /api/v1
├── db.py              # get_db() : connexion sqlite3.Row vers data/yugioh.db
├── schemas.py         # Pydantic models miroir de frontend/src/types/index.ts
├── labels.py          # Mappings DB → front : tier ("field"→"Rogue"), trend_label (emoji FR → Rising/Stable/Declining), pred_direction (↑→↓ → idem)
└── routers/
    ├── meta.py        # GET /meta/tier-list, /meta/evolution, /meta/predictions
    ├── boutique.py    # GET /boutique/signals, /early-signals
    ├── graph.py       # GET /graph/synergies (nodes card_graph_metrics + edges card_cooccurrence)
    └── cards.py       # GET /cards/{name} (fuzzy match), POST /simulate-ban
```

**Points d'attention (à connaître avant de retoucher) :**
- `meta_score` (formule `sqrt(share × placement_score_norm)`) ne dépasse jamais ~0.15 en pratique — toute UI qui l'affiche en barre doit se recalibrer en relatif au max du dataset, pas en absolu sur [0,1] (corrigé sur tier-list et predictions)
- `boutique_buy_signals` a une ligne par **(archétype, carte)** : une staple générique (ex: Super Polymerization) apparaît sous plusieurs archétypes → toute clé React doit combiner les deux, pas juste `card_name`
- `/simulate-ban` : `bridge_score` vient de `card_impact` (35 cartes seulement, sinon 0) ; `fragmentation` est une approximation (betweenness normalisée sur le max du dataset, pas de métrique de fragmentation précalculée) ; `community_id = -1` si la carte n'a pas de `top_archetype` dans `card_impact`
- Pas de table card→communauté : `/graph/synergies` groupe par `cards.archetype`, pas par `graph_communities.community_id` (qui n'est qu'un résumé par communauté, 63 lignes)
- **⚠ Bug corrigé (2026-08-05)** : `sqlite3.ProgrammingError` intermittente sur tous les endpoints — FastAPI exécute les routes `def` (sync) dans un threadpool, `sqlite3.connect()` sans `check_same_thread=False` casse dès que la requête tombe sur un thread différent de celui qui a ouvert la connexion. Fix dans `db.py`. **Si un nouvel endpoint sync est ajouté et manipule `db` directement sans passer par `get_db()`, il aura le même problème.**
- `GET /cards/search` est enregistré **avant** `GET /cards/{name}` dans `cards.py` — sinon FastAPI matche `/cards/search` comme `{name}="search"`. Respecter cet ordre pour toute nouvelle route `/cards/...`.

### ✅ Frontend Next.js — Branché sur l'API réelle (2026-08-05)

**Stack :** Next.js 16.2.12 + TypeScript + Tailwind CSS + shadcn/ui + recharts + vis-network (^10)
**Dossier :** `frontend/`
**Dev :** lancé via le tool preview (config `"frontend"` dans `.claude/launch.json`, `autoPort: true`) → `http://localhost:3000`
**⚠ `frontend/AGENTS.md`** : Next 16 a un nouveau modèle de cache (`'use cache'` + Cache Components, opt-in via `cacheComponents: true` dans `next.config.ts` — **pas activé ici**, donc l'ancien `fetch(url, { next: { revalidate } })` utilisé dans `lib/api.ts` reste valide). Vérifier `node_modules/next/dist/docs/` si un changement touche au caching/fetch.
**⚠ Cache disque `.next/cache`** : persiste entre redémarrages du serveur dev (contrairement au cache mémoire). Si une donnée fraîchement ajoutée côté API n'apparaît pas côté front malgré un redémarrage du serveur, faire `rm -rf frontend/.next` avant de conclure à un bug.

**Structure :**
```
frontend/src/
├── app/
│   ├── layout.tsx          # Layout global + navigation top bar
│   ├── page.tsx            # Redirect → /tier-list
│   ├── tier-list/          # Server component + ArchetypeCard.tsx (grille de cartes, PAS un tableau)
│   ├── evolution/          # page.tsx (server, fetch) + EvolutionChart.tsx (client, recharts, connectNulls)
│   ├── predictions/        # Server component, api.predictions(), barre recalibrée au max
│   ├── boutique/           # Server component, api.boutiqueSignals(), key=archetype+card_name, CardChip
│   ├── early-signals/      # Server component, api.earlySignals(), CardChip
│   ├── graph/              # page.tsx (server, api.graphSynergies) + GraphView.tsx (client, vis-network, filtre par archétype)
│   └── ban-simulator/      # Client component (Suspense + useSearchParams pour ?card=...), api.simulateBan(), photo de la carte affichée
├── components/
│   ├── nav.tsx             # Navigation top bar (flex-wrap : recherche passe à la ligne si l'espace manque)
│   ├── smart-search.tsx    # Autocomplete debounced → GET /cards/search, clic → /ban-simulator?card=...
│   ├── card-chip.tsx       # Chip carte réutilisable, déclenche le hover-preview-context (pas de tooltip flottant local)
│   ├── hover-preview-context.tsx  # Provider React Context (preview: {name, imageUrl, subtitle}) — un seul par page
│   ├── hover-preview-panel.tsx    # Panneau fixe à gauche (`fixed left-6 top-32`, visible dès xl/1280px), affiche l'image en grand au survol
│   └── ui/                 # shadcn/ui: table, badge, card, input, select, info-tooltip...
├── lib/
│   └── api.ts              # Client fetch → NEXT_PUBLIC_API_URL (défaut http://localhost:8000/api/v1)
└── types/index.ts          # TypeScript types (TierEntry, BoutiqueSignal, GraphResponse, SearchResult, etc.)
```

`lib/mock.ts` supprimé (plus aucune page ne l'utilise).

**Tier List (2026-08-05, redesign) :** passée d'un tableau HTML par tier à une grille de cartes (`ArchetypeCard.tsx`), une seule liste continue triée par rang (pas de sections par tier). Chaque carte : 25% vignette (image la plus vue de l'archétype) / 75% infos (nom, meta score, share, trend), badge tier incrusté sur la vignette. **Pas de dégradé de saturation par tier** — testé puis retiré à la demande (le "Rogue" est juste une étiquette de classement yugiohmeta.com pour "hors T0-T3", pas une carte moins bonne visuellement). Le survol déclenche toujours le panneau latéral (`HoverPreviewPanel`) commun aux pages boutique/early-signals.

`HoverPreviewProvider`/`HoverPreviewPanel` remplacent l'ancien tooltip flottant par carte (`bottom-full` dans un conteneur `overflow-hidden` → invisible, clippé). Toute nouvelle page qui utilise `CardChip` doit être enveloppée dans un `<HoverPreviewProvider>` avec un `<HoverPreviewPanel />`, sinon `useHoverPreview()` lève une erreur.

**`InfoTooltip`** (`components/ui/info-tooltip.tsx`) : bulle ⓘ ouverte vers le **bas** (`top-full`, pas `bottom-full`) — sinon coupée par un ancêtre `overflow-hidden` (ex: conteneur de tableau). Ne pas revenir à `bottom-full` sans vérifier qu'aucun ancêtre ne clippe.

**Ban Radar (TOK-53)** — `scripts/build_ban_radar.py` → table `ban_radar` →
`GET /api/v1/ban-radar` → page `/ban-radar`. Score de risque 0-100 sur 6 critères
pondérés, avec décomposition par critère renvoyée au front (barre colorée).

Deux pièges à ne pas refaire si le scoring est retouché :
- **L'omniprésence seule ne prédit rien.** Konami ne frappe pas les staples les
  plus jouées mais les pièces de moteur des decks qui gagnent. La v1, bâtie sur
  ubiquité + nombre d'archétypes, plaçait les cartes réellement touchées au rang
  médian 302/681 — le hasard. Le nombre d'archétypes qui jouent une carte ne
  discrimine pas du tout (médiane 4 chez les touchées comme chez les autres).
- **Le critère décisif est le nombre moyen d'exemplaires joués** (2.50 chez les
  touchées vs 1.10). Le retirer fait tomber le rappel top-10% de 5/10 à 1/10.

Toute modification du scoring doit être repassée au backtest :
`python scripts/build_ban_radar.py --backtest`. Les listes ne sont plus codées en
dur, elles sont dérivées de `banlist_history` — une carte compte comme touchée
quand son statut gagne en sévérité par rapport à la liste précédente du même
format. Toute nouvelle banlist scrapée devient donc automatiquement un point de
mesure, sans toucher au code.

Les poids sont dupliqués entre le script et `backend/app/routers/ban_radar.py`
(le script calcule, l'API réapplique pour la décomposition) — garder les deux alignés.

**Résultats du backtest (2026-08-14)** — seules les fenêtres d'au moins 600 decks
et 5 cartes touchées sont retenues, les autres sont listées comme écartées :

| Liste | Univers | Rang médian | Hasard | Top-25% |
|---|---|---|---|---|
| TCG 2026-05-18 | 923 cartes / 1 264 decks | **127** | 462 | 8/11 |
| OCG 2026-07-01 | 1 089 cartes / 1 713 decks | **31** | 544 | 7/11 |
| OCG 2026-04-01 *(écartée)* | 556 cartes / 416 decks | 285 | 278 | 2/7 |

Deux enseignements :
- **Le modèle transfère à l'OCG**, format sur lequel il n'a jamais été calibré,
  et y réussit mieux qu'en TCG. C'est une validation hors distribution, plus
  exigeante qu'un simple rejeu sur le format d'origine.
- **En dessous d'environ 600 decks dans la fenêtre, le classement ne vaut rien.**
  La liste OCG d'avril 2026 (416 decks) tombe exactement au niveau du hasard.
  C'est ce qui justifie `BACKTEST_MIN_DECKS`, et ce seuil ne doit pas être baissé
  pour faire entrer des listes supplémentaires : on ne récolterait que du bruit.

Le classement OCG **ne s'écrit pas en base** : `ban_radar` est servie telle quelle
par l'API, qui n'a pas de notion de format. `--format ocg` refuse d'écrire et
renvoie vers `--dry-run`.

La page propose un filtre **Tout / Pièces d'archétype / Staples génériques**
(`?kind=archetype|generic`, filtré en SQL et non côté client, sinon le « top 50 »
porterait sur un sous-ensemble déjà tronqué). La bascule repose sur
`top_archetype IS NULL`, renseigné par le script quand moins de 50% des decks
jouant la carte appartiennent à son archétype porteur.

### ⚠ Pièges du pipeline de fetch (corrigés le 2026-08-14)

`fetch_tournament_decks.py` / `fetch_ocg_decks.py` avaient trois bugs silencieux.
À garder en tête pour tout nouveau script d'ingestion :
- `deck_cards` n'a **aucune contrainte d'unicité**. Tout script qui y insère doit
  purger les lignes du deck avant réinsertion, sinon chaque relance empile.
- Les champs `author`, `deckType`, `tournamentType`, `tournamentLocation` de
  l'API yugiohmeta sont **tantôt une chaîne, tantôt un objet** `{_id, name}` :
  passer systématiquement par `extract_name`, sinon sqlite3 rejette le dict et
  le `except` avale le deck entier sans bruit.
- L'API éclate parfois une carte en deux entrées dans la même zone (amount 1
  puis 2 = 3 exemplaires) : agréger avant insertion.

### `banlist_history` — scraping scripté, TCG + OCG

`scripts/fetch_banlist_history.py` remplace le notebook 09 pour cette table
(le notebook reste la source de `banlist_features`). Il reconstruit la table
intégralement à chaque exécution : Yugipedia est la source de vérité et amende
les listes passées rétroactivement.

Deux changements par rapport au notebook :
- **Les listes OCG sont scrapées** (catégorie `OCG Forbidden & Limited Lists`,
  87 listes). C'est ce qui a débloqué le second point de backtest du Ban Radar.
  La catégorie contient aussi des sous-catégories régionales (coréen, chinois
  simplifié…) qu'il faut filtrer — ce ne sont pas des listes.
- **Une colonne `format`** ('TCG' / 'OCG'). Le filtre historique
  `list_name LIKE '%TCG%'` laissait de côté 33 listes TCG antérieures à 2021 que
  Yugipedia nomme sans suffixe (« September 2020 Lists »). Ne plus filtrer sur
  le nom de la page.

État au 2026-08-14 : 23 995 lignes, TCG jusqu'au 2026-05-18, OCG jusqu'au
2026-07-01.

**Sur la banlist TCG en vigueur :** YGOPRODeck (`?banlist=tcg`) renvoie 5 cartes
de moins que la liste du 18 mai — Ext Ryzeal, Maliss P Dormouse, Maliss P White
Rabbit, Maliss Q White Binder et Number 89: Diablosis the Mind Hacker, toutes
assouplies. Mais **Yugipedia n'a aucune liste TCG après le 18 mai**. C'est donc
plus probablement une dérive de la donnée YGOPRODeck qu'une nouvelle banlist.
Dans les deux cas : aucune nouvelle restriction TCG, donc aucun point de
backtest supplémentaire de ce côté.

### 🗄 Base de service (déploiement, TOK-35)

`scripts/build_serving_db.py` → `data/serving.db`, **9,4 Mo au lieu de 236 Mo**.

L'API n'interroge que 12 des 36 tables : tout ce qu'elle sert est précalculé.
`deck_cards` et ses index pèsent 74% de `yugioh.db` et ne sont jamais lus en
ligne — ils ne servent qu'aux notebooks et à `build_ban_radar.py`. La base de
service est donc transportable avec le déploiement : **pas de volume persistant
à provisionner ni à sauvegarder**, le backend reste en lecture seule pure.

- Le backend lit `YGO_DB_PATH` si la variable est définie, sinon `data/yugioh.db`.
  En production : `YGO_DB_PATH=/app/data/serving.db`.
- Le script embarque une **garde anti-dérive** : il scanne les `FROM`/`JOIN` des
  routeurs et échoue si l'un d'eux référence une table absente de `SERVED_TABLES`.
  Sans ça, un nouvel endpoint partirait en production avec une table manquante et
  ne casserait qu'à la première requête. `--check` la lance sans rien écrire.
- `data/serving.db` n'est pas trackée (`data/*.db`) : elle se régénère.

Conséquence à évaluer avant de provisionner quoi que ce soit : à 9 Mo en lecture
seule, **Railway n'est peut-être plus nécessaire** — l'API pourrait tourner en
fonctions serverless à côté du front, base embarquée. Ça supprimerait la moitié
de TOK-35.

### 🔜 À faire

- **TOK-35** : déploiement — base de service prête, reste à trancher l'hébergement (Vercel seul vs Vercel + Railway) et à fournir les credentials
- **TOK-52** : Mode Joueur / Mode Boutique (toggle UX) — nécessite de trancher ce que chaque mode change concrètement (pas fait en autonome pour cette raison)
- **TOK-55** : Ban Predictor vs History — deux points de mesure concluants disponibles (TCG mai 2026, OCG juillet 2026), la page publique reste à faire
- **Phase B/C (TOK-54 à 67)** : Deck Builder, Referral boutique, API freemium — voir BACKLOG.md

### ✅ Fait en autonome le 2026-08-05 (pendant absence de Thomas)
TOK-33 (graphe vis-network interactif), TOK-48 (smart search), TOK-49 (card chips), TOK-50 (archetype thumbnails), TOK-51 (tooltips), + fix thread-safety SQLite critique. Détail dans les descriptions Linear de chaque ticket.

### ✅ Fait avec Thomas le 2026-08-05 (session suivante)
Fix positionnement `InfoTooltip` (clippée par `overflow-hidden`). Redesign complet de `/tier-list` : table → grille de cartes (wireframes validés via le tool visualize avant implémentation), panneau de survol étendu à `/tier-list` en plus de boutique/early-signals, photo ajoutée sur `/ban-simulator`. Tentative de dégradé de saturation par tier testée puis retirée sur demande.

---

## Structure du projet
```
yugioh-meta-analyzer/
├── app.py                    # Dashboard Streamlit (6 pages, toujours valide)
├── run.sh                    # bash run.sh → lance Streamlit
├── BACKLOG.md                # Backlog (synchronisé avec Linear TOK-5 à 67)
├── context.md                # Ce fichier
├── backend/                  # API FastAPI (TOK-31) — voir Phase 5
│   ├── requirements.txt
│   └── app/
├── frontend/                 # Next.js (TOK-32/33/34) — voir Phase 5
│   └── src/
├── scripts/
│   ├── fetch_cards.py
│   ├── init_db.py
│   ├── fetch_tournament_decks.py
│   ├── fetch_ocg_decks.py
│   └── setup_impact_tables.py
├── notebooks/ (14 notebooks)
└── data/
    ├── yugioh.db             # Base SQLite principale (non trackée Git)
    └── raw/cards.json
```

---

## APIs

### YGOPRODeck v7
- `https://db.ygoprodeck.com/api/v7/cardinfo.php` — `misc=yes&format=tcg`
- Endpoints : `/archetypes.php`, `/cardsets.php`

### yugiohmeta.com (non officielle)
- `https://www.yugiohmeta.com/api/v1/top-decks`
- TCG : `ocg[$ne]=true` / OCG : `ocg=true`
- Pas de clé requise

---

*Dernière mise à jour : 2026-08-14*

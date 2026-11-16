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
│   ├── page.tsx            # Home en bento (5 tuiles branchées sur l'API), plus de redirection
│   ├── tier-list/          # Server component + TierList.tsx (filtres) + ArchetypeRow.tsx (liste dense)
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
│   ├── ds/                 # Design system Ember : em.tsx (<Em>), page.tsx (Page, PageHero, StatBand, Toolbar, pillClass, Callout, Explainer, Meter), tags.tsx (TierTag, TrendLabel, BanStatus, Tag)
│   └── ui/                 # shadcn/ui restylés sur les tokens : table, input, info-tooltip (badge, button, card, select inutilisés)
├── lib/
│   └── api.ts              # Client fetch → NEXT_PUBLIC_API_URL (défaut http://localhost:8000/api/v1)
└── types/index.ts          # TypeScript types (TierEntry, BoutiqueSignal, GraphResponse, SearchResult, etc.)
```

`lib/mock.ts` supprimé (plus aucune page ne l'utilise).

**Design system « Ember » (2026-10-31) :** source de vérité visuelle dans `docs/design-system.md` (maquettes : `docs/design-reference.html`). Toutes les pages l'appliquent : thème sombre uniquement, un seul accent `--signal`, tokens en classes Tailwind (`bg-ink-3`, `text-signal`, `border-line`…), **aucune couleur Tailwind brute ni hex dans `src/`**. Tier list en liste dense (l'ancienne grille de cartes est abandonnée), home en bento, Ban Radar avec score en grand et barre empilée des critères.

Pièges rencontrés pendant la refonte :
- **Espace perdu dans un texte JSX multi-ligne qui contient une entité** (`&apos;`, `&amp;`…) : la compilation supprime l'espace initial du texte qui suit une balise ou une expression (« génériques</strong> trustent » rendu « génériquestrustent »). Écrire l'apostrophe typographique `’` plutôt que `&apos;`, ou construire la phrase dans une chaîne JS.
- **Canvas (vis-network) et `var()`** : le canvas ne résout pas les variables CSS. `GraphView` lit les tokens au runtime (`getComputedStyle`), police comprise. Les SVG (home, recharts) acceptent `var(--…)` directement.
- **Chiffres de vitrine** (19 888 decklists, 13 797 cartes, r = 0,771, 4 mois, 63 communautés) : aucun endpoint ne les expose, ils sont dans `src/lib/site-facts.ts`, à mettre à jour à la main quand la base est rafraîchie.
- `prefers-reduced-motion` coupe transitions et animations, mais **pas** `transform` (il casserait les centrages en `-translate-y-1/2`) : les déplacements au survol s'écrivent en `motion-safe:`.
- Formats français centralisés dans `src/lib/format.ts` (`fmtNum`, `fmtPct`, `fmtDate`…) : ne plus utiliser `toFixed` pour l'affichage.
- `--faint` (rangs, placeholders) est à 3,2:1 de contraste sur `--ink` : à réserver au décoratif, jamais à une information seule.

`HoverPreviewProvider`/`HoverPreviewPanel` remplacent l'ancien tooltip flottant par carte (`bottom-full` dans un conteneur `overflow-hidden` → invisible, clippé). Toute nouvelle page qui utilise `CardChip` doit être enveloppée dans un `<HoverPreviewProvider>` avec un `<HoverPreviewPanel />`, sinon `useHoverPreview()` lève une erreur.

**`InfoTooltip`** (`components/ui/info-tooltip.tsx`) : bulle ⓘ ouverte vers le **bas** (`top-full`, pas `bottom-full`) — sinon coupée par un ancêtre `overflow-hidden` (ex: conteneur de tableau). Ne pas revenir à `bottom-full` sans vérifier qu'aucun ancêtre ne clippe.

**`/graph` (vis-network 10) — pièges corrigés le 2026-10-31 :**
- **Pas de `fit()` animé.** Deux `fit` animés enchaînés sans frame entre eux (celui de fin de stabilisation + le nôtre) laissent une `viewFunction` orpheline branchée sur `initRedraw` : la caméra revient au cadrage précédent à chaque redessin (le filtre recentrait avec un changement de retard). Les `fit` sont donc instantanés.
- `fit()` plafonne le zoom à 1 par défaut : le recentrage sur un archétype passe `maxZoomLevel: 4`, sinon la clique reste minuscule.
- `blurNode` n'est pas émis quand la souris quitte le canvas depuis un nœud : le conteneur vide le panneau de survol sur `onMouseLeave`.
- Jointure `cards` ↔ noms issus de `deck_cards` : `cards.name` porte `<P>`/`<C>`/`<Q>` (« Maliss <P> March Hare »), pas `deck_cards` → joindre sur `REPLACE(REPLACE(c.name,'<',''),'>','')` (graph, ban_radar, card_impact). Les ~19 nœuds encore sans image sont des cartes récentes absentes de `cards` (relancer `fetch_cards.py`).

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
- `deck_cards` n'avait **aucune contrainte d'unicité** : chaque relance empilait.
  `fetch_tournament_decks.py` crée désormais l'index unique
  `idx_deck_cards_unique (deck_id, card_name, zone)`. Tout script qui y insère
  doit quand même purger les lignes du deck avant réinsertion, sinon `IntegrityError`.
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

### 📒 Journal des prédictions (2026-11-01)

`scripts/log_predictions.py` archive l'état courant de `meta_predictions`, `boutique_alerts`,
`boutique_buy_signals`, `early_card_signals` et `ban_radar` dans la table `prediction_log`
(append-only : triggers SQLite contre UPDATE/DELETE) **et** dans `data/prediction_log.jsonl`
(versionné par git). Ces cinq tables sont écrasées à chaque recalcul : sans journal, on ne peut
pas prouver « annoncé le X, réalisé le Y ».

- **À lancer après chaque recalcul d'une source** (notebook 05, notebook 10, notebook 11,
  `build_ban_radar.py`), puis **committer `data/prediction_log.jsonl`** : le commit (et le push) date
  la prédiction par un tiers. `--dry-run` simule, `--status` résume.
- Idempotent (clé : kind, sujet, date de calcul, version du modèle). Si la table est vide, elle
  est reconstruite depuis le fichier jsonl.
- **`provenance`** : `live` si journalisé au plus 1 jour après le calcul, `backfill` sinon. Le premier
  lot (2 008 lignes, calculées entre juin et août 2026) est `backfill` : il ne prouve rien d'indépendant.
  Seules les lignes `live` commitées sont une preuve.
- Bump `META_MODEL` / `BOUTIQUE_MODEL` / `EARLY_MODEL` dans le script quand un modèle change ; la
  version du Ban Radar est l'empreinte de `WEIGHTS` lue dans `build_ban_radar.py`.
- Le script ouvre la base avec `timeout=60` : un processus qui garde `yugioh.db` ouverte (backend,
  notebook, agent) bloque l'écriture (`database is locked`).
- La table n'est pas dans `SERVED_TABLES` (aucun endpoint ne la lit encore) : l'ajouter le jour où
  la page TOK-55 « Ban Predictor vs History » la servira.
- Il n'existe pas encore de script de **validation** (comparer chaque prédiction à la réalité
  après `target_date`) : prochaine étape.

### ⚖️ Légalité des decks à la date du tournoi (2026-11-01)

**Problème :** `tournament_decks.illegal` (drapeau de l'API yugiohmeta) est évalué contre une banlist
**postérieure** au tournoi. Avant le 2 février 2026 (TCG) et avril 2026 (OCG), 90 à 100 % des decks
sont jugés illégaux ; le filtre `illegal = 0` des notebooks 02, 03, 04, 09, 10, 12 et de
`build_ban_radar.py` jette donc l'essentiel de l'historique (4 757 decks « légaux » sur 21 206), et en
priorité les decks qui jouaient des cartes touchées ensuite (biais de survivant). C'est ce qui rend
`meta_scores` si maigre (moins de 40 decks par mois avant 2026).

**Correctif (étape 1, faite) :** `scripts/compute_deck_legality.py` reconstruit la table `deck_legality`
(banlist en vigueur à la date `created` du tournoi, infractions comptées main + extra + side). Résultat :
20 220 decks légaux (TCG 9 282, OCG 10 938), 598 illégaux, 388 non évaluables (format Genesys, légalité
par points). Accord avec l'API de 99,6 % depuis juin 2026, période où la liste est stable.

- `illegal` n'est **pas** modifié : tant qu'on ne rebranche pas les notebooks, rien ne change.
- `days_to_boundary` : distance au changement de liste le plus proche. Autour d'un changement
  (≈ 14 jours) la date réelle d'entrée en vigueur est ambiguë (accord 84-92 % en fév.-mai 2026).
- **À vérifier :** `Stake Your Soul!` et `Vanquish Soul Razen` (Semi-Limited dans la liste de
  février 2026) concentrent les désaccords avec l'API : banlist scrapée ou API en cause ?
- **À vérifier :** l'API juge « légaux » des decks Genesys (≈ 11 % du TCG depuis février) : le
  méta TCG actuel en est probablement pollué.
- **Étape 2 (non faite) :** rebrancher les consommateurs sur `deck_legality` (`legal = 1`, et
  `days_to_boundary > 14` si on veut éviter les fenêtres ambiguës), recalculer `meta_scores`, les
  prédictions, les signaux boutique, puis relancer `build_ban_radar.py --backtest` (obligatoire,
  c'est un changement de données du scoring). Les chiffres de vitrine (r = 0,771…) changeront.

### 🧹 Nettoyage du backlog fiabilité (2026-11-16, branche `chore/nettoyage-backlog`)

Chiffres VÉRIFIÉS (commande lancée) ; voir `docs/evaluation-prediction.md`, `docs/tok-74-kewl-tune.md`, `docs/tok-77-genesys.md`.

- **Données rafraîchies** : 23 948 decks (TCG 11 618, OCG 12 330) jusqu'au 2026-11-14 ; `deck_legality` : 22 422 légaux, 915 Genesys non évaluables. Banlists à jour : TCG 2026-10-19, OCG 2026-10-01.
  `scripts/refresh_decks.py` (job launchd `com.tokoz.yugioh-refresh-decks`, lundi 8h30) enchaîne fetch TCG, OCG, légalité et journalise dans `data/fetch_health.jsonl` (`--status`).
- **Chaîne de recalcul** : `python scripts/refresh_all.py` (02 → 04 → banlist_features → 05 → 10 → buy_signals → 11 → ban_radar → card_impact → log_predictions → check), notebooks exécutés par nbconvert (copies dans `logs/executed/`). Tous les consommateurs lisent `deck_legality.legal = 1`.
- **Pièges trouvés** : `REFERENCE_DATE` figée au 2026-06-14 dans les notebooks 02 et 04 (corrigé : dernier deck chargé) ; `banlist_features` et `boutique_buy_signals` n'avaient plus de producteur (scripts `build_banlist_features.py`, `build_buy_signals.py`, rétro-ingéniérés) ; le notebook 11 ne s'exécutait pas (f-string) ; nb 11 garde des fenêtres codées en dur (`2025-12-01`, `2026-01-01`) à rendre relatives ; `meta_scores` mêlait TCG et OCG (54 % OCG) et groupait par `uploaded` : corrigé (TOK-80).
- **TOK-81 (fait)** : `build_buy_signals.py` v2 remet `price_opp` sur 0-100 (poids 70/30 inchangés) ; en v1 le prix pesait ≤ 0,3 point sur 100. Les rangs changent : à archétype égal, la carte bon marché passe devant. `BOUTIQUE_MODEL`/`EARLY_MODEL` passés en v2 dans `log_predictions.py`.
- **TOK-80 (fait)** : `meta_scores` = **TCG pur**, mois = date du tournoi (`created`) ; `meta_scores_ocg` = OCG, même formule (nb 04). `META_MODEL` = `blend-ridge-naive-tcg-pure-v2`. Le journal du 2026-11-16 contient donc deux versions (v1 mixte, v2 TCG) : seule v2 compte. Notebook 09 sur TCG propre : r = 0,574 (lag 2), 0,475 (lag 4).
- **TOK-82 (partie données)** : fenêtres du notebook 11 rendues relatives à la date du jour (TCG −168 j, OCG −380 j, méta −200 j) 
- **TOK-82 (partie front, fait 2026-11-16)** : `site-facts.ts` mis à jour (23 948 decklists, r ≈ 0,53 [0,43 ; 0,59], 105 archétypes, fenêtre « 2 à 6 mois ») ; textes de la home, tier list, boutique (« à surveiller » et non « à acheter », rappel du signal de juin perdant), prédictions (gain ≈ 5 %, pas de rupture) et Ban Radar (backtest 84/889, 19/1236, deux listes TCG récentes mauvaises) réécrits. `graphCommunities` (63) non recalculé. Les 63 communautés et r sont à relire à chaque refresh.
- **Backtest, listes TCG récentes** : le haut du classement tient (2026-10-19 : Droll & Lock Bird #3, Called by the Grave #5, Elfnote Tinia #6, Triple Tactics Talent #10) mais la liste du 2026-10-19 touche 43 cartes, dont beaucoup de cartes marginales (Amorphage, Naturia Beast, Spell Canceller…) qui tirent le rang médian à 308/905. [SUPPOSÉ, non testé] le rang médian est un mauvais critère sur une liste massive ; poids calés avant Genesys ; le méta Genesys (exclu) n'est pas vu par le Ban Radar. Pas de changement de WEIGHTS sans nouveau backtest.
- **Backtest Ban Radar (données légales, 2026-11-16)** : TCG 2026-05-18 rang médian 84/889 (avant 127/923), OCG 2026-07-01 19/1236 (avant 31/1089). Dix listes TCG et dix OCG passent désormais le seuil de 600 decks (au lieu de 2). ⚠ Les deux listes TCG les plus récentes sont mauvaises : 2026-09-21 rang 206/981 (hasard ≈ 490), 2026-10-19 rang 308/905 (hasard ≈ 452). Aucun poids modifié.
- **TOK-73** : gain du modèle prédictif ≈ 4 % de MAE sur la variation (ρ delta ≈ 0,35, égal à une régression à une variable). Signal OCG→TCG **réel mais** r ≈ 0,53 à 4 mois (IC95 [0,43 ; 0,59], 105 archétypes), plateau 2-6 mois, et r = 0,771/n = 43 non reproductible (cible mixte TCG+OCG).
- **TOK-74** : Kewl Tune pesait déjà 22-32 % du TCG légal de mai à juillet, 8,9 % en septembre, 0,4 % en octobre (Rotary Forbidden TCG 2026-09-21). Cartes du signal du 17 juin : −34,8 % (34 cartes ≥ 1 €) vs marché −0,8 %.
- **TOK-77** : Genesys = 27-44 % des decks TCG depuis juillet ; l'ancien filtre `illegal = 0` ne laissait presque que du Genesys.
- **TOK-75** : `python scripts/validate_predictions.py` (table `prediction_validation`) ; aucune prévision `live` n'est échue avant décembre 2026.
- **TOK-83 (2026-11-16)** : `GET /ban-radar` mettait 10-20 s (jointure `REPLACE(REPLACE(c.name…))` sans index). Fix : index d'expression `idx_cards_name_clean` (créé par `init_db.py` et `build_serving_db.py`) ; **la comparaison doit s'écrire `= +r.card_name`** (le `+` coupe l'affinité TEXT, sinon SQLite ignore l'index). À reproduire pour toute nouvelle jointure sur `cards`.
- **TOK-95 (2026-11-16)** : fusion `--no-ff` de `claude/front-vitrine-06112d` dans `main` (le correctif TOK-83 n'y était pas : `/ban-radar` 7,3 s, `/card-impact` 7,2 s, `/graph/synergies` 4,9 s → 0,01-0,06 s, mêmes temps sur `serving.db`). Erreur 500 de `/early-signals` : `EarlySignal.archetype` était `str`, or 31 lignes sur 151 de `early_card_signals` ont `archetype = NULL` (cartes sans archétype dans YGOPRODeck : Fydraulis Harmonia, Subspace Battle…). Le bug existait déjà, il est apparu quand le recalcul du lundi a fait entrer ces cartes dans le top 50. Corrigé en `str | None` (API et `types/index.ts`), la page affiche « — ». Ne pas filtrer les NULL en SQL : on cacherait des signaux réels.
- **Test de fumée de l'API** : `backend/tests/test_endpoints.py` appelle tous les GET (découverts via OpenAPI) et `POST /simulate-ban`, exige 200. Une route à paramètre obligatoire doit être ajoutée à `EXPLICIT_GETS`, sinon le test échoue. À lancer avant chaque push, sur les deux bases : depuis `backend/`, `../.venv/bin/python -m pytest tests -q` puis avec `YGO_DB_PATH=../data/serving.db`. Dépendances : `backend/requirements-dev.txt`. Les tables étant recalculées chaque lundi, c'est le seul garde-fou contre une donnée que le schéma Pydantic refuse.
- `data/serving.db` reconstruite (10,2 Mo). Sauvegardes locales : `data/backup_avant_nettoyage_20261116.db`, `data/backup_serving_avant_nettoyage_20261116.db`.

### 🛒 Signal boutique v3 (TOK-113, 2026-11-16)

Correctif **à la source** des deux défauts trouvés par TOK-97. Chaîne : notebook 10 → `boutique_alerts`,
`boutique_card_alerts`, `ocg_archetype_scores` → `build_buy_signals.py` → `boutique_buy_signals`.

- **Règle « pas encore en TCG » sur les cartes, pas sur le nom** : archétype retenu si ≥ 5 decks OCG légaux sur 3 mois
  et ≥ 3 cartes clés jamais sorties en TCG (ni vues dans un deck TCG, Genesys inclus, ni `cards.tcg_date` passée).
  La règle par nom (< 5 decks TCG sur 12 mois) gardait 55 archétypes sur 94, dont 40 avec moins de 3 cartes inédites :
  vieux archétypes TCG faibles (Labrynth, Runick), hybrides (Elfnote existe sous 6 noms en TCG). Toon et Witchcrafter,
  gardés par le filtre de l'API, sont joués en TCG depuis le 2026-11-14 sous d'autres noms.
- **Résultat au 2026-11-16** : 3 archétypes (Raise Moon 100, Trirealm Rift 56,6, Harpie/Amazoness 44,0), 42 cartes
  clés dont 30 inédites, **12 signaux d'achat : Fort 3, Modéré 5, Faible 4**. Seules les cartes déjà cotées ressortent.
- **`tcg_entry_estimated` n'existe plus** (c'était date du calcul + 4 mois). Remplacé par `tcg_window_start` /
  `tcg_window_end` : médiane du premier deck OCG des cartes inédites + 75 à 202 jours (P10-P90 du délai
  `cards.ocg_date` → `tcg_date` sur 1 897 cartes 2022-2025, médiane 103 jours). C'est un intervalle à 80 %, **non validé
  hors échantillon**. Une date par archétype n'est pas défendable (30 cas, 1 à 10 mois, 37 % jamais arrivés).
- **Staples** : decks TCG légaux, 12 mois, > 20 % des decks **et** ≥ 30 archétypes (24 cartes). À 6 mois, le seuil
  attrape les pièces de moteur des decks dominants (Fydraulis Harmonia, Medius the Pure). Même filtre côté OCG (10 cartes,
  dont Maxx "C") : la garde ≥ 30 archétypes y est indispensable, sinon 9 cartes Elfnote passent pour des staples.
- **Cartes interdites** : lues dans `banlist_history` (liste TCG en vigueur, 156) et plus dans `cards.ban_tcg` (116,
  figé au dernier `fetch_cards.py`). 4 cartes interdites étaient proposées à l'achat.
- **Date de référence = dernier deck chargé**, une seule borne OCG pour tout le notebook (plus de `date('now')`).
- **`ocg_archetype_scores`** (nouvelle table, 89 archétypes) : force OCG de **tous** les archétypes. Le notebook 11 la
  lit pour `signal_ocg` ; il lisait `boutique_alerts`, qui ne contient plus que 3 archétypes. Effet sur
  `early_card_signals` : Spearman 0,9996, top 50 identique.
- **Journal** : `BOUTIQUE_MODEL = unreleased-cards-v3`, `target_date` = mois de fin de fenêtre (NULL si la source n'a
  pas de fenêtre : on ne journalise jamais une échéance non calculée). `EARLY_MODEL` = v3. Les lignes boutique v1/v2
  restent (ajout seul) et `validate_predictions.py` les évalue **à part**, statut `évaluée_horizon_fixe`. Une ligne v3
  est jugée sur `arrived` : ≥ 5 decks TCG dont le nom contient l'archétype avant la fin de la fenêtre.
- `app.py` (Streamlit) affiche la fenêtre. `backend/app/routers/boutique.py` est repris tel quel de
  `claude/refonte-front-cbe8af` (fusion sans conflit) ; son filtre par nom fait désormais double emploi.

Limites connues, à ne pas présenter comme résolues :
- **Fort / Modéré / Faible sont relatifs au premier du lot** (`alert_norm` et `buy_score_100` divisés par le maximum) :
  il y a toujours un « Fort ». Aujourd'hui ce sont des génériques à moins de 0,50 € jouées par Raise Moon.
- **`cards` date du 2026-06-13** : `views_week` (moitié de la formule) est figé, et `fetch_cards.py` n'interroge que
  `format=tcg`. Les cartes inédites n'ont donc pas de vues : la moyenne se fait sur les seules cartes connues.
- Une générique peut sortir sous deux archétypes (Pot of Desires). « Harpie/Amazoness » est un nom hybride : son
  arrivée en TCG sous un autre nom serait manquée par le validateur.
- Le front de `main` lit encore `tcg_entry_estimated` (colonne à « — ») ; la fenêtre n'est servie par aucun endpoint.
- La base réelle est en schéma v3 depuis le 2026-11-16 et la branche est fusionnée dans `main` le même jour. Une
  branche antérieure à cette fusion qui lit `tcg_entry_estimated` répond 500 sur `/boutique/signals`.
  Sauvegardes : `data/backup_avant_boutique_v3_20261116.db`, `data/backup_serving_avant_boutique_v3_20261116.db`.

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

*Dernière mise à jour : 2026-11-16 (TOK-113 : signal boutique v3)*

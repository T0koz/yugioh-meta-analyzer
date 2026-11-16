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

> Les journaux détaillés (livraisons, chiffres datés, historique des tickets) sont dans `docs/journal/`. Ce fichier ne garde que l’essentiel et les pièges durables.

## État du projet — Phases 1 à 4 : ✅ TOUTES TERMINÉES

`yugioh.db` : 28 tables (cards 13 797, tournament_decks, deck_cards, meta_scores, early_card_signals, banlist_history, boutique_*, card_cooccurrence*, graph…), 14 notebooks (01 à 12), signal boutique OCG→TCG (r=0,771 à l’époque, remplacé par r ≈ 0,53 depuis le nettoyage du 2026-11-16). Tableau des tables, liste des notebooks, NLP combos : voir le journal.
→ détail complet : `docs/journal/etat-phases-1-4.md`

---

## Phase 5 — Front-end + API : 🏗️ En cours

### ✅ Backend FastAPI — Livré (TOK-31, 2026-08-05)

FastAPI + sqlite3 stdlib, routeurs dans `backend/app/routers/` (meta, boutique, graph, cards, ban_radar…), préfixe `/api/v1`, dev : `cd backend && ../.venv/bin/uvicorn app.main:app --reload --port 8000`. Pièges : voir « Pièges durables ».
→ détail complet : `docs/journal/backend-fastapi.md`

### ✅ Frontend Next.js — Branché sur l’API réelle (2026-08-05)

Next.js 16 + TS + Tailwind + shadcn + recharts + vis-network ; design system Ember (`docs/design-system.md`), aucune couleur brute dans `src/`. Arborescence, composants et pièges de refonte/graphe : journal (pièges clés copiés ci-dessous).
→ détail complet : `docs/journal/frontend-nextjs.md`

### Ban Radar (TOK-53) — scoring et backtest (extrait de la section Frontend, laissé ici : durable)

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


### ⚠ Pièges durables (copiés des journaux ; l’original reste dans `docs/journal/`)

**API / backend**
- `boutique_buy_signals` a une ligne par **(archétype, carte)** : une staple générique (ex: Super Polymerization) apparaît sous plusieurs archétypes → toute clé React doit combiner les deux, pas juste `card_name`
- **⚠ Bug corrigé (2026-08-05)** : `sqlite3.ProgrammingError` intermittente sur tous les endpoints — FastAPI exécute les routes `def` (sync) dans un threadpool, `sqlite3.connect()` sans `check_same_thread=False` casse dès que la requête tombe sur un thread différent de celui qui a ouvert la connexion. Fix dans `db.py`. **Si un nouvel endpoint sync est ajouté et manipule `db` directement sans passer par `get_db()`, il aura le même problème.**
- `GET /cards/search` est enregistré **avant** `GET /cards/{name}` dans `cards.py` — sinon FastAPI matche `/cards/search` comme `{name}="search"`. Respecter cet ordre pour toute nouvelle route `/cards/...`.

**Front Next 16**
**⚠ `frontend/AGENTS.md`** : Next 16 a un nouveau modèle de cache (`'use cache'` + Cache Components, opt-in via `cacheComponents: true` dans `next.config.ts` — **pas activé ici**, donc l'ancien `fetch(url, { next: { revalidate } })` utilisé dans `lib/api.ts` reste valide). Vérifier `node_modules/next/dist/docs/` si un changement touche au caching/fetch.
**⚠ Cache disque `.next/cache`** : persiste entre redémarrages du serveur dev (contrairement au cache mémoire). Si une donnée fraîchement ajoutée côté API n'apparaît pas côté front malgré un redémarrage du serveur, faire `rm -rf frontend/.next` avant de conclure à un bug.
- **Espace perdu dans un texte JSX multi-ligne qui contient une entité** (`&apos;`, `&amp;`…) : la compilation supprime l'espace initial du texte qui suit une balise ou une expression (« génériques</strong> trustent » rendu « génériquestrustent »). Écrire l'apostrophe typographique `’` plutôt que `&apos;`, ou construire la phrase dans une chaîne JS.
`HoverPreviewProvider`/`HoverPreviewPanel` remplacent l'ancien tooltip flottant par carte (`bottom-full` dans un conteneur `overflow-hidden` → invisible, clippé). Toute nouvelle page qui utilise `CardChip` doit être enveloppée dans un `<HoverPreviewProvider>` avec un `<HoverPreviewPanel />`, sinon `useHoverPreview()` lève une erreur.
**`InfoTooltip`** (`components/ui/info-tooltip.tsx`) : bulle ⓘ ouverte vers le **bas** (`top-full`, pas `bottom-full`) — sinon coupée par un ancêtre `overflow-hidden` (ex: conteneur de tableau). Ne pas revenir à `bottom-full` sans vérifier qu'aucun ancêtre ne clippe.
- Jointure `cards` ↔ noms issus de `deck_cards` : `cards.name` porte `<P>`/`<C>`/`<Q>` (« Maliss <P> March Hare »), pas `deck_cards` → joindre sur `REPLACE(REPLACE(c.name,'<',''),'>','')` (graph, ban_radar, card_impact). Les ~19 nœuds encore sans image sont des cartes récentes absentes de `cards` (relancer `fetch_cards.py`).
- **Piège LCP : ne jamais faire démarrer à opacité 0 un texte du premier écran.** Le LCP ne le compte qu'une fois
  visible ; le fondu d'entrée coûtait jusqu'à 0,8 s. L'utilitaire `enter` glisse sans fondu (`rise-in`) ; le fondu
  (`fade-rise`) est réservé à `Reveal`, sous le premier écran.

**Données, bases, pipeline**
- Le backend lit `YGO_DB_PATH` si la variable est définie, sinon `data/yugioh.db`.
  En production : `YGO_DB_PATH=/app/data/serving.db`.
- **À lancer après chaque recalcul d'une source** (notebook 05, notebook 10, notebook 11,
  `build_ban_radar.py`), puis **committer `data/prediction_log.jsonl`** : le commit (et le push) date
  la prédiction par un tiers. `--dry-run` simule, `--status` résume.
- Le script ouvre la base avec `timeout=60` : un processus qui garde `yugioh.db` ouverte (backend,
  notebook, agent) bloque l'écriture (`database is locked`).
- **TOK-83 (2026-11-16)** : `GET /ban-radar` mettait 10-20 s (jointure `REPLACE(REPLACE(c.name…))` sans index). Fix : index d'expression `idx_cards_name_clean` (créé par `init_db.py` et `build_serving_db.py`) ; **la comparaison doit s'écrire `= +r.card_name`** (le `+` coupe l'affinité TEXT, sinon SQLite ignore l'index). À reproduire pour toute nouvelle jointure sur `cards`.
- **Test de fumée de l'API** : `backend/tests/test_endpoints.py` appelle tous les GET (découverts via OpenAPI) et `POST /simulate-ban`, exige 200. Une route à paramètre obligatoire doit être ajoutée à `EXPLICIT_GETS`, sinon le test échoue. À lancer avant chaque push, sur les deux bases : depuis `backend/`, `../.venv/bin/python -m pytest tests -q` puis avec `YGO_DB_PATH=../data/serving.db`. Dépendances : `backend/requirements-dev.txt`. Les tables étant recalculées chaque lundi, c'est le seul garde-fou contre une donnée que le schéma Pydantic refuse.

**Ban Radar récent, combos**
- **Backtest Ban Radar (données légales, 2026-11-16)** : TCG 2026-05-18 rang médian 84/889 (avant 127/923), OCG 2026-07-01 19/1236 (avant 31/1089). Dix listes TCG et dix OCG passent désormais le seuil de 600 decks (au lieu de 2). ⚠ Les deux listes TCG les plus récentes sont mauvaises : 2026-09-21 rang 206/981 (hasard ≈ 490), 2026-10-19 rang 308/905 (hasard ≈ 452). Aucun poids modifié.
- **Garde de nom** : YGOPRODeck renumérote parfois une carte (même nom, autre `id`) et l'index sur
  `cards.name` n'est pas unique. Le script n'insère jamais un nom déjà présent (il l'affiche en ⚠).
  Toute autre insertion dans `cards` doit faire le même contrôle, sinon les jointures par nom doublent.

### `banlist_history` — scraping scripté, TCG + OCG

`scripts/fetch_banlist_history.py` reconstruit la table à chaque exécution (Yugipedia fait foi) ; colonne `format` TCG/OCG, ne plus filtrer sur le nom de page. Aucune liste TCG Yugipedia après le 2026-05-18 à l’époque.
→ détail complet : `docs/journal/banlist-history.md`

### 🗄 Base de service (déploiement, TOK-35)

`scripts/build_serving_db.py` → `data/serving.db` (≈ 10 Mo, 12 tables servies, `YGO_DB_PATH`), garde anti-dérive `SERVED_TABLES`, `--check` sans écriture.
→ détail complet : `docs/journal/base-de-service.md`

### 📒 Journal des prédictions (2026-11-01)

`scripts/log_predictions.py` → table `prediction_log` (append-only) + `data/prediction_log.jsonl` à committer (Thomas seul) après chaque recalcul ; `provenance` live/backfill.
→ détail complet : `docs/journal/journal-predictions.md`

### ⚖️ Légalité des decks à la date du tournoi (2026-11-01)

`scripts/compute_deck_legality.py` → table `deck_legality` (banlist en vigueur à la date du tournoi) ; le drapeau `illegal` de l’API est biaisé (banlist postérieure). Tous les consommateurs lisent maintenant `legal = 1`.
→ détail complet : `docs/journal/legalite-decks.md`

### 🧹 Nettoyage du backlog fiabilité (2026-11-16, branche `chore/nettoyage-backlog`)

Chiffres vérifiés : 23 948 decks, chaîne `scripts/refresh_all.py`, `meta_scores` TCG pur (TOK-80), signal OCG→TCG r ≈ 0,53 (TOK-73), backtest Ban Radar 84/889 (TCG) et 19/1236 (OCG), index `+r.card_name` (TOK-83), `EarlySignal.archetype` nullable (TOK-95), test de fumée de l’API.
→ détail complet : `docs/journal/nettoyage-backlog-fiabilite.md`

### 🎨 Refonte front « Braise vivante » (TOK-94)

TOK-96 (états, titres, contraste, CardThumb), TOK-97 (tier list calculée à la volée sur la part de decks, `backend/app/tiering.py`), TOK-98 (`CardArt`/next/image, mouvement CSS, Inter Tight, Lighthouse, piège LCP). Ordre imposé 96 → 97 → 98.
→ détail complet : `docs/journal/refonte-front-braise-vivante.md`

### 🛒 Signal boutique v3 (TOK-113, 2026-11-16)

Règle « pas encore en TCG » appliquée sur les cartes ; `tcg_entry_estimated` remplacé par `tcg_window_start`/`tcg_window_end` (intervalle 80 %, non validé) ; table `ocg_archetype_scores` ; limites connues listées dans le journal.
→ détail complet : `docs/journal/signal-boutique-v3.md`

### 🤝 Collaboration (TOK-107, 2026-11-16)

Collaboratrice data scientist qui pousse sur `main` sans revue, dépôt public : `python scripts/check.py` avant tout push, CI sans blocage, une seule base de référence (Thomas), snapshot via `scripts/export_db_snapshot.py`. Règles : `docs/ONBOARDING.md` §8.
→ détail complet : `docs/journal/collaboration.md`

### 🧩 Moteur de combos (TOK-84, préparation du 2026-11-16)

Projet distinct (`docs/moteur-combos/`), pas de code de moteur. `scripts/fetch_new_cards.py` ajoute les cartes absentes sans réécrire les existantes ; garde de nom obligatoire avant tout insert dans `cards`.
→ détail complet : `docs/journal/moteur-combos.md`

### 🧭 Travail en sessions parallèles (retour d'expérience du 2026-11-16)

Quatre sessions ont tourné en parallèle (front, collaboration, combos, signal boutique), chacune dans un worktree
`.claude/worktrees/…`, puis tout a été fusionné dans `main` (merges `--no-ff`) et poussé.
- **Un worktree n'a pas de base** (`data/*.db` non suivie) ni `node_modules` : lancer le backend avec
  `YGO_DB_PATH=<dépôt principal>/data/serving.db`, lire `yugioh.db` en lecture seule (`file:…?mode=ro`).
  `scripts/check.py` sait retrouver le venv et la base du dépôt principal.
- **Conflits garantis dans `context.md`** : chaque session ajoute sa section au même endroit. Résolution : garder les deux.
  Règle qui a marché : une session = une section de `BACKLOG.md` et de `context.md`.
- **Une base partagée change sous les branches** : la fusion de TOK-113 (schéma v3) a cassé `/boutique/signals` sur la
  branche front tant qu'elle lisait `tcg_entry_estimated`. Fusionner `main` dans la branche avant de la livrer.
- **Coût** : quatre sessions + sous-agents consomment vite. Une seule session vraiment active à la fois, une session neuve
  par ticket, ne pas laisser une session en lancer une autre sans accord de Thomas.
- Avant chaque push : `python scripts/check.py` (remplace la liste manuelle tsc / eslint / pytest / `--check`).

### 🏷 Seuil absolu des libellés boutique (suite de TOK-113, 2026-11-17)

`buy_label` (relatif au premier du lot) n'est plus servi. `GET /boutique/signals` renvoie `signal_label` (Fort / Modéré / Faible / null),
`archetype_rank` et `label_rule` : rang de l'archétype parmi les ~89 archétypes de `ocg_archetype_scores` (Fort ≤ 10 %, Modéré ≤ 25 %),
calculé à la volée (`backend/app/signal_label.py`), « seuils provisoires, non validés hors échantillon ». Les données ne permettent pas
de valider un seuil (une seule série datée, rien d'échu avant mars 2027) ; un rang est stable dans le temps, un seuil en points non.
`ocg_archetype_scores` est dans `SERVED_TABLES` : sans reconstruction de `serving.db`, l'API sert les signaux sans libellé.
→ détail complet : `docs/journal/seuils-signal-boutique.md`

### 🏠 Nouvelle page d'accueil (TOK-106, 2026-11-16, branche `claude/tok-106-accueil-66ff33`, non fusionnée)

Accueil « Braise vivante » portée du prototype : hero (éventail de 5 cartes, braises), exemple Kewl Tune piloté par le
défilement, bento d'outils, méthode et limites, pied de page (`SiteFooter`, accueil seulement pour l'instant).
Mesuré sur build de production, mobile, `LH_THROTTLING=devtools` : Performance 98, Accessibilité 100, LCP 1,79 à 1,88 s,
JavaScript transféré 180 ko, CLS 0.
- **`loading.tsx` ne doit pas revenir à la racine de `app/`.** Next enveloppait toutes les pages dans un Suspense : le
  HTML statique livrait le squelette puis le contenu dans un bloc caché révélé par script. Sans JavaScript, les pages
  n'affichaient que « Chargement des données… », et React retardait la révélation d'environ 0,4 s (c'était l'écart
  « non isolé » entre premier affichage et LCP). Il est dans `app/ban/` (seule route dynamique). Gain : LCP mobile
  ≈ 1,65 à 1,75 s sur les pages statiques (avant ≈ 2,0 s).
- **Ton des textes (consigne du 2026-11-16, tout le site)** : sobre, factuel, statistique ; aucun appel à l'action ; une
  phrase porte une mesure, une période et une source, sinon elle disparaît ; le graphique explique, le texte annote.
- **Tuile boutique** : le grand chiffre est le **rang de l'archétype** (`archetype_rank` sur `label_rule.population`),
  jamais `buy_score` (ordre d'affichage). Libellé `signal_label` toujours accompagné de « seuils provisoires, non validés
  hors échantillon ».
- **Données figées** : `lib/proof-data.ts` (parts mensuelles de Kewl Tune, relevé du 16/11 : `meta_scores_ocg` n'est pas
  servie) et `SITE_FACTS.banBacktest` (4 des 20 listes du backtest). À relever de nouveau quand la base change.
- **Effets** (`components/home/effects.tsx`) : chacun part d'un HTML serveur complet ; `data-live` (posé en JS, ≥ 900 px,
  mouvement autorisé) est le seul interrupteur du récit au défilement. Styles `home-*` dans `globals.css`.
- Tokens ajoutés : `--ocg` (série OCG uniquement), `--shadow-card`, `--holo`, `--tile-glow`. `CRITERIA` du Ban Radar est
  dans `lib/ban-criteria.ts` (partagé avec l'accueil). `LH_PAGES=/,/boutique` limite `npm run lighthouse` à quelques pages.
→ détail complet : `docs/journal/accueil-tok-106.md`

### 📈 Dataviz maison et palette de données (TOK-99, 2026-11-17, branche `claude/tok-99-dataviz-923148`, non fusionnée dans `main`)

recharts supprimé. `/evolution` (courbes, client) et `/predictions` (haltères, serveur) sont des SVG calculés avec D3 ;
palette catégorielle `--cat-1` à `--cat-6` (aussi sur la barre des critères du Ban Radar) ; `DataFooter` (source, date,
échantillon) sous chaque graphique et tableau. Mesuré : `/evolution` 190,6 ko de JavaScript (avant 274,1), Access. 100,
LCP mobile 1,76 s.
- **`d3-scale` reste côté serveur** : dans un composant client il ajoute ≈ 12 ko transférés et fait dépasser 200 ko.
  Côté client : `d3-array` (`nice`, `ticks`) + `d3-shape`, échelle linéaire écrite à la main. Jamais le paquet `d3` entier.
- **Texte de graphique ≥ 12 px** : à 11 px, l'audit « font-size » de Lighthouse fait tomber les bonnes pratiques à 96.
- **`npm run contrast`** (dans `frontend/`) après toute retouche d'un token de couleur : échoue sous 4,5:1.
- Les `--cat-*` disent qui (série, critère), jamais un état ; `--ocg` reste réservé à l'OCG et ne se mélange pas à eux.
  Toutes les paires de teintes ne sont pas séparables en vision daltonienne : toujours une étiquette ou une légende.
- **Tout nouveau graphique ou tableau** : `DataFooter` (date obligatoire) + alternative tabulaire en `<details>`.
- Champs ajoutés à l'API (rien de retiré) : `decks_by_month`, `data_month`, `computed_at`. La base servie n'a pas de date
  pour le graphe de co-occurrences : le pied du graphe et du simulateur l'écrit.
→ détail complet : `docs/journal/dataviz-tok-99.md`

### 🧬 Page d'archétype et transitions de vue (TOK-101, 2026-11-17, branche `claude/tok-101-archetype-49be45`, non fusionnée dans `main`)

`/archetype/{slug}` : part de méta, tier, tendance, part mensuelle (SVG serveur), cartes clés, signal boutique.
`GET /api/v1/archetypes/{slug}` (`routers/archetypes.py`) ne lit que des tables servies, aucun calcul nouveau.
Mesuré (build de production, mobile, `LH_THROTTLING=devtools`, 9 pages) : LCP 1,72 à 1,84 s, Accessibilité 100, CLS 0.
- **Le slug est calculé par l'API** (`backend/app/slugs.py`, a-z 0-9 et tiret) et servi (`slug` dans la tier list,
  `archetype_slug` dans les signaux boutique). Le front ne le recalcule jamais. 231 archétypes, aucune collision.
- **Résolution tolérante à la casse, exprès.** Le cache de pages de Next est rangé par chemin : sur macOS (disque
  insensible à la casse) une 404 calculée pour `/archetype/Branded` écrasait la page de `/archetype/branded`. Toute
  casse rend donc la même page ; l'adresse canonique est le slug servi. Une réécriture par expression régulière dans
  `next.config.ts` ne marche pas : ces motifs sont insensibles à la casse.
- **Les archétypes d'un signal boutique ne sont pas dans la tier list** (pas encore en TCG) : leur page existe quand
  même, sans graphique ni cartes clés, et s'ouvre depuis `/boutique`.
- **Fenêtres différentes sur la même page** : part et tier sur la fenêtre de la tier list (396 decks), cartes clés sur
  celle du Ban Radar (1 883 decks). Chaque bloc a son `DataFooter`.
- **Transitions de vue** (`experimental.viewTransition`, `components/view-transitions.tsx`) : `PageTransition` se place
  AUTOUR de `<Page>` (dans un nœud DOM qui vient d'être monté, l'entrée et la sortie ne se jouent pas) et prend un
  `id` qui sert de clé. `SharedElement` porte le même nom sur les deux pages. Tout est en `default="none"`.
- **Mouvement réduit** : la règle globale `*` ne couvre pas `::view-transition-*`, d'où une règle dédiée dans `globals.css`.
- **Texte de graphique en HTML positionné en pourcentage** (`ShareChart`) : dans un SVG à `viewBox`, 12 px deviennent
  6 px sur mobile. Le tracé est dans un SVG étiré (`vector-effect: non-scaling-stroke`).
- À faire au lot SEO : lien canonique vers le slug servi (les variantes de casse rendent la même page).
→ détail complet : `docs/journal/archetype-tok-101.md`

### 🔎 SEO de partage et tests visuels (TOK-100, 2026-11-16, branche `claude/tok-100-seo-tests-409521`, non fusionnée dans `main`)

Lien canonique, Open Graph, carte Twitter et image de partage sur chaque page ; `sitemap.xml` (10 pages + archétypes
servis par l'API) et `robots.txt`. Suite visuelle : 36 captures (12 pages × 3 largeurs) en 45 s, bruit mesuré 0 pixel.
Lighthouse SEO 100 sur 12 pages ; accueil inchangé (LCP mobile 1,80 s, JavaScript 182 ko).
- **Toute nouvelle page passe par `pageMetadata`** (`lib/seo.ts`) : Next ne fusionne pas `openGraph` entre layout et
  page, une page sans lui hériterait du titre et de l'adresse du layout. L'ajouter aussi à `STATIC_PATHS`
  (`app/sitemap.ts` et `scripts/check-meta.mjs`) et à `PAGES` (`scripts/visual_tests.py`).
- **Adresse publique** : `NEXT_PUBLIC_SITE_URL` (`frontend/.env.example`), sinon domaine Vercel, sinon
  `http://localhost:3000`. À renseigner au déploiement (TOK-35), sinon canoniques et sitemap pointent en local.
- **`python scripts/check.py --visuel`** (ou `.venv/bin/python scripts/visual_tests.py`) après toute retouche de
  l'interface ; changement voulu → `--update`, puis commiter les références. Hors du `check.py` par défaut : 45 s et
  le build télécharge les polices Google (échec réseau passager observé, alors « ignoré »).
- **Les captures ne lisent pas la base** : fausse API rejouant `frontend/tests/visual/fixtures/`. Si la forme d'une
  réponse d'API change, `--refresh-fixtures` (API réelle lancée), sinon la suite teste un contrat périmé.
- **Références produites sur macOS** : sur un autre système, les régénérer localement avant de comparer.
- **Images de partage** : aucune illustration de carte ; un chiffre seulement avec période et source. Couleurs lues
  dans `globals.css`, polices WOFF dans `src/assets/og-fonts/` (Satori ne lit pas le WOFF2).
- `npm run check:meta -- http://localhost:3100` vérifie les balises sur un build local (API réelle lancée).
→ détail complet : `docs/tests-visuels.md`, `docs/journal/seo-tests-tok-100.md`

### 🔘 Composants d'interaction (lot 8, 2026-11-17, branche `claude/lot08-boutons-ef9f72`, non fusionnée dans `main`)

Boutons, pills, onglets et bascules ont une seule source : `components/ds/control.tsx` (`Button`, `ButtonLink`, `Pill`,
`PillLink`, `TabRail`, `TabLink`, `controlClass`) + le bloc `.ctl` de `globals.css`. CSS seul. Mesuré : JavaScript
transféré inchangé (`/evolution` 191,4 ko avant et après, même script de mesure), CSS +0,7 ko, CLS 0, 0 animation en
mouvement réduit, pire contraste 4,52:1 (désactivé).
- **Tout nouveau bouton, filtre ou onglet passe par ce composant.** Sur la page : utilitaires de mise en page seulement.
- **Listes d'ombres à nombre de couches constant** (2 internes + 3 portées) entre états, sinon la transition saute.
- **Le bloc est dans `@layer components`** : hors couche, il l'emporterait sur les utilitaires Tailwind (`w-full`…).
- **Largeur de la nav à 768 px** : quatre onglets + la recherche tiennent avec 10 px de retrait par onglet, pas 12.
- **Un build avec `NEXT_DIST_DIR=<autre dossier>`** réécrit `frontend/tsconfig.json` et son dossier n'est pas ignoré
  par Git (seuls `.next` et `.next-visual` le sont) : ne pas faire `git add -A` après, et restaurer `tsconfig.json`.
- Toute retouche d'un contrôle change les 36 captures (la nav est sur chaque page) : `--update` après relecture.
→ détail complet : `docs/design-system.md` §4 « Composants d'interaction »

### 🃏 Decks : index et fiche de composition (TOK-114, lot 9, 2026-11-16, branche `claude/lot09-tok-114-decks-99ff00`, non fusionnée dans `main`)

`/decks` et `/decks/{slug}` : par archétype et par zone, part des listes qui jouent chaque carte (« 94 %, 15 sur 16 »)
et exemplaires médians ; 5 listes récentes avec leur résultat. `scripts/build_archetype_profiles.py` → 3 tables servies
(`archetype_card_profile`, `archetype_recent_decks`, `archetype_recent_deck_cards`) → `GET /decks`, `GET /decks/{slug}`.
Mesuré : LCP mobile 1,75 à 1,87 s, Accessibilité 100, `serving.db` 10,7 → 11,6 Mo.
- **Seuils à un seul endroit**, `backend/app/deck_profile.py` : de base ≥ 80 % des listes, d'appoint ≥ 20 %, fiche à
  partir de 8 listes (en dessous, la page ne montre que les listes). Le script compte, il ne pose aucun seuil.
- **Même fenêtre et même population que la tier list** (`MIN_WINDOW_DECKS` importé) : le test de fumée vérifie que les
  effectifs de `/decks` et de `/meta/tier-list` sont égaux. Le script tourne donc après le notebook 04.
- **Un pourcentage ne s'affiche jamais sans son effectif** (« k sur n »). Pas d'intervalle : trop large à 8 listes.
- **Pas de colonne masquée dans un tableau `table-fixed`** (les cellules se décalent) ; **pas d'illustration `eager`
  dans une tuile** (elle devient l'élément LCP sur mobile) ; **une capture de plus de 16 383 px casse `--update`**
  (limite WebP) : garder les longues listes repliées.
- **Toute nouvelle route a son `opengraph-image.tsx`** : celle de la racine ne descend pas.
- Dans un worktree : `build_archetype_profiles.py --db <dépôt principal>/data/yugioh.db`.
→ détail complet : `docs/journal/decks-tok-114.md`

### 🛠 Outillage : pré-autorisations, garde-fou, fin de journée (lot 13, 2026-11-16, branche `claude/lot13-outillage-195837`, non fusionnée)

`.claude/settings.json` (partagé) : règles `allow` précises (lecture, `git status/diff/log/show`, `check.py`, `tsc`, `eslint`, build, pytest) et `deny` des
compositions dangereuses (`find -delete/-exec`, `--fix`, `rg --pre`, `--output`). Hook `PreToolUse` `.claude/hooks/garde_fou.py` : refuse `git push` (toutes
formes), `--force`, `--no-verify`, `rm -rf` hors `.claude/worktrees/` ; 52 cas testés (`python .claude/hooks/test_garde_fou.py`, branché dans `check.py`).
Commande `/fin-de-journee` (`.claude/commands/`) : propose les diffs de `context.md` et `BACKLOG.md`, ne commite pas.
- **Une règle `Bash(...)` porte sur le texte, pas sur le sens** : `Bash(rm *)` ne bloque pas `bash -c 'rm …'`, `git push *` ne bloque pas `git -C . push`. Le hook, lui, découpe la commande (`shlex`) et examine chaque segment ; il tourne même sans règle.
- **Un hook ne se déclenche qu'après fusion** de la branche dans celle de travail ; les worktrees déjà ouverts le lisent depuis leur propre copie de `.claude/`.
- **`npm run lighthouse` n'est pas pré-autorisé** (il lance un serveur). Détail : `docs/planning/2026-11-17/decisions-prises.md`, essai : `docs/planning/2026-11-17/essai-fin-de-journee-16-11.md`.

### 🗣 Charte « ton et explication » (lot 15 étape 1, 2026-11-17, branche `claude/lot15-charte-23027e`, non fusionnée)

`docs/charte-ton-et-explication.md` : ton, ordre d'explication (encodage → annotation → incertitude → légende → pied → Méthode repliée), règles d'incertitude appuyées sur 8 listes / 600 decks / k sur n, 10 avant / après, inventaire (6 `InfoTooltip`, 8 formules ou notations). **Validée par Thomas le 17/11** : infobulles gardées pour une définition simple, aucune formule sur le site (`/methode` sans formule), mois < 100 decks atténués, intervalles dessinés, couches après maquette. Étape 2 après les lots 11 et 12.

### 🖼 Images de cartes hébergées (TOK-92, lot 10, 2026-11-17, branche `claude/lot10-tok-92-images-5c0cd5`, non fusionnée)

0 requête vers `images.ygoprodeck.com` (navigateur et serveur, mesuré sur build de production, 10 pages × 2 largeurs).
- **Incrémental** : `python scripts/download_card_images.py` (ajoute seulement les cartes sans fichier ; fait aussi partie de
  `refresh_all.py`, en dernier). Emplacement : `<dépôt principal>/data/card-images/` (`art`, `card-sm`, `card-lg`, 1,1 Go, ignoré).
- **Front** : `NEXT_PUBLIC_CARD_IMAGES_URL` (défaut `/card-images`, servi par une route locale lisant `CARD_IMAGES_DIR`,
  par défaut `../data/card-images` : dans un worktree, la renseigner). `lib/card-images.ts` seul connaît les URL.
- `fetch_cards.py` ne met pas `cards` à jour (JSON seul) ; la chaîne utilise `fetch_new_cards.py`. Ne jamais y mettre `init_db.py`.
- Les tests visuels remplacent `/_next/image` par un aplat : ils ne dépendent pas du dossier d'images.
- **TOK-35** : choisir le stockage, y envoyer le dossier, renseigner la variable.
→ détail : `docs/journal/images-tok-92.md`

### 🚀 Préparation du déploiement Vercel (TOK-35, lot 14, 2026-11-17, branche `claude/lot14-tok-35-deploiement-2c1401`, non fusionnée)

Option A configurée sans rien déployer : `vercel.json` (racine, **Vercel Services**, bêta tous plans : service `backend` FastAPI `app.main:app` + service `frontend` Next.js, `/api/*` → API), `.vercelignore`, `.env.example`.
Guide pas à pas et formulaire de décisions : `docs/deploiement.md`.
- **Le projet doit être relié depuis la racine**, Root Directory vide, preset « Services » (le lien actuel part de `frontend/`).
- **Base embarquée** : `cp data/serving.db backend/data/serving.db` (ignoré par Git) avant `vercel deploy` ; sur Vercel (`VERCEL` défini) `db.py` la lit seule, et ouvre toujours en `mode=ro`. Pas de Git connecté : tout déploiement part de la machine de Thomas.
- **Bloquant** : le build du front interroge l'API (pages pré-générées), et la liaison `BACKEND_URL` ne se résout pas au build ; `lib/api.ts` et `card-chip.tsx` partagent `NEXT_PUBLIC_API_URL`. Lot de code à prévoir (§ 8.1 du guide).
- **Images** : ni Vercel Blob (1 Go et 2 000 opérations gratuits pour 1,17 Go et 42 136 fichiers) ni le déploiement (100 Mo) ne conviennent ; recommandé : Cloudflare R2 (10 Go, 1 M d'écritures gratuits, sortie gratuite). `next/image` : 5 000 transformations par mois en Hobby → images de cartes en `unoptimized` (lot suivant).
- **Protection** : la production est indexable ; « All Deployments » + Vercel Authentication est gratuit (tous plans), Password Protection est payant. Retour arrière sur Hobby : seulement le déploiement de production précédent.

### 🛒 Boutique par archétype et courbes de prix (TOK-103, lot 11, 2026-11-17, branche `claude/lot11-tok-103-boutique-e98c5d`, non fusionnée)

`/boutique` regroupée par archétype : frise rang OCG + fenêtre d'arrivée TCG (80 %), calendrier des relevés, une courbe
Cardmarket par carte. `scripts/build_boutique_price_history.py` → table servie `boutique_price_history` → `GET /boutique/prices`.
Mesuré : LCP mobile 1,75 à 1,79 s (4 mesures sur 5), Accessibilité 100, 3 captures changées.
- **Trous** : deux relevés à plus de 10 jours ne sont pas reliés (`backend/app/price_history.py`, seul endroit) ; la période
  est hachurée, rien n'y est tracé. Sous 3 relevés, points seulement.
- **Relevés de prix** : avant ce lot, `snapshot_prices.py` ne tournait qu'au lancement de Streamlit (`run.sh`) ; il est
  maintenant dans `refresh_all.py`, suivi de l'extrait boutique.
- Après fusion, sur la base de référence : `python scripts/build_boutique_price_history.py` puis `python scripts/build_serving_db.py`.
- Scénario de test des gérants : `docs/tests-gerants-boutique.md`.
→ détail complet : `docs/journal/boutique-tok-103.md`

### 📜 Ban Radar contre l'historique (TOK-55, lot 12, 2026-11-17, branche `claude/lot12-tok-55-ban-historique-206ce4`, non fusionnée)

Onglet `/ban?tab=historique` : 20 banlists rejouées (10 TCG, 10 OCG), rang médian des cartes touchées face à la bande du
hasard (90 %) et à la base « staples les plus jouées », top 25 de la veille face aux cartes touchées, 6 listes écartées
affichées. `scripts/build_ban_history.py` → `ban_backtest_lists`, `ban_backtest_cards` (servies) → `GET /ban-radar/history`.
- **Ordre** : `build_ban_history.py` puis `build_serving_db.py` (sinon « Table absente »). Pas encore dans `refresh_all.py`.
- **Mêmes chiffres que `--backtest`** : le script passe par `build_ban_radar.backtest_lists`, la boucle de `backtest()`.
  Toute modification du backtest passe par cette fonction, jamais par une copie.
- **⚠ La base staples bat le score en rang médian sur 7 listes TCG sur 10** (le score reste devant en OCG, 8 sur 10, et
  en tête de classement : top 25 touché 29 contre 16 en TCG, 41 contre 18 en OCG). Le piège « l'omniprésence seule ne
  prédit rien » (section Ban Radar ci-dessus) vient de la v1 sur données biaisées : à réviser après validation de Thomas.
- **Veille de l'entrée en vigueur, pas de l'annonce** : les decks joués entre les deux sont dans la fenêtre (jusqu'à 10 %).
  Ne jamais écrire « avant l'annonce ». Seules 3 listes sont postérieures au calage des poids (2026-08-14).
→ détail complet (sorties brutes, vérification du data scientist) : `docs/journal/ban-historique-tok-55.md`

### 🔜 À faire

- **Thomas** : pseudo GitHub de la collaboratrice (TOK-108), envoi de la base (TOK-109, `scripts/export_db_snapshot.py`), protection de `main` (interdire force-push), contact d'un juge pour les combos (TOK-89, `docs/moteur-combos/dossier-juge.md`)
- **Suites de TOK-113** : rafraîchir `cards` dans la chaîne (`views_week` figé au 13 juin), seuil absolu pour Fort / Modéré / Faible
- **TOK-92** : images faites (section ci-dessous) ; reste l'envoi vers le stockage définitif au déploiement (TOK-35)
- **Vérifier** au prochain `fetch_cards.py` que le nom corrigé par la session combos n'est pas écrasé

- **TOK-35** : déploiement — base de service prête, reste à trancher l'hébergement (Vercel seul vs Vercel + Railway) et à fournir les credentials
- **TOK-52** : Mode Joueur / Mode Boutique (toggle UX) — nécessite de trancher ce que chaque mode change concrètement (pas fait en autonome pour cette raison)
- **TOK-55** : page faite (lot 12, section ci-dessus) ; reste les dates d'annonce des banlists (veille de l'annonce au lieu de l'entrée en vigueur) et l'ajout à `refresh_all.py`
- **Phase B/C (TOK-54 à 67)** : Deck Builder, Referral boutique, API freemium — voir BACKLOG.md

### ✅ Fait en autonome / avec Thomas le 2026-08-05

TOK-33, 48, 49, 50, 51, fix thread-safety SQLite, redesign `/tier-list` (depuis remplacé par la liste dense Ember).
→ détail complet : `docs/journal/faits-2026-08-05.md`

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

*Dernière mise à jour : 2026-11-16 (fin de journée : refonte front, collaboration, combos et TOK-113 fusionnés dans `main`)*

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

### 🔜 À faire

- **Thomas** : pseudo GitHub de la collaboratrice (TOK-108), envoi de la base (TOK-109, `scripts/export_db_snapshot.py`), protection de `main` (interdire force-push), contact d'un juge pour les combos (TOK-89, `docs/moteur-combos/dossier-juge.md`)
- **Suites de TOK-113** : rafraîchir `cards` dans la chaîne (`views_week` figé au 13 juin), seuil absolu pour Fort / Modéré / Faible
- **TOK-92** : images de cartes à ré-héberger avant le déploiement ; des cartes récentes n'ont toujours pas d'image (`fetch_new_cards.py` tourne désormais le lundi)
- **Vérifier** au prochain `fetch_cards.py` que le nom corrigé par la session combos n'est pas écrasé

- **TOK-35** : déploiement — base de service prête, reste à trancher l'hébergement (Vercel seul vs Vercel + Railway) et à fournir les credentials
- **TOK-52** : Mode Joueur / Mode Boutique (toggle UX) — nécessite de trancher ce que chaque mode change concrètement (pas fait en autonome pour cette raison)
- **TOK-55** : Ban Predictor vs History — deux points de mesure concluants disponibles (TCG mai 2026, OCG juillet 2026), la page publique reste à faire
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

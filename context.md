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
- **L'omniprésence prédit une partie des bans, mais pas la tête de liste** (révisé le 2026-11-17, validé par
  Thomas ; remplace « l'omniprésence seule ne prédit rien »). L'ancien constat venait de la v1 (rang médian 302/681,
  le hasard), calculée sur des données biaisées par le drapeau `illegal`. Sur données légales (backtest rangé liste par
  liste, lot 12, `docs/journal/ban-historique-tok-55.md`), une base « staples les plus jouées » (même univers classé
  par la seule part des decks) fait **mieux que le score en rang médian sur 7 listes TCG sur 10** — tendance, **pas un
  écart démontré** (test du signe p = 0,34, diagnostic TOK-115) ; le score reste devant en OCG (8 sur 10) et **en tête
  de classement** : top 25 de la veille touché 29 fois sur 250 contre 16 pour les staples en TCG, 41 contre 18 en OCG
  (seul l'écart OCG est démontré, 9 listes sur 10, p = 0,02). Lecture : le score sert à désigner les premières cartes visées, pas à classer
  l'ensemble mieux que la popularité. Toute retouche du scoring se compare aux deux bases (hasard et staples), pas au
  hasard seul. Le nombre d'archétypes qui jouent une carte ne discrimine toujours pas (médiane 4 chez les touchées
  comme chez les autres, constat v1 non recalculé).
- **Le critère décisif est le nombre moyen d'exemplaires joués** (2.50 chez les
  touchées vs 1.10). Le retirer fait tomber le rappel top-10% de 5/10 à 1/10 (chiffres de la v1, non recalculés
  sur données légales : à vérifier au prochain changement de scoring).

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

**Lot 18, fondations du moteur (2026-11-18, branche `claude/lot18-fondations-moteur-dab1df`, non fusionnée)** : paquet
`moteur_combos/` (état, schéma, chargement du deck, harnais), base à part `data/combos.db` (jamais `yugioh.db`, lue en
`mode=ro`). Commande : `python scripts/combos_harnais.py` (`--detail`). 72 départs construits (48 complets, 24 avec
mémoire en texte libre), classement 54 « règles confirmées » / 6 « un seul avis » / 12 « non exécutable sans règles ».
**Aucune règle de jeu codée.** Horloge de la règle d'arrêt ouverte : J2 avant le 13/01/2027 (décision 0053).
- **Isolement de l'oracle** (TOK-86, AGPL) : ne jamais lire son code ni `~/code/oracle-ignis/` ; seul
  `docs/moteur-combos/reponses-oracle.md` (données) est lisible.
- **Le texte des cartes vit dans `combos.db`** (copie locale, ignorée par Git) ; un texte changé remet la carte à
  `non_traitee` (errata). Le dépôt ne garde que `text_sha256`.
- **Le statut d'un point de règle est lu dans `points-de-regle-a-valider.md`** : changer la colonne « Relecture 1 » ou
  « Confiance » change le classement. R27 se précise en R27a / R27b dans `moteur_combos/classement.py`.
- Tests : `python -m pytest moteur_combos/tests` (branché dans `check.py` quand `moteur_combos/` ou les fichiers du jeu
  de tests changent ; les tests qui lisent les textes demandent `yugioh.db`, sinon « ignorés »).
→ détail : `docs/moteur-combos/definitions-et-schema.md` (§ 2 mis à jour, § 3), décisions par défaut :
`docs/planning/2026-11-18/decisions-prises.md`

**Lot C1, tranche 0 du moteur (TOK-90, 2026-11-18, branche `claude/c1-tok-90-tranche-0-554a89`, non fusionnée)** :
premières règles de jeu (`moteur_combos/regles.py` : Invocation Normale, Invocation Spéciale et Fusion, activation,
coût, limites dans les cinq formes, chaîne simple), 5 cartes formalisées (`cartes.py` : Aluber, Branded Fusion,
Fallen of Albaz, Tri-Brigade Springans Kitt, Rindbrumm en `brouillon`), 10 situations exécutées et conformes au YAML
(`scenarios.py` : T01, T03, T04, T05, T08, T09, T11, T15, T60, T68). Combo : Aluber → Branded Fusion → Rindbrumm
(Albaz + Kitt du Deck) → Kitt rappelle Albaz. Formulaire : `docs/planning/2026-11-18/decisions-prises.md` (C1).
- **« Non couvert » s'applique effet par effet** : une formalisation déclare tous les effets ; une résolution peut
  rester `NON_CODEE` (jamais jouée) ou `HORS_PERIMETRE` (suppose l'adversaire). Une carte `non_traitee` jouée,
  déplacée ou choisie → `non_couvert` ; restée en main → **réserve** dans le résultat ; option de légalité inconnue →
  liste « peut-être incomplète ». Ne jamais faire disparaître une option : la ranger dans l'une de ces trois sorties.
- **Formaliser une carte, c'est écrire contre `text_sha256`** : un errata désactive la formalisation (test dédié).
- **Un scénario traduit l'action d'une situation, il ne dit jamais le verdict** : verdict et `choix` viennent du YAML.
- Plusieurs déclencheurs simultanés → `non_couvert` (R22 non tranché) ; le test « retirer X » (hypothèse de Winston,
  definitions § 4) n'est pas encore écrit.

**Lot C2, J1 formalisation (TOK-118, 2026-11-18, branche `claude/c2-j1-formalisation-a044b3`, non fusionnée)** : les 37
cartes du pilote sont `formalisee` (`moteur_combos/cartes_j1.py` + tranche 0) ; 72 effets déclarés, 57 du pilote, tous
exercés par un test ; 69/72 situations du YAML et 30/30 situations J1 (`situations-j1.yaml`, verdicts de l'agent)
exécutées et conformes ; 0 erreur de formalisation trouvée, 173 tests pytest. **J1 non déclaré atteint** : le taux
d'erreur demande l'oracle sur les situations J1 et la relecture à l'aveugle de 20 effets tirés (graine 20260118, cible
borne haute Wilson ≤ 20 %). Rapport : `docs/moteur-combos/j1-rapport.md` ; pour l'oracle :
`situations-pour-oracle.md` ; formulaire : `docs/planning/2026-11-18/decisions-prises.md` (C2).
- **`formalisee` = résolutions écrites ET chaque effet du pilote exercé par un test** (`regles.EXERCES`, compté par le
  harnais), sinon `brouillon`. Le YAML n'exerçait que 29 des 57 effets : sans la mesure, 28 effets jamais joués
  auraient été déclarés formalisés.
- **R22 codé** (ordre libre, obligatoires d'abord) ; **R23 obligatoire** (texte TCG) contre l'oracle (texte OCG).
- **Passer les tests du premier coup ne vaut pas vérification** : YAML et formalisation sont deux lectures LLM du même
  texte. Le 0/30 d'aujourd'hui est un constat, pas le taux de J1 (avis `data-scientist-ygo`).
- 13 points non tranchés par le texte (N01 à N13, marqués ⚖ dans le code) ; N01 (`Luluwalilith` sur sa propre sortie
  de l'Extra Deck) répond « non couvert » : toute Invocation Synchro de `Luluwalilith` est non couverte pour l'instant.
- Une situation J1 ou un scénario du YAML est une traduction en décisions ; la liste attendue reste celle du YAML.
  Nouvelle situation : départ dans `situations-j1.yaml`, scénario dans `SCENARIOS_J1` (`scenarios.py`).

**Lot C3, J2 exploration (TOK-119, 2026-11-18, branche `claude/c3-j2-exploration-ff7592`, non fusionnée)** : étape 0
(N09 corrigé : un monstre insensible reste choisissable par un effet sans cible, l'effet est sans effet sur lui ; N01
et DIVIN adoptés ; N04 « Attribut déjà porté » gardé permis par le texte TCG) ; exploration bornée
(`moteur_combos/exploration.py`, 8 filtres déclarés D4, largeur ou A* vers une cible, jalons), stockage dans
`combos.db` (schéma inchangé), 5 combos de guides publics (`docs/moteur-combos/combos-guides.md`). Résultat : séquences
retrouvées **4 sur 5 sans cible** (largeur, 60 s), 5 sur 5 vers la cible, joueur au hasard 0 sur 5 ; **J2 « atteint sous
réserve », horloge du 13/01/2027 maintenue**. Commande : `python scripts/combos_j2.py` (≈ 12 min). Rapport et
formulaire : `docs/moteur-combos/j2-rapport.md`.
- **Une décision à une seule option ne consomme jamais d'entrée du préfixe de réponses** (au premier passage comme au
  rejeu) : sinon le préfixe se décale et des branches entières disparaissent sans erreur (bug trouvé au lot C3).
- **Un combo « à une carte » se joue avec la carte seule** (les 4 autres retirées du jeu) : avec des cartes de réponse
  en main, le moteur s'en sert comme matériel (`Ghost Ogre` pour `Granguignol`).
- **Une cible de plateau ne suffit pas à dire « retrouvé »** : G3 la remplissait par un autre chemin ; les jalons
  (actions clés du guide, en sous-suite) font la différence.
- ≈ 1 200 états/s, facteur 3 à 4 par transition : le parcours en largeur ne dépasse pas 6 transitions en 60 s.

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
  servie) et `SITE_FACTS.banTop25` (bilan top 25 par format, 20 listes du backtest, depuis le lot 16). À relever de nouveau quand la base change.
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


**Étape 2 (2026-11-17, branche `claude/lot15-explication-graphique-d831c8`, non fusionnée)** : composants `components/ds/explain.tsx`
(effectif, légende, annotation, barre d'intervalle, bande, mois atténués, couche « Méthode »), `DataFooter` avec `uncertainty`
obligatoire, `InfoTooltip` au toucher et au clavier (une phrase de définition), page `/methode` sans formule, bande de Wilson à 95 %
sur `/evolution` (qui trace maintenant la part des decks), la page d'archétype et la tier list. Accessibilité 100 sur 9 pages,
`/evolution` 192 → 190 ko de JavaScript, 0 formule dans le HTML rendu de 16 pages.
- **Wilson dans un seul module** (`lib/wilson.ts`, `npm run test:stats`, lancé par `check.py`). Intervalle minimal : decks supposés
  indépendants. Validé par le data scientist ; **à relire par la collaboratrice avant mise en ligne**.
- **Un mois de moins de 100 decks ne fixe pas l'échelle** (à 1 deck, une part vaut 100 %) ; le dernier mois relevé est « en cours »
  par convention (pas de date système, captures déterministes).
- `GET /meta/evolution` sert `decks` (k) en plus ; une réponse figée sans lui se rabat sur `share × n`.
- `next build` refuse un `node_modules` en lien symbolique hors du projet : `cp -cR` pour construire un autre commit.
- **Verdict du Ban Radar non écrit** (consigne de Thomas, 17/11) : onglet Historique et sections Ban Radar de `/methode` sans
  phrase de conclusion sur la qualité du score ; emplacement « lecture en attente du diagnostic TOK-115 » (lot 15a).
→ détail complet : `docs/journal/explication-graphique-lot15.md`
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
- **Images** : ni Vercel Blob (1 Go et 2 000 opérations gratuits pour 1,17 Go et 42 136 fichiers) ni le déploiement (100 Mo) ne conviennent ; Cloudflare R2 retenu (10 Go, 1 M d'écritures gratuits, sortie gratuite).
- Retour arrière sur Hobby : seulement le déploiement de production précédent.

**Lot 14 bis (2026-11-17, branche `claude/lot14bis-code-deploiement-3f856b`)** — choix de Thomas : R2, site public non diffusé (aucune protection), voie 2.
- **Adresse de l'API** (`apiBaseUrl()`, `lib/api.ts`) : serveur `API_URL` → `BACKEND_URL` + `/api/v1` → `NEXT_PUBLIC_API_URL` → `localhost:8000` ;
  navigateur `NEXT_PUBLIC_API_URL` (`/api/v1` en ligne). `API_URL` ne va **jamais** dans les variables Vercel (elle masquerait `BACKEND_URL`).
  Une `NEXT_PUBLIC_API_URL` relative côté serveur lève une erreur explicite.
- **Voie 2** : `python scripts/deploy_prebuilt.py` vérifie (base, copie ignorée par Git, API locale, lien à la racine) et **affiche** `vercel pull` /
  `vercel build` / `vercel deploy --prebuilt --archive=tgz` ; `--execute preview|prod` les lance (Thomas seul). `--prebuilt` + Services : cohérent avec
  la doc (Build Output API par services), pas décrit explicitement ; repli au § 8 du guide.
- **Piège `--prebuilt`** : les variables système manquent au build. `VERCEL_ENV` est passée par le script (noindex des aperçus) ;
  `NEXT_PUBLIC_SITE_URL` est obligatoire en Production, sinon canoniques en `localhost:3000` (le script refuse sans elle).
- **Images de cartes en `unoptimized`** (`CardImage`, `SafeImage`) : 0 requête `/_next/image` mesurée (657 images, 10 pages × 2 largeurs).
  Tout nouvel affichage d'image de carte passe par `CardArt`/`CardImage`, jamais `next/image` directement.
  `visual_tests.py` remplace aussi `/card-images/…` par l'aplat : 45 captures identiques.
- `.vercel/` ignoré à la racine (`vercel pull` y écrit des variables).

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
  en tête de classement : top 25 touché 29 contre 16 en TCG, 41 contre 18 en OCG). Le piège de la section Ban Radar a été
  révisé en conséquence le 2026-11-17 (validé par Thomas).
- **Veille de l'entrée en vigueur, pas de l'annonce** : les decks joués entre les deux sont dans la fenêtre (jusqu'à 10 %).
  Ne jamais écrire « avant l'annonce ». Seules 3 listes sont postérieures au calage des poids (2026-08-14).
→ détail complet (sorties brutes, vérification du data scientist) : `docs/journal/ban-historique-tok-55.md`

### 🔬 Diagnostic du Ban Radar TCG (TOK-115, lot 15a, 2026-11-17, branche `claude/lot15a-tok-115-diagnostic-d81236`, non fusionnée)

`scripts/diagnose_ban_radar.py` (lecture seule, graine fixée, ≈ 50 s) : régression logistique sur les 20 listes du
backtest, validation temporelle à fenêtre croissante, bootstrap par liste + test du signe. **Aucun poids modifié.**
- **Les poids écrits ne sont pas les poids effectifs** : poids × écart type du critère. Effectifs : exemplaires 40 %,
  tendance 24 %, part des decks 17 %, déjà restreinte 13 %, porteur 5 %, pont 2 %. Toute retouche de `WEIGHTS` se
  raisonne en poids effectifs (le script les imprime).
- **Pourquoi le TCG résiste** : 47 % des cartes touchées TCG jouées à moins de 1,5 exemplaire (22 % en OCG) ; pris
  seuls, exemplaires et tendance ont une AUC de 0,61 et 0,59 en TCG contre 0,83 pour la part des decks.
- Régression tenue à l'écart (7 listes TCG) : bat les poids actuels en rang médian (7/7, p = 0,016), pas les staples
  (4/7) ; top 25 25 contre 13 aux staples. Règle d'adoption non remplie → formulaire (recommandation : ne rien changer).
- Avec 10 listes par format, seul l'écart de top 25 en OCG (9/10, p = 0,02) dépasse le hasard au test du signe.
→ détail complet et formulaire : `docs/journal/ban-radar-tcg-diagnostic.md`

### ✍️ Réécriture des textes (lot 16, première moitié, 2026-11-17, branche `claude/lot16-reecriture-textes-9d97ee`, non fusionnée)

`docs/textes-avant-apres.md` : tous les textes visibles de `frontend/src/` (846), page, fichier:ligne, problème, proposition ;
formulaire en tête. 43 à changer (titres en question ou en promesse, intros sans effectif, « trustent », « réessaie »), 28 textes
du Ban Radar qui jugent le score **en attente du formulaire TOK-115** (formulations tirées de la relecture). Boutique, Decks et
Méthode déjà conformes. Rien n’est appliqué avant la validation de Thomas.
- **`scripts/check_copy.py`** (bibliothèque standard) : règles de la charte §1 et §5 sur le texte visible seulement ;
  `--dump` liste les textes relevés, `--strict` rend l’étape bloquante. Dans `check.py` : avertissement quand
  `frontend/src/` change (ou `--all`), à passer en `--strict` une fois les textes appliqués.
- **Extraction heuristique** : un texte JSX coupé par `{expr}` sort en morceaux ; le titre de l’accueil (tableau `TITLE`)
  échappe à l’extracteur. Un faux positif se déclare dans `ALLOW`, jamais en affaiblissant une règle.
- « Yu-Gi-Oh! » est exclu de la règle du point d’exclamation (nom de marque).

**Seconde moitié (2026-11-18, branche `claude/lot16-application-textes-8896be`, non fusionnée)** : T01 à T43 et B01 à B28
appliqués (99 lignes marquées ✅ dans `docs/textes-avant-apres.md`, écarts au § 0) ; titre neutre « Méta Yu-Gi-Oh! TCG et
OCG » (h1, partage, image) ; `check_copy.py --strict` **bloquant** dans `check.py` (853 textes, 0 occurrence) ; 35 captures
sur 51 régénérées. Aucun `WEIGHTS`, aucune donnée ni API touchés.
- **Verdict du Ban Radar écrit une fois** (`lib/ban-verdict.ts`, chiffres de `SITE_FACTS.banTop25`, backtest du 16/11) : accueil,
  encart du Radar, onglet Historique, `/methode`. Dans l’Historique, il disparaît si les listes servies ne donnent plus les
  mêmes sommes (`verdictMatches`) : après une nouvelle banlist, relancer le diagnostic, puis réécrire `banTop25` et le texte.
- **Le titre de l’accueil** (`TITLE`, mots révélés un à un) échappe toujours à `check_copy.py` : à relire à la main.
- Un worktree n’a pas de `frontend/node_modules` : `cp -cR <dépôt principal>/frontend/node_modules frontend/` (clone APFS,
  ≈ 10 s, ignoré par Git) avant `tsc`, `eslint` ou les captures.

### 🧪 Audit de rigueur statistique (lot 19, 2026-11-17, branche `claude/lot19-audit-rigueur-e3bee6`, non fusionnée)

Aucun score ne remplit « estimé, validé hors échantillon, comparé au naïf, incertitude affichée » ; pires écarts : signaux précoces (carte interdite en tête, banlist figée au 13 juin), fenêtre d'arrivée « 80 % » couvrant 62-67 % en 2024-2025, score boutique ≈ part OCG (ρ 0,94) → `docs/journal/audit-rigueur-statistique.md`.

**Correctifs A1 à A8 (lot 20, TOK-122, 2026-11-18, branche `claude/lot20-audit-a1-a8-cbc82f`, non fusionnée)** : un commit par ticket ; `early_card_signals` produite par `scripts/build_early_signals.py` (référence = dernier deck, banlist à date, cartes déjà en méta exclues ; colonne `as_of`), couverture réelle de la fenêtre d'arrivée affichée (62-67 %), r ≈ 0,53 sorti du bandeau boutique, simulateur décrit comme une approximation, libellé affiché journalisé, flèche des prédictions sur l'écart dessiné, réglages manuels datés sur `/methode`, tendance de la tier list corrigée (Benjamini-Hochberg) et tiers « limite ». Après fusion : `build_early_signals.py` puis `build_serving_db.py`. Pièges : `text_synergies` (notebook 07, hors chaîne) ne couvre plus les cartes récentes, la proximité de texte vaut 0 ; l'IC « −4 % » de l'audit vient d'une table d'avant TOK-80 ; seuls 20 archétypes sont testés pour la tendance, pas 60 ; `PRED_GAP_THRESHOLD` (0,003) suit `W_MODEL` du notebook 05. Formulaire : `docs/planning/2026-11-18/decisions-prises.md` (lot 20).

### 📅 Dates d'annonce des banlists (TOK-121, lot 21, 2026-11-18, branche `claude/lot21-dates-annonce-65588d`, non fusionnée)

Table nouvelle `banlist_announcements` (`scripts/fetch_banlist_announcements.py`, Yugipedia + sources citées ; `banlist_history`
intacte, hors `SERVED_TABLES`, dernière étape de `refresh_all.py`) ; `diagnose_ban_radar.py --annonces` classe la veille de
l'annonce. Les 20 listes du backtest ont une date ou une raison écrite (16 avec le jour de publication des cartes, 4 TCG
avec une borne haute seulement). Effet : OCG ≈ 5 rangs médians sur 1 100 (9 listes sur 10), TCG rien de net, aucun des 60 tests
ne survit à la correction ; **verdict de l'Historique inchangé**.
- **« Annoncée » ≠ cartes publiques.** Konami OCG publie la date de la liste ~10 jours avant son contenu, et Yugipedia écrit
  « first announced » pour l'une ou l'autre (OCG 2026, TCG 2024-09 : date de sortie seule). La table a `announced_date` et
  `content_date` ; toute mesure coupe à `content_date`. Jamais de date devinée : sans preuve, la colonne reste vide.
- Coupure plus tôt = fenêtre de 6 mois et césure de tendance plus anciennes aussi : pas de lecture « annonce seule » sans placebo.
- `build_ban_radar.backtest_lists(..., as_of_override)` : paramètre optionnel, défaut inchangé.
→ détail complet : `docs/journal/dates-annonce-banlists-tok-121.md`

### 📐 Ban Radar en rangs et pont daté (TOK-120, lot 22, Jalon 1, 2026-11-18, branche `claude/j1-tok-120-132-ban-radar-pont-d32da4`, non fusionnée)

Diagnostic seulement : `WEIGHTS` inchangés, `--backtest` identique (84/889, 19/1236), rien d'affiché ne change.
`scripts/diagnose_ban_radar_rangs.py` (ou `diagnose_ban_radar.py --rangs [--coupure contenu]`, ≈ 1 min) : critères en rangs
centiles par liste, logit conditionnel par liste (Breslow, vérifié contre l'exacte), pont daté (`scripts/bridge_date.py`).
**Règle d'adoption non remplie** : le logit conditionnel sur les rangs la remplit à la veille de l'entrée en vigueur, pas à
la veille du contenu (OCG 3/7 contre les poids actuels) ; contre les staples en TCG, égalité (−0,15 point, 5/7, p = 0,45).
Recommandation A (ne rien changer), validée par `data-scientist-ygo`.
- **En rangs centiles, les poids écrits deviennent les poids effectifs** (sauf « déjà restreinte », 93 % d'égalités à 0),
  et les poids estimés sur les rangs sont proches des poids écrits (0,29 / 0,20 / 0,17 / 0,16 / 0,12) : le défaut du score
  était l'échelle brute des critères, pas la valeur des poids. Le pont reçoit un poids négatif (−0,05 [−0,10 ; −0,01]).
- **`card_graph_metrics` est périmée** (663 nœuds ; le graphe recalculé aujourd'hui en a 1 402, Spearman 0,31) : elle
  alimente le critère `bridge` et la « fragmentation » du simulateur. `bridge_date.py` reproduit `card_cooccurrence` à
  l'identique à la date du jour (10 741 paires).
- **`load_usage` filtre sur `created`, pas `uploaded`** : 2,5 % des decks des fenêtres du backtest sont mis en ligne après
  la coupure (surtout dans « tendance »). Correction = changement du backtest, au formulaire.
- Toute règle d'adoption future : candidats et règle figés dans la docstring avant la première exécution, aux deux coupures.
→ détail complet et formulaire : `docs/journal/ban-radar-rangs-tok-120.md`, `docs/planning/2026-11-18/decisions-prises.md` (lot 22)

**Score de pont et simulateur contre les banlists (TOK-132, B3, lot 26, même branche)** : `scripts/diagnose_pont_simulateur.py`
(≈ 4 min, lecture seule, rien d'affiché ne change). Mesure : variation de la part cumulée des archétypes porteurs (≥ 50 % de
leurs decks jouent la carte), 3 mois avant / 3 mois après ; 17 listes, 158 cartes touchées. Un ban fait baisser ses
porteurs (−3,1 points contre des cartes de même popularité, −5,5 sans contrôles contaminés). **Le score de pont
(`card_impact`, onglet « Impact ») va dans le sens contraire** à part des decks égale (+6,5 [+4,5 ; +8,6]) : il mesure la
diffusion d'une carte, dont le ban déplace le moins ses porteurs. Fragmentation du simulateur : bon sens, aucun gain hors
échantillon ; « archétypes voisins » : 31 % seulement sont des archétypes de deck, pas meilleurs qu'une liste naïve.
Formulaire : renommer « Impact » en « Diffusion », simulateur décrit sans prévision (non appliqué).
- **Une règle de gain doit fixer le sens attendu** : ici le « gain » hors échantillon venait d'un coefficient de signe
  contraire à l'affirmation testée (signe ajouté après lecture, déclaré).
→ détail complet : `docs/journal/pont-simulateur-tok-132.md`, formulaire `docs/planning/2026-11-18/decisions-prises.md` (lot 26)

### 🌱 Signaux précoces rejoués contre « vues seules » (TOK-129, B2, Jalon 1, 2026-11-18, branche `claude/j1-tok-129-93-signaux-fraicheur-d1344d`, non fusionnée)

`scripts/backtest_early_signals.py` (≈ 35 s, lecture seule, graine fixée, rien d'affiché ne change ; dépend de TOK-122) rejoue
`build_early_signals.py` à 25 dates (2024-07 → 2026-07) ; « entrer en méta » = ≥ 3 % des decks TCG légaux sur 120 j.
Critère B2 **rempli en cartes** (P@20 0,536 contre 0,382 aux vues, +0,154, IC dates [+0,066 ; +0,252]) **mais pas robuste** :
≈ 8 épisodes (effectif efficace 6,5), écart nul compté par archétype (+0,026 [−0,063 ; +0,119] par épisodes). Signal solide :
la force OCG sans vues désigne l'archétype qui arrive (+0,272 [+0,114 ; +0,430] contre les vues). Le texte coûte −0,106.
Recommandation au formulaire : revoir la page (archétypes classés par la force OCG, après backtest propre).
- **`views_week` n'existe qu'à une date** (`data/raw/cards.json`, commit du 13/06) : toute date antérieure voit des vues du
  futur. Aucun test des vues n'est possible sans archive datée.
- **Compter les réussites en archétypes, pas seulement en cartes** : un top 20 rempli d'un archétype qui arrive gonfle la
  precision@20 ; bootstrap par épisodes (dates consécutives du même archétype), pas seulement par dates.
- **Le calcul servi n'est pas le calcul testé** : texte nul au lot 20 (`text_synergies` hors chaîne) ; le recalculer ferait
  revenir le texte, qui fait baisser le score.
→ détail complet : `docs/journal/signaux-precoces-backtest-tok-129.md`, formulaire `docs/planning/2026-11-18/decisions-prises.md` (TOK-129)

### 🩺 Fraîcheur des tables servies et santé de `/top-decks` (TOK-93, Jalon 1, 2026-11-18, même branche, non fusionnée)

`scripts/check_freshness.py` (stdlib, `mode=ro`) : une règle par table de `SERVED_TABLES` (`computed_at`, `as_of` contre
le dernier deck, mois, cohérence graphe ↔ `card_cooccurrence`, historique ↔ banlists, vues ↔ instantané du 13/06, fille ↔
mère, sinon « non datée ») + un GET sur yugiohmeta `/top-decks`. Code 1 si une table est périmée ou l'endpoint en erreur ;
ligne `fraicheur_tables` dans `data/fetch_health.jsonl` ; `--status`. Dernière étape de `refresh_decks.py` (après
`serving`, sur `serving.db`) et contrôle de `deploy_prebuilt.py`. Au 18/11 : 12 ok, 3 périmées connues tolérées jusqu'au
31/12 (graphe 663 contre 1 402 nœuds, TOK-136 ; vues figées), 2 non datées, 2 lues par aucun routeur ; endpoint HTTP 200.
- **Jamais un contrôle qui peut échouer dans `refresh_all.py`** : son code 1 fait sauter `serving` dans `refresh_decks.py`.
- **Nouvelle table servie → une règle dans `RULES`** (test : toute table de `SERVED_TABLES` en a une) ; table vide,
  absente ou colonne de date vide = périmée, jamais tolérée ; une tolérance (`KNOWN_STALE`) a toujours une expiration.
- **Ne pas nommer une ligne du journal `"freshness"`** : `refresh_decks.py` relit ces lignes pour le nombre de decks.
→ détail complet (plan B si `/top-decks` disparaît) : `docs/journal/fraicheur-tables-tok-93.md`, formulaire TOK-93

### ⏳ Fenêtre d'arrivée en TCG par analyse de survie (TOK-130, B1, Jalon 2, 2026-11-18, branche `claude/jalon-2-survie-intervalles-ocg-af6a73`, non fusionnée)

Diagnostic seulement : la fenêtre affichée (75-202 jours, notebook 10) ne change pas. `scripts/build_arrival_survival.py`
(≈ 8 s, lecture seule ; `--write` écrit deux tables nouvelles non servies, `--reference` requis sur la base du dépôt
principal) : Kaplan-Meier par archétype, censure et entrée différée, validation à origine glissante mensuelle.
**Critère non atteint et non testable** : 5 prévisions seulement sur 2024-2025 (85 % annoncés, 60 % observés, IC de
l'écart [−60 ; +15]) ; 2025-2026 : 18 fenêtres justes sur 23 (78 %) pour 89 % annoncés, fenêtre actuelle 15 sur 23,
écart non démontré (p = 0,45). Formulaire : `docs/planning/2026-11-18/decisions-prises.md` (Jalon 2, TOK-130).
- **Arrivée définie par les cartes** (la moitié des cartes inédites sorties en TCG), pas par le nom : 9 libellés sur 62
  étaient déjà joués en TCG sous ce nom avant l'ancre. Le validateur (`validate_predictions.py`) juge encore par le nom.
- **Le « 37 % jamais arrivés » ne vaut pas pour la population du notebook 10** : 42 arrivées sur 44 unités, P(jamais)
  ≤ 6,5 %. Le défaut principal est l'échantillon (données OCG depuis janvier 2024), pas le biais du survivant.
- **En unité archétype, la fenêtre actuelle couvre 27 sur 36 (75 %)** sur 2024-2026, 12 sur 18 sur 2026 seule
  (hors échantillon) ; le 62-67 % de l'A2 est en unité carte.
- La probabilité Kaplan-Meier est trop confiante d'environ 11 points : ne jamais l'afficher comme couverture.
→ détail complet : `docs/journal/fenetre-survie-tok-130.md`

### 📏 Intervalles de prévision par archétype (TOK-131, B4, Jalon 2, 2026-11-18, branche `claude/jalon-2-survie-intervalles-ocg-af6a73`, non fusionnée)

`scripts/build_prediction_intervals.py` (≈ 6 s, lecture seule ; `--write [--reference]` écrit la table nouvelle
`meta_prediction_intervals`, non servie) : conformité séquentielle sur les résidus du walk-forward de la prévision
servie (TCG, fonctions importées d'`evaluate_prediction.py`), calibration sur les mois antérieurs. Retenue par règle
figée : Mondrian par terciles de niveau, **75,7 % [67,7 ; 82,0]** pour 80 % visés sur 24 mois (507 prévisions) ; 5
premiers du mois 68,3 %. Rien d'affiché ne change : `GET /meta/predictions` sert `interval_lo/hi` seulement si la table
existe, `/predictions` ne les dessine qu'avec `NEXT_PUBLIC_PREDICTION_INTERVALS=1`. Formulaire : `decisions-prises.md`
(Jalon 2, TOK-131).
- **Une couverture moyenne de 80 % ne prouve rien ici** : les deux naïves y sont aussi (78,7 et 82,8 %). Les ratés sont
  sur les gros archétypes et sur 4 mois de rupture de méta, où tous les archétypes bougent ensemble (échangeabilité
  violée) ; le centre de la prévision, à 30 % du retour à la moyenne, est biaisé vers la persistance en tête de méta.
- **Ne jamais écrire `meta_prediction_intervals` sur la référence avant le formulaire** : le routeur la cite, donc
  `build_serving_db.py` refusera de construire tant qu'elle n'est pas dans `SERVED_TABLES`.
- Le notebook 05 entraîne le modèle de production sur des lignes qui incluent la cible partielle du mois en cours
  (effet 0,11 point en moyenne, négligeable pour les intervalles, à corriger à part).
→ détail complet : `docs/journal/intervalles-tok-131.md`

### 🗾 Parts OCG mensuelles servies (TOK-116, Jalon 2, 2026-11-18, branche `claude/jalon-2-survie-intervalles-ocg-af6a73`, non fusionnée)

L'exemple Kewl Tune de l'accueil lit `GET /archetypes/kewl-tune` (`history` en TCG, `ocg_history` en OCG,
`ocg_history_computed_at`) au lieu des données figées de `proof-data.ts` (décision 0041). `meta_scores_ocg` est dans
`SERVED_TABLES` (règle de fraîcheur ajoutée). Valeurs identiques au relevé du 16/11, 51 captures inchangées.
- **Après fusion : `python scripts/build_serving_db.py`** sur la référence. Sans cela, `test_home_example_has_both_series`
  échoue sur `serving.db` et l'accueil n'affiche pas la section (rendu volontairement absent plutôt que partiel).
- **Une table lue par un routeur doit y être nommée en clair** (« FROM meta_scores_ocg ») : `build_serving_db.py --check`
  et `check_freshness.py` repèrent les tables par expression régulière, une requête construite par f-string leur échappe.
- **Fenêtre fixe** (août 2025 → novembre 2026) : les textes de l'accueil nomment ses mois et ses pics ; un recalcul qui
  déplacerait un pic ne serait vu par aucun test.
- Nouvelle fixture de test visuel : `kewl-tune` ajouté à `ARCHETYPES` dans `scripts/visual_tests.py`.
→ détail complet : `docs/journal/parts-ocg-servies-tok-116.md`

### 🔍 Vérification des données du 18/11 (TOK-133, Jalon 3, 2026-11-18, branche `claude/jalon-3-entretien-vitrine-280593`, non fusionnée)

Rapport seul, lecture seule : `docs/planning/fond/2026-11-18-donnees.md`. 20 tables servies identiques entre `yugioh.db`
et `serving.db` (schéma et empreinte des lignes) ; fraîcheur par `check_freshness.py --sans-journal` (aucune périmée
hors tolérances) ; bornes respectées (parts, scores, prix, exemplaires).
- **13 cartes jouées n'ont pas de fiche dans `cards`** (`Bystial Druiswurm`, 4 974 decks ; 4 `Artmage …` ; `Empire of
  Endymion` contre `Endymion Empire`…) : sans image ni lien, mais le score du Ban Radar n'est pas touché (statut lu dans
  `banlist_history`). Proposé : table de correspondance des noms et contrôle « cartes jouées sans fiche ».
- **`cards.ban_tcg` est figé au 13/06** comme `views_week` (12 désaccords avec la banlist en vigueur) : le site lit
  `banlist_history`, mais `evaluate_prediction.py` et `combos_extract_deck.py` lisent encore `cards.ban_tcg`.
- 116 cartes sans illustration carrée chez YGOPRODeck (4 affichées) ; 40 decks à moins de 40 cartes de Main Deck.
- `build_serving_db.py --check` ouvre `data/yugioh.db` du checkout : dans un worktree, passer par un lien ou par
  `check_coverage` sur une connexion `mode=ro`.

### 📚 Documentation réalignée sur le code (TOK-134, Jalon 3, 2026-11-18, même branche, non fusionnée)

`docs/api-contracts.md` (16 endpoints au lieu de 8, paramètres et champs réels), `docs/data-models.md` (effectifs du
18/11, colonnes changées, 12 tables ajoutées), `docs/architecture.md`, `README.md`, `docs/ONBOARDING.md` (stack Next 16 /
D3, chaîne `refresh_decks.py` / `refresh_all.py`, 20 tables servies, r ≈ 0,53 au lieu de 0,771). Écart par écart :
`docs/planning/fond/2026-11-18-documentation.md`. Doc seulement.
- **Écarts restés dans le code** (docstrings) : `check.py` dit les textes « non bloquants » (ils le sont depuis le
  lot 16) et « 45 captures » (51) ; `build_serving_db.py` dit « 12 tables, ~9 Mo » (20, ~12 Mo).
- Toute nouvelle route ou table : la ligne de `api-contracts.md` (tableau des endpoints) et la section de
  `data-models.md` vont avec.

### 🧪 Tests de l'API (TOK-135, Jalon 3, 2026-11-18, même branche, non fusionnée)

`backend/tests` : 74 → 125 tests passés + 1 `xfail`, sur les deux bases, sans réseau ni modification du code testé.
Nouveaux fichiers : `test_price_history.py`, `test_labels_mapping.py`, `test_db.py`, `test_routes_synthetic.py` (routes
sur bases en mémoire : filtres, tri, bornes, 404/422), `test_api_invariants.py` (base réelle : tier = `tier_for`, trous
de prix = `find_gaps`, libellés boutique, seuils du backtest), `test_build_serving_db.py`.
- **Bug signalé (`xfail`)** : `/cards/search` et `resolve_card_name` mettent la saisie telle quelle dans un `LIKE` :
  « % » et « _ » ne sont pas échappés (« %% » renvoie toutes les cartes, `/cards/%25` une carte au lieu d'un 404).
- **`test_build_serving_db.py` voit une table citée par un routeur et absente de `SERVED_TABLES` même si elle n'existe
  pas encore** (ce que `check_coverage` ne voit pas) ; un alias SQL inédit dans un routeur s'ajoute à `NOT_TABLES`, une
  table lue seulement si elle existe à `OPTIONAL_TABLES` (`meta_prediction_intervals` aujourd'hui).
- Les routes se testent sans base avec `app.dependency_overrides[get_db]` et une connexion `:memory:`
  (`check_same_thread=False`, `row_factory = sqlite3.Row`).
→ détail : `docs/planning/fond/2026-11-18-tests.md`

### 🌙 File de nuit du 16-17/11 (orchestrateur) : fusionnée dans `main` le 17/11

Lots 1 à 19 fusionnés (`--no-ff`) dans la branche d'intégration `claude/front-nuit-17-11`, elle-même **fusionnée dans `main` le
17/11 vers midi (`bd22ae8`), après la revue avec Thomas ; rien poussé** (`main` a 120 commits d'avance sur `origin/main`).
Le dépôt principal est revenu sur `main`. Dernier `check.py --all --visuel` : vert (46 tests sur chaque base, 51 captures).
Les sections ci-dessus qui disent « branche … non fusionnée » sont donc dans `main`. État lot par lot : `docs/planning/etat.md` ;
décisions prises par défaut : `docs/planning/2026-11-17/decisions-prises.md` ; Linear synchronisé le 17/11 (tickets livrés en « In Review »).
- **Bases modifiées par l'orchestrateur** (après sauvegarde `data/backup_*_20261116.db` / `_20261117.db`) : tables ajoutées par TOK-114,
  TOK-103 et TOK-55 dans `yugioh.db` (aucune table existante changée, vérifié contre les sauvegardes) ; `serving.db` reconstruite (11,8 Mo).
- **Parallélisme** (règle de Thomas, 17/11, `file.md`) : un lot à la fois ; une deuxième session seulement pendant une attente passive de la
  première, sur d'autres fichiers ; jamais plus de deux. Motif noté dans `etat.md`.
- **Modèle** : lots front sur Opus 5.5 à partir du lot 11 (consigne de Thomas du 16/11 au soir) ; `CLAUDE.md` dit encore « Fable ».
- **Garde-fou** : faux positif connu (heredoc qui cite la commande de push) et contournements par la syntaxe du shell, rapport de revue
  `docs/planning/fond/2026-11-17.md` sur la branche `claude/fond-2026-11-17-b80f1e` (non fusionnée, tâche de fond).

### 🔜 À faire

- **Priorité n° 1 depuis le 18/11 (décision de Thomas) : le moteur de combos (TOK-84).** Chaîne de la file : lot 17 (oracle,
  TOK-86) et lot 18 (fondations, TOK-117) en cours, puis C1 tranche 0 (TOK-90) → C2 J1 formalisation (TOK-118) → C3 J2
  exploration (TOK-119, échéance de la règle d'arrêt 13/01/2027). Le reste (16, 20 = TOK-122, 21 = TOK-121, 22 = TOK-120,
  23-26 = TOK-123, tâches de fond) passe en deuxième session, pendant une attente passive. Lots de méthode : rien d'affiché ne
  change sans formulaire de Thomas ; la relecture de la collaboratrice vient après (décision du 18/11).
- **Validé par Thomas le 17/11 (revue du matin, détail dans `docs/planning/2026-11-17/decisions-prises.md`)** : formulaire TOK-115
  (poids inchangés, verdict de l'Historique tel que proposé) ; audit de rigueur (A1-A4 puis A5-A8) ; textes du lot 16 (tout appliquer,
  titre neutre « Méta Yu-Gi-Oh! TCG et OCG », `check_copy.py` bloquant) ; source de l'oracle TOK-86 (`edo9300/ygopro-core`, usage
  local hors dépôt) ; D1 à D7 du moteur de combos ; les 14 notes « à valider » de `docs/decisions/` (52 acceptées).
- **Lots prêts à lancer** (un à la fois) : 20 (correctifs
  A1 à A8 de l'audit). Le lot 17 (TOK-86) est prêt aussi : `premake` 5.0.0 et `lua@5.4`
  installés le 17/11 (`/opt/homebrew/opt/lua@5.4`, non liée ; le cœur demande Lua 5.3 ou 5.4, pas la 5.5 de `brew install lua`).
- **Encore en attente de Thomas** : lots de correctifs de la revue de code (rapport de la tâche de fond).
- **TOK-116** : livré au Jalon 2 (parts OCG servies, `build_serving_db.py` à relancer après fusion).
- **Push de `main` par Thomas** (fusion faite le 17/11, `check.py --all --visuel` vert) ; supprimer les worktrees et les branches de lots fusionnées.
- **TOK-35** : relier le projet Vercel depuis la racine du dépôt, créer le compte Cloudflare R2, premier déploiement de prévisualisation (`docs/deploiement.md`).
- **Thomas** : pseudo GitHub de la collaboratrice (TOK-108), envoi de la base (TOK-109), protection de `main`.
- **TOK-89, relecture 1 faite le 17/11** (joueur de tournoi, non arbitre) : 32 points de règle sur 34 confirmés, taux d'erreur
  mesuré 1/34 (Wilson 95 % : 0,5 à 14,9 %, borne optimiste : un relecteur, ancrage sur la lecture affichée). **D3 infirmée**
  (colonnes et Zone Monstre Extra comptent), révisée le 18/11 en « entre-deux » ; **D1 maintenue** malgré l'absence de
  `Lubellion` (83 % des listes) : si le jalon J2 échoue sur un combo qui passe par elle, suspecter la liste avant le moteur.
  Le Google Form régénéré depuis `dossier-juge.md` par `scripts/build_judge_form.py` (`formulaire-juge.gs`).
  → `docs/moteur-combos/reponses-juge-2026-11-17.md`
- **À relire par la collaboratrice** : calcul de Wilson (`frontend/src/lib/wilson.ts`), diagnostic TOK-115, recalculs de l'audit (62-67 %, 0,94).
- **Suites** : `views_week` figé au 13 juin ; date de calcul du graphe de co-occurrences absente ; dates d'annonce des banlists ;
  gain du modèle de prédiction cité à 4, 5 ou 6 % selon les documents.
- **TOK-52** : Mode Joueur / Mode Boutique — à trancher ce que chaque mode change.
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

*Dernière mise à jour : 2026-11-17 (revue du matin : décisions validées, lots 1 à 19 fusionnés dans `main`, non poussés)*

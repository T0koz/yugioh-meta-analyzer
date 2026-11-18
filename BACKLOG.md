# Backlog — Yu-Gi-Oh! Meta Analyzer

Statuts : `✅ Done` · `🔜 À faire`
Priorités : `🔴 High` · `🟠 Medium` · `🟢 Low`

Suivi détaillé sur [Linear](https://linear.app/tokoz) (**source de vérité**).
Tickets terminés (✅ Done) et leurs « état » détaillés : [`docs/journal/backlog-archive.md`](docs/journal/backlog-archive.md). Ce fichier ne garde que les tickets ouverts, en cours ou à faire.

---

## Phase 5 — Front-end & API 🏗️ En cours

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-35 | Déploiement (Vercel front + back) | 🟡 Préparé le 2026-11-17 (lot 14, branche `claude/lot14-tok-35-deploiement-2c1401`) : `vercel.json` (Services), `.vercelignore`, base embarquée en lecture seule, guide `docs/deploiement.md`. Code de déploiement le 2026-11-17 (lot 14 bis, branche `claude/lot14bis-code-deploiement-3f856b`) : adresses d'API serveur / navigateur séparées, images de cartes sans `/_next/image`, script voie 2 `scripts/deploy_prebuilt.py`. Rien déployé. Reste à Thomas : relier le projet depuis la racine, envoyer les images sur R2, variables, premier `--execute preview` (`docs/deploiement.md` §0) | 🔴 High |

**TOK-35 — état :** `scripts/build_serving_db.py` produit `data/serving.db`
(9,4 Mo contre 236 Mo), le backend la lit via `YGO_DB_PATH`. Plus besoin de
volume persistant. Reste à trancher l'hébergement : à cette taille, l'API peut
sans doute tourner en serverless à côté du front, ce qui rendrait Railway inutile.

---

## Fiabilité des données & validité statistique — point du 2026-11-16

Issu du point projet du 2026-11-16 (voir `docs/ONBOARDING.md` §4-5 pour le détail). Ordre de
traitement conseillé : TOK-70 → TOK-72 → TOK-69 → TOK-74 / TOK-73.

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-76 | Risque : dépendance à l'API non officielle yugiohmeta | 🟡 Monitoring fait (`data/fetch_health.jsonl`) ; risque structurel reste | 🟠 Medium |
| TOK-78 | Onboarding d'une data scientist (`docs/ONBOARDING.md` fait ; accès tranché : dépôt public, écriture directe, base par Drive — voir TOK-107) | 🟡 Reste l'invitation (TOK-108) et l'envoi de la base (TOK-109) | 🟠 Medium |
| TOK-92 | Ré-héberger les images de cartes avant le déploiement (hotlink YGOPRODeck interdit) | 🟡 Livré le 2026-11-17 sur `claude/lot10-tok-92-images-5c0cd5` : 14 084 cartes, 3 tailles, 1,1 Go hors Git, 0 requête YGOPRODeck ; reste le stockage définitif (TOK-35) — `docs/journal/images-tok-92.md` | 🟠 Medium |
| TOK-93 | Contrôle de fraîcheur des tables servies dans le job du lundi | 🔜 À faire | 🟠 Medium |
| — | _13 tickets terminés (TOK-68 à 75, 77, 79, 83, 91, 113) : voir l’archive_ | | |

⚠ **Intitulé trompeur dans Linear** : TOK-25 s'appelle « Modèle séquentiel ARIMA ou LSTM ». Le modèle
réellement retenu est **70 % naïf + 30 % Ridge** (l'AR(1) a été testé puis écarté, notebook 05).

---

## TOK-94 — Refonte front « Braise vivante » (audit du 2026-11-16) — PRIORITAIRE

**Priorité sur le reste du backlog** (décision 11), y compris le moteur de combos. Audit et
proposition : `docs/audit-front/rapport.md`. Décisions : `docs/audit-front/decisions-2026-11-16.md`.
Rien n'est lancé tant que Thomas ne le décide pas (décision 12).

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-106 | Nouvelle page d'accueil d'après le prototype | 🟡 Livrée le 2026-11-16 sur `claude/tok-106-accueil-66ff33` (non fusionnée dans `main`) : Perf. 98, Access. 100, LCP mobile ≈ 1,8 s, JS 180 ko. Reste la relecture des textes par Thomas — `docs/journal/accueil-tok-106.md` | 🔴 High |
| TOK-99 | Dataviz maison en SVG (D3) + palette de données | 🟡 Livrée le 2026-11-17 sur `claude/tok-99-dataviz-923148` (non fusionnée dans `main`) : recharts supprimé, `/evolution` 190,6 ko de JavaScript (avant 274,1), Access. 100, palette `--cat-1` à `--cat-6` ≥ 5,1:1, pied source + date sur 9 vues (2 sans date servie : graphe, simulateur) — `docs/journal/dataviz-tok-99.md` | 🟠 Medium |
| TOK-100 | Qualité : SEO de partage + tests visuels Playwright | 🟡 Livrée le 2026-11-16 sur `claude/tok-100-seo-tests-409521` (non fusionnée dans `main`) : Lighthouse SEO 100 sur 12 pages, balises vérifiées par script sur 73 adresses, 36 captures (12 pages × 3 largeurs) en 45 s, bruit 0 pixel, références 3,4 Mo — `docs/tests-visuels.md`, `docs/journal/seo-tests-tok-100.md` | 🟠 Medium |
| TOK-101 | Page d'archétype + transitions de vue | 🟡 Livrée le 2026-11-17 sur `claude/tok-101-archetype-49be45` (non fusionnée dans `main`) : `/archetype/{slug}` (63 pages construites d'avance, les autres à la demande), `GET /archetypes/{slug}`, transitions de vue depuis la tier list ; LCP mobile 1,72 à 1,84 s, Access. 100, CLS 0 — `docs/journal/archetype-tok-101.md` | 🟠 Medium |
| TOK-102 | Graphe de synergies refondu (Sigma.js ou PixiJS) | 🔜 Backlog | 🟠 Medium |
| TOK-103 | Boutique regroupée par archétype avec courbes de prix | 🟡 Livrée le 2026-11-17 sur `claude/lot11-tok-103-boutique-e98c5d` (non fusionnée dans `main`) : `GET /boutique/prices` (table servie `boutique_price_history`), trous hachurés au-delà de 10 jours sans relevé, LCP mobile 1,75 à 1,79 s, Access. 100 ; reste le test avec 3 gérants (Thomas, `docs/tests-gerants-boutique.md`) — `docs/journal/boutique-tok-103.md` | 🟠 Medium |
| TOK-104 | Suivi des Web Vitals réels (suppose TOK-35) | 🔜 Backlog | 🟢 Low |
| TOK-105 | Option 3D pour le graphe, après le mois 3 | 🔜 Backlog | 🟢 Low |
| — | _4 tickets terminés (TOK-95 à 98) : voir l’archive_ | | |

- **TOK-116** (🔜 Backlog, 🟠 Medium, créé le 2026-11-17) : servir les parts OCG mensuelles par l'API pour remplacer
  les données figées de l'accueil (`lib/proof-data.ts`, décision 0041).
- Suites hors chantier : `log_predictions.py` journalise la fausse date comme `target_date` ; le notebook 10 ne
  filtre pas les archétypes déjà en TCG ; `/meta/evolution` choisit son top 15 sur un mois à petits effectifs.

---

## Lot 8 — Composants d'interaction (file du 2026-11-17, sans ticket Linear)

✅ Livré le 2026-11-17 sur `claude/lot08-boutons-ef9f72` (non fusionnée dans `main`) : source unique
`frontend/src/components/ds/control.tsx` + bloc `.ctl` de `globals.css` ; 13 fichiers migrés, `ui/button.tsx` supprimé ;
JavaScript inchangé, contraste AA sur tous les états (pire cas 4,52:1), 0 animation en mouvement réduit, 36 références
visuelles régénérées — `docs/design-system.md` §4, captures dans `docs/planning/2026-11-17/lot-08-captures/`.

---

## Lot 9 — TOK-114, Decks : index des archétypes et fiche de composition (file du 2026-11-17)

✅ Livré le 2026-11-16 sur `claude/lot09-tok-114-decks-99ff00` (non fusionnée dans `main`) : `scripts/build_archetype_profiles.py`
(3 tables servies, 4 309 + 167 + 7 303 lignes), `GET /decks` et `GET /decks/{slug}`, pages `/decks` et `/decks/[archetype]` ;
seuils de base ≥ 80 %, d'appoint ≥ 20 %, fiche dès 8 listes (13 archétypes, 292 listes sur 396) ; LCP mobile 1,75 à 1,87 s,
Accessibilité 100 ; 9 captures ajoutées, 6 modifiées — `docs/journal/decks-tok-114.md`.
Suites sans ticket : option de chemin pour `build_serving_db.py` (worktrees) ; ticket TOK-114 à créer ou à mettre à jour dans Linear.

---

## Lot 13 — Outillage (file du 2026-11-17, sans ticket Linear)

🟡 Livré le 2026-11-16 sur `claude/lot13-outillage-195837` (non fusionnée) : `.claude/settings.json`, hook `garde_fou.py` (28 cas bloqués,
24 autorisés, testés dans `check.py`), commande `/fin-de-journee`, règle d'or dans `CLAUDE.md` — `context.md` § Outillage.

---

## Lot 15 — Charte « ton et explication » (file du 2026-11-17)

🟡 Étape 1 livrée le 2026-11-17 sur `claude/lot15-charte-23027e` : `docs/charte-ton-et-explication.md`, formulaire à valider par Thomas avant l'étape 2 (composants, `/methode`).
🟡 Étape 2 livrée le 2026-11-17 sur `claude/lot15-explication-graphique-d831c8` (non fusionnée) : composants d'explication,
infobulles au toucher et au clavier, `/methode` sans formule, bandes de Wilson (Évolution, archétype, tier list), incertitude dite
sous chaque graphique ; reste la relecture du calcul de Wilson par la collaboratrice avant mise en ligne — `docs/journal/explication-graphique-lot15.md`.

---

## Lot 15a — TOK-115, diagnostic du Ban Radar TCG (file du 2026-11-17)

🟡 Livré le 2026-11-17 sur `claude/lot15a-tok-115-diagnostic-d81236` (non fusionnée) : `scripts/diagnose_ban_radar.py`,
diagnostic et formulaire dans `docs/journal/ban-radar-tcg-diagnostic.md`. Cause : poids effectifs dominés par les
exemplaires et la tendance, faibles en TCG. Poids estimés meilleurs que les actuels en TCG, pas que les staples en rang
médian : aucun `WEIGHTS` changé. Reste : formulaire à valider par Thomas (poids, rangs centiles, `bridge`, dates
d'annonce, verdict de la page Historique).

---

## Lot 16 — Réécriture des textes selon la charte (file du 2026-11-17) ✅

🟡 Première moitié livrée le 2026-11-17 sur `claude/lot16-reecriture-textes-9d97ee` (non fusionnée) : `docs/textes-avant-apres.md`
(846 textes relevés : 775 conformes, 43 à changer, 28 en attente du formulaire TOK-115), formulaire de validation en tête,
`scripts/check_copy.py` (mots interdits, branché dans `check.py` en avertissement). **Aucun texte du site modifié.** Reste :
validation par Thomas, puis application et passage du script en bloquant (`--strict`).
✅ Seconde moitié livrée le 2026-11-18 sur `claude/lot16-application-textes-8896be` (non fusionnée) : T01 à T43 et B01 à B28
appliqués selon les réponses de Thomas du 17/11 (titre neutre « Méta Yu-Gi-Oh! TCG et OCG », verdict TOK-115), `check_copy.py`
bloquant (0 occurrence), 35 captures régénérées — `docs/textes-avant-apres.md` § 0.

---

## Lot 19 — Audit de rigueur statistique (2026-11-17)

🟡 Rapport livré sur `claude/lot19-audit-rigueur-e3bee6` (non fusionnée) : 13 scores audités, aucun ne remplit les 4 critères ; 14 tickets proposés (A1-A8 en S, B1-B5, C1), formulaire à valider par Thomas — `docs/journal/audit-rigueur-statistique.md`.

---

## Suites du diagnostic TOK-115 et de l'audit de rigueur (17-18/11)

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-122 | Correctifs de l'audit A1 à A8 (A1-A4 d'abord) | 🟡 Livré le 2026-11-18 sur `claude/lot20-audit-a1-a8-cbc82f` (non fusionnée) : A1 à A8 faits, un commit chacun, critères mesurés dans `docs/journal/audit-rigueur-statistique.md` ; deux écarts à l'audit (IC du gain périmé, 20 archétypes testés et non 60) au formulaire. Reste : `build_early_signals.py` + `build_serving_db.py` sur la référence, formulaire lot 20, relecture de la collaboratrice | 🔴 High |
| TOK-121 | Collecte des dates d'annonce des banlists | 🟡 Livré le 2026-11-18 sur `claude/lot21-dates-annonce-65588d` (non fusionnée) : table `banlist_announcements` (170 listes, 20 du backtest couvertes ou justifiées), `diagnose_ban_radar.py --annonces` ; effet faible et exploratoire (OCG ≈ 5 rangs, TCG rien), Historique inchangé. Reste : lancer le script sur la base de référence, formulaire lot 21, relecture de la collaboratrice — `docs/journal/dates-annonce-banlists-tok-121.md` | 🟠 Medium |
| TOK-120 | Ban Radar : rangs par liste, régression conditionnelle, pont daté (B5) | 🟡 Livré le 2026-11-18 sur `claude/j1-tok-120-132-ban-radar-pont-d32da4` (Jalon 1, non fusionnée) : `diagnose_ban_radar_rangs.py`, `bridge_date.py` ; règle d'adoption non remplie (échec OCG à la coupure « contenu », égalité avec les staples en TCG), `WEIGHTS` inchangés ; `card_graph_metrics` périmée. Reste : formulaire lot 22, relecture de la collaboratrice — `docs/journal/ban-radar-rangs-tok-120.md` | 🟠 Medium |
| TOK-132 | B3 : score de pont et simulateur confrontés aux banlists | 🟡 Livré le 2026-11-18 sur `claude/j1-tok-120-132-ban-radar-pont-d32da4` (Jalon 1, non fusionnée) : `diagnose_pont_simulateur.py` ; un ban fait baisser ses porteurs (−3,1 points), mais le score de pont va dans le sens contraire d'« Impact » (+6,5 à part des decks égale) et les archétypes voisins du simulateur ne battent pas une liste naïve. Reste : formulaire lot 26 (renommer en « Diffusion »), relecture de la collaboratrice — `docs/journal/pont-simulateur-tok-132.md` | 🟠 Medium |
| TOK-129 | B2 : signaux précoces rejoués contre « vues seules » | 🟡 Livré le 2026-11-18 sur `claude/j1-tok-129-93-signaux-fraicheur-d1344d` (Jalon 1, non fusionnée, dépend de TOK-122) : `backtest_early_signals.py` ; critère rempli en cartes (+0,154 contre les vues, IC dates [+0,066 ; +0,252]) mais nul compté par archétype (≈ 8 épisodes) ; la force OCG sans vues désigne l'archétype qui arrive (+0,272). Reste : formulaire TOK-129 (revoir la page), relecture de la collaboratrice — `docs/journal/signaux-precoces-backtest-tok-129.md` | 🟠 Medium |
| TOK-123 | Chantiers de méthode B1 à B4 (lots 23 à 26), C1 plus tard | 🔜 Lots 23-26 ; relecture de la collaboratrice après (décision du 18/11) | 🟠 Medium |

## TOK-107 — Collaboration et stack (2026-11-16)

En parallèle de la refonte front. Une collaboratrice (l'amie data scientist de Thomas), accès direct à
`main` sans revue, dépôt qui reste public, base hébergée à terme (copie au départ), avis sur la stack.
Vigilance : jamais d'identifiants commités (dépôt public), base hébergée privée, `CLAUDE.md` à adapter.
Livrables : `docs/collaboration/`, `scripts/check.py`, `.githooks/pre-push`, `.github/workflows/verifications.yml`.

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-108 | L'inviter sur GitHub (pseudo à fournir) et dans Linear (équipe Tokoz), mettre à jour TOK-78 | 🔜 Attend son pseudo GitHub ; invitations faites par Thomas. Protection de `main` à poser (interdire force-push et suppression, sans revue) | 🔴 High |
| TOK-109 | Lui fournir une copie de la base (court terme, accès privé) | 🟡 Méthode prête (`scripts/export_db_snapshot.py`, Drive nominatif, `docs/collaboration/transmission-base.md`) ; envoi par Thomas | 🔴 High |
| — | _3 tickets terminés (TOK-110, 111, 112) : voir l’archive_ | | |

## TOK-84 — Moteur de combos, pilote Branded (réunion du 2026-11-16) — PRIORITÉ N° 1 DEPUIS LE 18/11

**Décision de Thomas (18/11)** : le moteur de combos passe en tête de la file (`docs/planning/file.md`, lots 17, 18, C1-C3) ; le reste avance en deuxième session. Décisions, jalons et règle d'arrêt : [`docs/moteur-combos/decisions-2026-11-16.md`](docs/moteur-combos/decisions-2026-11-16.md).

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-85 | Définitions formelles + schéma de données | ✅ Fait ; D3 révisée après la relecture du 17/11 — `docs/moteur-combos/definitions-et-schema.md` | 🟠 Medium |
| TOK-86 | Banc d'oracle Project Ignis en local (AGPL : jamais dans le produit, jamais fourni au LLM) | 🟡 Installation arrêtée le 2026-11-17 (cœur hors organisation officielle, `premake5` et Lua absents) ; décision de Thomas requise — `docs/moteur-combos/reponses-oracle.md` | 🟠 Medium |
| TOK-87 | Jeu de tests Branded écrit à la main (deck de tournoi réel) | ✅ 72 situations, relues par le juge le 17/11 (relecture 1) — `docs/moteur-combos/tests-branded.yaml` | 🟠 Medium |
| TOK-90 | Tranche 0 : un combo Branded de bout en bout | 🟡 Livré le 18/11 (lot C1, branche `claude/c1-tok-90-tranche-0-554a89`, non fusionnée) : `moteur_combos/regles.py`, 5 cartes formalisées, combo Aluber → Branded Fusion → Rindbrumm → Kitt rappelle Albaz ; négatifs T60 (hors timing), T04 (effet déjà utilisé), T11 (matériel manquant), T68 « non couvert » ; 10 situations exécutées dans le harnais, 77 tests pytest ; 11 décisions par défaut (`docs/planning/2026-11-18/decisions-prises.md`) | 🔴 Urgent |
| TOK-89 | Trouver un juge humain qui connaît le jeu | 🟡 Relecture 1 faite le 17/11 (joueur de tournoi, non arbitre, Google Form + entretien) : 32 points sur 34 confirmés, R22 contesté (probable malentendu), R34 complété ; D3 révisée (« entre-deux », 18/11), D1 maintenue malgré l'absence de `Lubellion` — `docs/moteur-combos/reponses-juge-2026-11-17.md`. Relecteur plus disponible : R22 levé par cohérence avec R23 ; R08, R27 (b), R34 n'ont qu'un avis (prochain relecteur ou oracle TOK-86) | 🔴 High |
| TOK-88 | Journal de chronométrage des étapes | 🟡 Ouvert — `docs/moteur-combos/chronometrage.md` (3 sessions d'agent le 2026-11-16, validation humaine non mesurée) | 🟢 Low |
| TOK-117 | Fondations du moteur (schéma, chargement des decks, harnais de tests) | 🟡 Livré le 18/11 (lot 18, fusionné dans `claude/moteur-18-11`) : `moteur_combos/`, `data/combos.db` (ignorée), harnais `python scripts/combos_harnais.py` (72 tests classés : 54 confirmés / 6 un seul avis / 12 sans point relu), 50 tests pytest, aucune règle de jeu ; 12 décisions par défaut à valider (`docs/planning/2026-11-18/decisions-prises.md`) | 🔴 Urgent |
| TOK-118 | J1 : formaliser les 37 cartes du pilote, taux d'erreur chiffré | 🟡 Formalisation livrée le 18/11 (lot C2, branche `claude/c2-j1-formalisation-a044b3`, non fusionnée) : 37 cartes `formalisee`, 57/57 effets du pilote exercés, 69/72 situations du YAML + 30 situations J1 conformes, 0 erreur trouvée. Reste pour atteindre J1 : oracle sur les 30 situations J1 et les points N01-N13 (`situations-pour-oracle.md`), relecture à l'aveugle de 20 effets tirés + 15 hors périmètre (`j1-rapport.md` § 4), formulaire C2 — `docs/moteur-combos/j1-rapport.md` | 🔴 High |
| TOK-119 | J2 : retrouver seul les combos des guides publics (échéance de la règle d'arrêt : 13/01/2027) | 🟡 Livré le 18/11 (lot C3, branche `claude/c3-j2-exploration-ff7592`, non fusionnée) : étape 0 (N09 corrigé, N01, N04), exploration bornée + stockage, 5 combos de guides ; séquences retrouvées 4 sur 5 sans cible, 5 sur 5 vers la cible, hasard 0 sur 5. **« Atteint sous réserve »**, horloge maintenue. Reste pour J2 plein : 5 combos de plus transcrits par un joueur, cible et jalons figés avant exécution, essai à 5 cartes ; formulaire C3 — `docs/moteur-combos/j2-rapport.md` | 🔴 High |

- ⚠ À arbitrer avec le data scientist : `views_week` des cartes existantes n'est jamais rafraîchi
  (1 088 valeurs sur 14 084 égales à celles de l'API du jour), alors que les cartes nouvelles
  arrivent avec une valeur du jour. Le signal précoce (notebook 11) compare donc des instantanés de
  dates différentes. Ce défaut existait avant ; l'ajout des cartes nouvelles le rend visible.
- ⚠ `cards.archetype` ne suit pas les règles du jeu (`Fallen of Albaz` y est « Dogmatika », ce qu'il
  n'est pas) : le moteur calcule l'appartenance depuis le nom et les clauses « always treated as ».
- TOK-89 fait (relecture 1 du 17/11) ; une seconde relecture par un arbitre reste souhaitable pour R08, R27, R34.

Jalons : **J1** 100 % des cartes Branded formalisées avec un taux d'erreur chiffré · **J2** le moteur
retrouve seul les combos des guides publics · **J3** il en trouve un qu'aucun guide ne cite. Règle
d'arrêt : J2 non atteint en 8 semaines ou J3 vide → réévaluer.

---

## Idées & exploration

| TOK | Item | Priorité |
|-----|------|----------|
| TOK-36 | Alerte email/Discord quand un signal précoce est détecté | 🟠 Medium |
| TOK-37 | Affiliation Cardmarket intégrée au front | 🟢 Low |

---

## Site public — Brainstorming 2026-08-05

Issu de `_bmad-output/brainstorming/brainstorming-session-2026-08-05-1.md` (28 idées, technique Brain Writing Round Robin). Idées non "Later" converties en tickets Linear.

### TOK-46 — Phase A : UX Fondations (site présentable)

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-52 | Mode Joueur / Mode Boutique (toggle UX) | 🔜 Next | 🟠 Medium |

### Phase B : Backend (données réelles) — rattaché à TOK-43

| TOK | Item | Priorité |
|-----|------|----------|
| TOK-67 | API publique freemium + API key boutique premium | 🟠 Medium |

### TOK-47 — Phase C : Data & Features avancées (différenciation)

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-55 | Ban Predictor vs History — track record public | 🟡 Livré le 2026-11-17 sur `claude/lot12-tok-55-ban-historique-206ce4` (non fusionnée) : onglet `/ban?tab=historique`, 20 listes, chiffres vérifiés par le data scientist (0 écart avec `--backtest`) ; reste `build_ban_history.py` sur la base de référence, les dates d'annonce, l'ajout à `refresh_all.py` — `docs/journal/ban-historique-tok-55.md` | 🟠 Medium |
| TOK-56 | Comparateur archétypes côte à côte | 🔜 À faire | 🟠 Medium |
| TOK-57 | Watchlist personnelle | 🔜 À faire | 🟢 Low |
| TOK-58 | Deck Builder + meta score temps réel | 🔜 À faire | 🟠 Medium |
| TOK-59 | Combo Visualizer intégré (graphe orienté) | 🔜 À faire | 🟠 Medium |
| TOK-60 | Deck vs Meta — analyse comparative vs top decklists | 🔜 À faire | 🟠 Medium |
| TOK-61 | Deck Score radar chart | 🔜 À faire | 🟢 Low |
| TOK-62 | Import YDKe / code deck | 🔜 À faire | 🟢 Low |
| TOK-63 | Suggestions "cartes qui amélioreraient ton deck" | 🔜 À faire | 🟢 Low |
| TOK-64 | Partage de deck → lien unique avec score + combos | 🔜 À faire | 🟢 Low |
| TOK-65 | Referral boutique — commission sur carte vendue | 🔜 À faire | 🟠 Medium |
| TOK-66 | Boutique partenaire — listing premium | 🔜 À faire | 🟢 Low |

**TOK-55** : page publique livrée (lot 12) ; en TCG, la base « staples les plus jouées » bat le score en rang médian
sur 7 listes sur 10, c'est affiché.

Idées "Later" (non converties) : Dark/Light mode, Meta Snapshot hebdo, Historique de decks, Social (profils créateurs, Deck Feed, rating, tournoi mensuel), Marketplace de decks guides.

---

Idée non créée : afficher un méta Genesys (décision produit).
Suites de TOK-113 sans ticket : rafraîchir `cards` dans la chaîne (`views_week` figé au 13 juin).
✅ Fait le 2026-11-17 (branche `claude/seuil-boutique-b07cfa`, non fusionnée) : libellé Fort / Modéré / Faible **absolu**
(rang de l'archétype parmi les 89 archétypes OCG, seuils provisoires non validés) servi par `GET /boutique/signals`
(`signal_label`, `archetype_rank`, `label_rule`) — `docs/journal/seuils-signal-boutique.md`. La fenêtre de sortie TCG est déjà servie et affichée.

**Fin de journée du 2026-11-16 :** TOK-95 à 98, TOK-107 (sauf invitation et envoi de la base), TOK-113 et la préparation
du moteur de combos (TOK-85, 87) sont dans `main`, poussés. Reste à Thomas : pseudo GitHub (TOK-108), envoi de la base
(TOK-109), protection de `main`, contact d'un juge (TOK-89). Prochaine étape technique : TOK-106.

**File de nuit du 16-17/11 :** lots 1 à 19 fusionnés dans `claude/front-nuit-17-11`, elle-même fusionnée dans `main` le 17/11
(`bd22ae8`, rien poussé) ; statuts « 🟡 Livré … sur `claude/lotNN-…` (non fusionnée) » ci-dessus = présents dans `main`. Linear synchronisé le 17/11 :
TOK-55, 92, 99, 100, 101, 103, 106, 114, 115 en « In Review » ; TOK-35 et TOK-86 en « In Progress ». Décisions en attente de Thomas :
`context.md` § « À faire » et `docs/planning/etat.md`.

*Dernière mise à jour : 2026-11-17 (fin de la file de nuit)*

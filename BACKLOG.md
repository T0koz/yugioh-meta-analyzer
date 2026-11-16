# Backlog — Yu-Gi-Oh! Meta Analyzer

Statuts : `✅ Done` · `🔜 À faire`
Priorités : `🔴 High` · `🟠 Medium` · `🟢 Low`

Suivi détaillé sur [Linear](https://linear.app/tokoz).

---

## Phase 1 — Données cartes

| TOK | Item | Statut |
|-----|------|--------|
| TOK-5 | `views_week` comme signal précoce d'entrée en méta | ✅ Done |
| TOK-6 | NLP sur texte des effets `desc` (synergies textuelles) | ✅ Done |
| TOK-7 | Endpoint `/archetypes.php` pour matching officiel | ✅ Done |
| TOK-8 | Historique banlist complet (scraping Yugipedia) | ✅ Done |
| TOK-9 | Prix dans le temps — snapshot quotidien toutes cartes | ✅ Done |
| TOK-10 | Images des cartes (`image_url`, `image_url_small` dans `cards`) | ✅ Done |

---

## Phase 2 — Decklists + co-occurrence + graphe

| TOK | Item | Statut |
|-----|------|--------|
| TOK-11 | Co-occurrence sur fenêtre glissante 90j | ✅ Done |
| TOK-12 | Tier list yugiohmeta.com (`/api/v1/tier-list`) | ✅ Done |
| TOK-13 | Pondération co-occurrence par placement (`1/placement`) | ✅ Done |
| TOK-14 | Extra deck analysé séparément (Jaccard + profil archetype) | ✅ Done |
| TOK-15 | Clustering des decks par style (K-Means k=4, silhouette=0.171) | ✅ Done |
| TOK-16 | Betweenness centrality sur le graphe | ✅ Done |
| TOK-17 | Nommage automatique des 63 communautés du graphe | ✅ Done |
| TOK-18 | Co-occurrence par trimestre (10 quarters) | ✅ Done |
| TOK-19 | Filtrer sur YCS / Nationals / WCQ uniquement | ✅ Done |
| TOK-20 | Segmentation OCG vs TCG | ✅ Done |

---

## Phase 3 — Score méta + modèle prédictif

| TOK | Item | Statut |
|-----|------|--------|
| TOK-21 | Features lag temporelles (`t-1`, `t-2`, `t-3`, delta, roll_mean) | ✅ Done |
| TOK-22 | Banlist historique comme feature temporelle | ✅ Done |
| TOK-23 | `trend_ratio_monthly` par fenêtre mensuelle glissante | ✅ Done |
| TOK-24 | Feature `months_since_debut` (âge de l'archetype) | ✅ Done |
| TOK-25 | Modèle AR(1) par archetype (AutoReg statsmodels) | ✅ Done |

---

## Phase 4 — Dashboard + NLP

| TOK | Item | Statut |
|-----|------|--------|
| TOK-26 | Appliquer la blacklist NLP dans notebook 08 | ✅ Done |
| TOK-27 | Tester NLP sur vraies vidéos combo guide | ✅ Done |
| TOK-28 | Pipeline NLP multi-vidéos / chaîne YouTube entière | ✅ Done |

---

## Signal boutiques

| TOK | Item | Statut |
|-----|------|--------|
| TOK-29 | Historique prix Cardmarket comme signal d'achat | ✅ Done |
| TOK-30 | Dashboard boutique dédié (B2B) | ✅ Done |

---

## Phase 5 — Front-end & API 🏗️ En cours

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-31 | Backend FastAPI — endpoints /meta, /boutique, /graph, /cards | ✅ Done | 🔴 High |
| TOK-32 | Front Next.js — toutes les pages | ✅ Done | 🔴 High |
| TOK-33 | Front — graphe synergies interactif (vis-network branché API) | ✅ Done | 🟠 Medium |
| TOK-34 | Front — simulateur de ban (branché API) | ✅ Done | 🟠 Medium |
| TOK-35 | Déploiement (Vercel front + back) | 🟡 Base de service prête | 🔴 High |

**TOK-35 — état :** `scripts/build_serving_db.py` produit `data/serving.db`
(9,4 Mo contre 236 Mo), le backend la lit via `YGO_DB_PATH`. Plus besoin de
volume persistant. Reste à trancher l'hébergement : à cette taille, l'API peut
sans doute tourner en serverless à côté du front, ce qui rendrait Railway inutile.

**Pages livrées** (toutes branchées sur l'API réelle, design system Ember depuis le 2026-10-31) :
- `/` — Home en bento : signal boutique, top Ban Radar, plus forte hausse prévue, graphe, aperçu simulateur
- `/tier-list` — Liste dense : hero + stats, filtres (Tous / T0–T3 / Rogue / En hausse), barre relative au max
- `/evolution` — Line chart mensuel (recharts), 4 séries max, accent sur la première
- `/predictions` — Tableau actuel vs prévu + delta
- `/boutique` — Signaux d'achat avec statut banlist TCG
- `/early-signals` — Liste dense : score + vues/semaine
- `/graph` — vis-network interactif, accent sur l'archétype filtré
- `/ban` — Ban Center : onglets Radar (score + barre empilée des critères), Cartes à impact, Simulateur

---

## Fiabilité des données & validité statistique — point du 2026-11-16

Issu du point projet du 2026-11-16 (voir `docs/ONBOARDING.md` §4-5 pour le détail). Ordre de
traitement conseillé : TOK-70 → TOK-72 → TOK-69 → TOK-74 / TOK-73.

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-68 | Fix doublons `deck_cards` + purge de la base | ✅ Done | 🔴 High |
| TOK-70 | Rafraîchir les decklists de tournoi (figées au 9 août) | ✅ Done (2026-11-16) — `refresh_decks.py` + job launchd lundi 8h30 | 🔴 High |
| TOK-69 | Pipeline de rafraîchissement des tables dérivées (`meta_scores` gelé en 2026-06) | ✅ Done — `scripts/refresh_all.py` | 🔴 High |
| TOK-71 | Snapshot quotidien des prix fiable (launchd, `scripts/launchd/`) | ✅ Done | 🔴 High |
| TOK-72 | Légalité des decks à la date du tournoi — étape 2 (rebrancher les consommateurs) | ✅ Done — recalcul + backtest faits | 🔴 High |
| TOK-73 | Évaluer honnêtement la prédiction + robustesse du signal OCG→TCG | ✅ Done — `docs/evaluation-prediction.md` | 🔴 High |
| TOK-74 | Vérifier l'entrée de Kewl Tune en TCG (prévue octobre 2026) | ✅ Done — verdict défavorable, `docs/tok-74-kewl-tune.md` | 🔴 High |
| TOK-75 | Script de validation du `prediction_log` (débloque TOK-55) | ✅ Done — `scripts/validate_predictions.py` | 🟠 Medium |
| TOK-76 | Risque : dépendance à l'API non officielle yugiohmeta | 🟡 Monitoring fait (`data/fetch_health.jsonl`) ; risque structurel reste | 🟠 Medium |
| TOK-77 | Mesurer la pollution Genesys dans le méta TCG | ✅ Done — `docs/tok-77-genesys.md` (27-44 % des decks TCG depuis juillet) | 🟠 Medium |
| TOK-78 | Onboarding d'une data scientist (`docs/ONBOARDING.md` fait, accès à décider) | 🟡 Partiel | 🟠 Medium |
| TOK-79 | Agent `coordinateur` (Rapport + Dispatch) + point hebdo `yugioh-point-hebdo` | ✅ Done | 🟠 Medium |
| TOK-83 | Perf : `GET /ban-radar` 10-20 s (jointure `REPLACE` sans index) | ✅ Done — index d'expression `idx_cards_name_clean` + `= +col` dans les routeurs (~30 ms) ; `serving.db` reconstruite | 🟠 Medium |
| TOK-91 | Tier list maison : recalculer depuis nos données (`meta_tier_list` figée au 17 juin, endpoint yugiohmeta 404) | 🔜 À faire | 🔴 High |
| TOK-92 | Ré-héberger les images de cartes avant le déploiement (hotlink YGOPRODeck interdit) | 🔜 À faire | 🟠 Medium |
| TOK-93 | Contrôle de fraîcheur des tables servies dans le job du lundi | 🔜 À faire | 🟠 Medium |

⚠ **Intitulé trompeur dans Linear** : TOK-25 s'appelle « Modèle séquentiel ARIMA ou LSTM ». Le modèle
réellement retenu est **70 % naïf + 30 % Ridge** (l'AR(1) a été testé puis écarté, notebook 05).

---

## TOK-94 — Refonte front « Braise vivante » (audit du 2026-11-16) — PRIORITAIRE

**Priorité sur le reste du backlog** (décision 11), y compris le moteur de combos. Audit et
proposition : `docs/audit-front/rapport.md`. Décisions : `docs/audit-front/decisions-2026-11-16.md`.
Rien n'est lancé tant que Thomas ne le décide pas (décision 12).

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-95 | Préalables bloquants : correctif TOK-83 dans `main` + erreur 500 de `/early-signals` | ✅ Done (2026-11-16) — branche fusionnée (`/ban-radar` 7 s → 0,05 s), `archetype` nullable, test de fumée `backend/tests` | 🔴 Urgent |
| TOK-96 | Jour 1 : gains rapides sans décision de design (débloqué : TOK-95 fait) | 🔜 À faire | 🔴 High |
| TOK-97 | Crédibilité des chiffres affichés (Elfnote, Ash Blossom, date de la tier list, écart 3 ou 4 mois) | 🔜 À faire | 🔴 High |
| TOK-98 | Semaine 1 : cartes, mouvement, typographie | 🔜 À faire | 🔴 High |
| TOK-106 | Nouvelle page d'accueil d'après le prototype (bloqué par TOK-95 et TOK-97) | 🔜 Backlog | 🔴 High |
| TOK-99 | Dataviz maison en SVG (D3) + palette de données | 🔜 Backlog | 🟠 Medium |
| TOK-100 | Qualité : SEO de partage + tests visuels Playwright | 🔜 Backlog | 🟠 Medium |
| TOK-101 | Page d'archétype + transitions de vue | 🔜 Backlog | 🟠 Medium |
| TOK-102 | Graphe de synergies refondu (Sigma.js ou PixiJS) | 🔜 Backlog | 🟠 Medium |
| TOK-103 | Boutique regroupée par archétype avec courbes de prix | 🔜 Backlog | 🟠 Medium |
| TOK-104 | Suivi des Web Vitals réels (suppose TOK-35) | 🔜 Backlog | 🟢 Low |
| TOK-105 | Option 3D pour le graphe, après le mois 3 | 🔜 Backlog | 🟢 Low |

TOK-83 et la partie front de TOK-82 sont dans `main` depuis la fusion de `claude/front-vitrine-06112d` (TOK-95, 2026-11-16).

---

## TOK-107 — Collaboration et stack (2026-11-16)

En parallèle de la refonte front. Une collaboratrice (l'amie data scientist de Thomas), accès direct à
`main` sans revue, dépôt qui reste public, base hébergée à terme (copie au départ), avis sur la stack.
Vigilance : jamais d'identifiants commités (dépôt public), base hébergée privée, `CLAUDE.md` à adapter.

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-108 | L'inviter sur GitHub (pseudo à fournir) et mettre à jour TOK-78 | 🔜 À faire | 🔴 High |
| TOK-109 | Lui fournir une copie de la base (court terme, accès privé) | 🔜 À faire | 🔴 High |
| TOK-112 | Règles de travail à deux (`CLAUDE.md`, vérifications avant push, `ONBOARDING.md`) | 🔜 À faire | 🟠 Medium |
| TOK-110 | Investiguer une base de données hébergée (note de comparaison, pas de migration) | 🔜 Backlog | 🟠 Medium |
| TOK-111 | Avis sur la stack pour travailler à deux (note, pas de changement) | 🔜 Backlog | 🟠 Medium |

---

## TOK-84 — Moteur de combos, pilote Branded (réunion du 2026-11-16)

Projet distinct du produit d'analyse de méta, mené en parallèle (le nettoyage du backlog reste
prioritaire). Décisions, jalons et règle d'arrêt : [`docs/moteur-combos/decisions-2026-11-16.md`](docs/moteur-combos/decisions-2026-11-16.md).

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-85 | Définitions formelles (état, action, équivalence, arrêt) + schéma de données | 🔜 Backlog | 🟠 Medium |
| TOK-86 | Banc d'oracle Project Ignis en local (AGPL : jamais dans le produit, jamais fourni au LLM) | 🔜 Backlog | 🟠 Medium |
| TOK-87 | Jeu de tests Branded écrit à la main (deck de tournoi réel, ~50 situations) | 🔜 Backlog | 🟠 Medium |
| TOK-90 | Tranche 0 : un combo Branded de bout en bout (bloqué par TOK-85 et TOK-87) | 🔜 Backlog | 🟠 Medium |
| TOK-89 | Trouver un juge humain qui connaît le jeu | 🔜 Backlog | 🟠 Medium |
| TOK-88 | Journal de chronométrage des étapes | 🔜 Backlog | 🟢 Low |

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
| TOK-48 | Smart Search + autocomplete + card preview au hover | ✅ Done | 🟠 Medium |
| TOK-49 | Card chip cliquable avec visuel partout sur le site | ✅ Done | 🟠 Medium |
| TOK-50 | Archetype thumbnails (image emblématique de l'archétype) | ✅ Done | 🟠 Medium |
| TOK-51 | Tooltip ⓘ "Comment c'est calculé" sur chaque stat | ✅ Done | 🟠 Medium |
| TOK-52 | Mode Joueur / Mode Boutique (toggle UX) | 🔜 Next | 🟠 Medium |

### Phase B : Backend (données réelles) — rattaché à TOK-43

| TOK | Item | Priorité |
|-----|------|----------|
| TOK-67 | API publique freemium + API key boutique premium | 🟠 Medium |

### TOK-47 — Phase C : Data & Features avancées (différenciation)

| TOK | Item | Statut | Priorité |
|-----|------|--------|----------|
| TOK-53 | Ban Radar — score de risque de ban (scoring multi-critères) | ✅ Done | 🟠 Medium |
| TOK-54 | Top cartes à fort impact si bannies (bridge score classé) | ✅ Done | 🟠 Medium |
| TOK-55 | Ban Predictor vs History — track record public | 🟡 Débloqué (10 points TCG / 10 OCG au backtest, `validate_predictions.py`) | 🟠 Medium |
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

**TOK-53 livré** : table `ban_radar` (`scripts/build_ban_radar.py`), endpoint
`GET /api/v1/ban-radar`, page `/ban-radar` avec filtre Tout / Pièces d'archétype
/ Staples génériques. Score de risque 0-100 sur 6 critères pondérés, le décisif
étant le nombre moyen d'exemplaires joués — pas l'omniprésence.

Backtest (`--backtest`, listes dérivées de `banlist_history`, plus codées en dur) :

| Liste | Rang médian | Hasard | Top-25% |
|---|---|---|---|
| TCG 2026-05-18 | **127**/923 | 462 | 8/11 |
| OCG 2026-07-01 | **31**/1 089 | 544 | 7/11 |
| OCG 2026-04-01 *(416 decks, écartée)* | 285/556 | 278 | 2/7 |

Le modèle transfère à l'OCG sans y avoir été calibré, et y fait mieux qu'en TCG.
En dessous de ~600 decks dans la fenêtre, il ne vaut rien — seuil à ne pas
baisser pour gagner des listes. Détail dans le docstring du script.

**TOK-55 débloqué** par ces deux points de mesure : reste à construire la page
publique. `scripts/fetch_banlist_history.py` (TCG + OCG) en est le socle.

Idées "Later" (non converties) : Dark/Light mode, Meta Snapshot hebdo, Historique de decks, Social (profils créateurs, Deck Feed, rating, tournoi mensuel), Marketplace de decks guides.

---

**Tickets créés le 2026-11-16 :** TOK-80 ✅ Done (`meta_scores` TCG pur + `meta_scores_ocg`) ; TOK-81 ✅ Done (échelle de
`price_opp`) ; TOK-82 ✅ Done (fenêtres du notebook 11 + chiffres et textes du front, `site-facts.ts`).
Idée non créée : afficher un méta Genesys (décision produit).

*Dernière mise à jour : 2026-11-16*

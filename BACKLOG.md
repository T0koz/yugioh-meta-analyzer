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
| TOK-32 | Front Next.js — toutes les pages (mock data) | ✅ Done | 🔴 High |
| TOK-33 | Front — graphe synergies interactif (vis-network branché API) | ✅ Done | 🟠 Medium |
| TOK-34 | Front — simulateur de ban (branché API) | 🟡 Partiel | 🟠 Medium |
| TOK-35 | Déploiement (Vercel front + Railway back) | 🔜 Next | 🔴 High |

**Pages livrées (mock data) :**
- `/tier-list` — Tier List avec barres de score et trends
- `/evolution` — Line chart interactif méta mensuel (recharts)
- `/predictions` — Tableau current vs prédit + delta
- `/boutique` — Signaux d'achat avec badges banlist TCG
- `/early-signals` — Score rings + views/semaine
- `/graph` — Placeholder SVG (full vis-network = TOK-33 post-API)
- `/ban-simulator` — Formulaire + bridge score + archetypes impactés

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

| TOK | Item | Priorité |
|-----|------|----------|
| TOK-53 | Ban Radar — probabilité d'être banni (scoring multi-critères) | 🟠 Medium |
| TOK-54 | Top cartes à fort impact si bannies (bridge score classé) | 🟠 Medium |
| TOK-55 | Ban Predictor vs History — track record public | 🟠 Medium |
| TOK-56 | Comparateur archétypes côte à côte | 🟠 Medium |
| TOK-57 | Watchlist personnelle | 🟢 Low |
| TOK-58 | Deck Builder + meta score temps réel | 🟠 Medium |
| TOK-59 | Combo Visualizer intégré (graphe orienté) | 🟠 Medium |
| TOK-60 | Deck vs Meta — analyse comparative vs top decklists | 🟠 Medium |
| TOK-61 | Deck Score radar chart | 🟢 Low |
| TOK-62 | Import YDKe / code deck | 🟢 Low |
| TOK-63 | Suggestions "cartes qui amélioreraient ton deck" | 🟢 Low |
| TOK-64 | Partage de deck → lien unique avec score + combos | 🟢 Low |
| TOK-65 | Referral boutique — commission sur carte vendue | 🟠 Medium |
| TOK-66 | Boutique partenaire — listing premium | 🟢 Low |

Idées "Later" (non converties) : Dark/Light mode, Meta Snapshot hebdo, Historique de decks, Social (profils créateurs, Deck Feed, rating, tournoi mensuel), Marketplace de decks guides.

---

*Dernière mise à jour : 2026-08-05*

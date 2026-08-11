---
stepsCompleted: [1, 2, 3, 4]
session_topic: "Site web public YGO Meta Analyzer — front-end + back-end"
session_goals: "Générer un max d'idées sans filtre, trier, puis convertir en TOKs"
selected_approach: "user-selected"
techniques_used: ["Brain Writing Round Robin"]
ideas_generated: 28
session_active: false
workflow_completed: true
date: 2026-08-05
---

# Brainstorming Session — 2026-08-05

**Topic:** Site web public Yu-Gi-Oh! Meta Analyzer — front-end + back-end
**Technique:** Brain Writing Round Robin
**Total idées :** 28

---

## Thème 1 — UX & Interface (Phase A)

| # | Idée | Priorité |
|---|------|----------|
| 1 | Smart Search + autocomplete + card preview au hover | Phase A |
| 2 | Card chip cliquable avec visuel partout sur le site | Phase A |
| 3 | Archetype thumbnails (image emblématique de l'archétype) | Phase A |
| 4 | Tooltip ⓘ "Comment c'est calculé" sur chaque stat | Phase A |
| 5 | Mode Joueur / Mode Boutique (toggle UX) | Phase A |
| 6 | Dark / Light mode | Later |

## Thème 2 — Data & Analyse (Phase C)

| # | Idée | Priorité |
|---|------|----------|
| 7 | Ban Radar — probabilité d'être banni (scoring multi-critères) | Phase C |
| 8 | Top cartes à fort impact si bannies (bridge score classé) | Phase C |
| 9 | Ban Predictor vs History — track record public | Phase C |
| 10 | Comparateur archétypes côte à côte | Phase C |
| 11 | Watchlist personnelle | Phase C |
| 12 | Meta Snapshot hebdomadaire auto-généré | Later |

## Thème 3 — Deck Builder (Phase C)

| # | Idée | Priorité |
|---|------|----------|
| 13 | Deck Builder + meta score temps réel | Phase C |
| 14 | Combo Visualizer intégré (graphe orienté) | Phase C |
| 15 | Deck vs Meta — analyse comparative vs top decklists | Phase C |
| 16 | Deck Score radar chart | Phase C |
| 17 | Import YDKe / code deck | Phase C |
| 18 | Suggestions "cartes qui amélioreraient ton deck" | Phase C |
| 19 | Partage de deck → lien unique avec score + combos | Phase C |
| 20 | Historique de decks + évolution du score | Later |

## Thème 4 — Social & Créateurs (Later)

| # | Idée | Priorité |
|---|------|----------|
| 21 | Profils créateurs avec decks + stats publiques | Later |
| 22 | Deck Feed communautaire | Later |
| 23 | Rating + commentaires sur les decks | Later |
| 24 | Tournoi mensuel "Best Build" | Later |

## Thème 5 — Monétisation & B2B (Phase B/C)

| # | Idée | Priorité |
|---|------|----------|
| 25 | Referral boutique — commission sur carte vendue | Phase C |
| 26 | Boutique partenaire — listing premium | Phase C |
| 27 | Marketplace de decks guides | Later |
| 28 | API publique freemium + API key boutique premium | Phase B |

---

## Roadmap décidée

**Phase A — UX Fondations** *(site présentable)*
Archetype thumbnails, card chips visuels, smart search + autocomplete, tooltips stats, mode joueur/boutique

**Phase B — Backend** *(données réelles)*
FastAPI scaffolding + endpoints, branchement pages, déploiement Railway + Vercel, API freemium

**Phase C — Data & Features** *(différenciation)*
Ban Radar, Deck Builder + Combo Visualizer, Social, Referral boutique

**Segmentation confirmée :**
- Mobile = B2C (joueur en tournoi, consultatif, gratuit/freemium)
- Desktop = B2B (boutique, analyse approfondie, payant)

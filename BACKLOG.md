# Backlog — Yu-Gi-Oh! Meta Analyzer

Statuts : `🟡 In Progress` · `✅ Done` · `❌ Abandonné`
Priorités : `🔴 High` · `🟠 Medium` · `🟢 Low` · `⚪ Sans priorité`

---

## Phase 1 — Données cartes (YGOPRODeck)

| ID | Item | Statut | Priorité | Notes |
|----|------|--------|----------|-------|
| P1-A | `views_week` comme signal précoce d'entrée en méta | | 🔴 High | Déjà en DB, jamais utilisé — quick win |
| P1-B | NLP sur texte des effets `desc` pour synergies textuelles | | 🔴 High | Notre notebook 07 prévu |
| P1-F | Endpoint `/archetypes.php` pour matching officiel des archetypes | | 🔴 High | Nommage plus propre |
| P1-C | Historique de banlist complet (scraping wiki) | | 🟠 Medium | Statut actuel seulement aujourd'hui |
| P1-D | Prix dans le temps — Cardmarket / TCGPlayer history | | 🟠 Medium | Snapshot statique aujourd'hui |
| P1-E | Images des cartes (URLs déjà dans l'API) | | 🟢 Low | Utile pour le front Phase 5 |

---

## Phase 2 — Decklists + co-occurrence + graphe

| ID | Item | Statut | Priorité | Notes |
|----|------|--------|----------|-------|
| P2-G | Intégrer les decklists OCG (7 322 déjà en DB) | | 🔴 High | Signal 3-6 mois d'avance sur TCG — valider corrélation OCG→TCG d'abord |
| P2-H | Co-occurrence sur fenêtre glissante 90j | | 🔴 High | Tout le corpus traité à égalité aujourd'hui |
| P2-Q | Récupérer la tier list yugiohmeta.com (`/api/v1/tier-list`) | | 🔴 High | À confirmer via Playwright |
| P2-I | Pondération co-occurrence par placement (`1/placement`) | | 🟠 Medium | Un Top 1 doit peser plus qu'un Top 50 |
| P2-J | Analyser l'extra deck séparément | | 🟠 Medium | Révèle les win conditions / boss monsters |
| P2-K | Clustering des decks par style de jeu (Combo / Control / Midrange / OTK) | | 🟠 Medium | |
| P2-L | Betweenness centrality sur le graphe | | 🟢 Low | Identifie les cartes pont entre archetypes |
| P2-M | Nommage automatique des 46 communautés du graphe | | 🟢 Low | Aujourd'hui nommées à la main |
| P2-N | Évolution du graphe par trimestre | | 🟢 Low | Voir quand un archetype monte ou tombe |
| P2-O | Filtrer sur `tournament_type` (YCS / Nationals uniquement) | | 🟢 Low | Signal haut niveau plus pur |
| P2-P | Segmentation géographique (NA vs EU) | | 🟢 Low | Métas régionales différentes |

---

## Phase 3 — Score méta + modèle prédictif

| ID | Item | Statut | Priorité | Notes |
|----|------|--------|----------|-------|
| P3-R | Features lag temporelles (`meta_score_t-1`, `t-2`, `t-3`) | | 🔴 High | Fix principal du R²≈-37 |
| P3-V | Banlist historique encodée comme feature temporelle | | 🔴 High | Dépend de P1-C |
| P3-S | trend_ratio par fenêtre mensuelle glissante | | 🟠 Medium | Global aujourd'hui = bruit |
| P3-T | Feature `months_since_debut` (âge de l'archetype) | | 🟠 Medium | |
| P3-U | Modèle séquentiel ARIMA ou LSTM par archetype | | 🟠 Medium | Vs régression cross-sectionnelle actuelle |

---

## Phase 4 — Dashboard + NLP combos

| ID | Item | Statut | Priorité | Notes |
|----|------|--------|----------|-------|
| P4-W | Appliquer la blacklist NLP (NEXT, Return, Fine...) | | 🔴 High | Dans notebook 08 cell 2 |
| P4-X | Tester NLP sur vraies vidéos combo guide | | 🔴 High | Type "Branded combo guide 2026" |
| P4-Y | Pipeline NLP multi-vidéos / chaîne YouTube entière | | 🟢 Low | Passer d'une vidéo test à toute une chaîne |

---

## Signal boutiques

| ID | Item | Statut | Priorité | Notes |
|----|------|--------|----------|-------|
| SB-Z | Croiser OCG + views_week → score d'alerte précoce boutiques | | 🔴 High | Dépend validation corrélation P2-G |
| SB-AA | Intégrer historique prix Cardmarket comme signal d'achat | | 🟠 Medium | Dépend de P1-D |
| SB-AB | Dashboard boutique dédié (différent du dashboard joueur) | | 🟢 Low | Cible B2B 150€/mois |

---

## Phase 5 — MVP Front-end + API

| ID | Item | Statut | Priorité | Notes |
|----|------|--------|----------|-------|
| P5-AC | Définir les endpoints API (FastAPI) | | ⚪ Sans priorité | À faire après nettoyage backlog |
| P5-AD | Front React — tier list dynamique | | ⚪ Sans priorité | |
| P5-AE | Front React — graphe synergies interactif | | ⚪ Sans priorité | |
| P5-AF | Front React — simulateur de ban | | ⚪ Sans priorité | |
| P5-AG | Déploiement (Vercel front + Railway/Render back) | | ⚪ Sans priorité | |

---

## Idées & exploration

| ID | Item | Statut | Priorité | Notes |
|----|------|--------|----------|-------|
| IDEA-3 | Alerte email/Discord quand un signal précoce détecté | | ⚪ Sans priorité | Feature clé boutiques |
| IDEA-4 | Affiliation Cardmarket intégrée au front | | ⚪ Sans priorité | Revenu passif dès le MVP |

---

*Dernière mise à jour : juin 2026*

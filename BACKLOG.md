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

## Phase 5 — Front-end & API 🔜

| TOK | Item | Priorité |
|-----|------|----------|
| TOK-31 | Définir les endpoints API (FastAPI) | 🔴 High |
| TOK-32 | Front React — tier list dynamique | 🔴 High |
| TOK-33 | Front React — graphe synergies interactif | 🟠 Medium |
| TOK-34 | Front React — simulateur de ban | 🟠 Medium |
| TOK-35 | Déploiement (Vercel front + Railway/Render back) | 🔴 High |

---

## Idées & exploration

| TOK | Item | Priorité |
|-----|------|----------|
| TOK-36 | Alerte email/Discord quand un signal précoce est détecté | 🟠 Medium |
| TOK-37 | Affiliation Cardmarket intégrée au front | 🟢 Low |

---

*Dernière mise à jour : 2026-06-19*

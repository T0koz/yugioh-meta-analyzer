# 0051 — Lots 4 et 5 : périmètre des pages, du SEO et des captures

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Lots 4 et 5, par défaut ; validée par Thomas le 2026-11-17 (revue du matin)
- Tickets : TOK-101, TOK-100

## Contexte
Registre des décisions de moindre portée prises par défaut pendant ce lot. Chaque ligne est une décision, rangée ici pour ne pas multiplier les notes d'une ligne.

## Options
- Pour chaque ligne, voir la source (question et alternatives).

## Décision

  - Archétypes à signal boutique absents de la tier list → **ils ont une page (signal, part OCG, 0 deck TCG), ouverte depuis `/boutique`** (le brief demande le signal « si présent »)
  - Étendue des transitions de vue → **tier list ↔ page d'archétype seulement** (le plus prudent, drapeau expérimental)
  - Prédiction du mois suivant sur la page d'archétype → **non affichée** (`meta_predictions` porte des `data_month` différents selon l'archétype ; à trancher avec le data scientist)
  - Poids des références visuelles (12,4 Mo en PNG) → **WebP sans perte : 3,4 Mo, commitées** (mêmes pixels, 72 % de moins)
  - Intégration à `check.py` → **option `--visuel` ; rappel non bloquant quand `frontend/src/` change** (45 s et build dépendant du réseau)
  - Graphe de synergies non déterministe → **canvas masqué dans la capture** (fixer la graine toucherait au composant (TOK-102))
  - Chiffres dans les images de partage → **accueil et archétypes seulement, avec période et source** (lecture prudente de la consigne ; un aperçu reste en cache plusieurs jours)
  - Polices des images : Satori ne lit pas le WOFF2 → **copies WOFF (OFL) dans `src/assets/og-fonts/` (76 ko)** (typographie du design system sans dépendance ; licence compatible)
  - Périmètre du sitemap → **tier list courante + signaux boutique (63 pages)** (aucun endpoint ne liste les 231 archétypes)
  - Adresse canonique des onglets de `/ban` → **une par onglet, toutes dans le sitemap** (trois contenus distincts ; une seule image de partage par route)
  - Déploiements d'aperçu Vercel → **`noindex` et `robots.txt` fermé quand `VERCEL_ENV=preview`** (évite l'indexation d'un aperçu)

## Raison
Une raison est donnée entre parenthèses pour chaque ligne.

## Conséquences
À relire par Thomas ligne par ligne ; chacune est réversible sauf mention contraire dans la source.

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lots 4 et 5)

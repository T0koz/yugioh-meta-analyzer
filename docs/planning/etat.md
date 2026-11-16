# État de la file

| # | Lot | Statut | Modèle utilisé | Note |
|---|---|---|---|---|
| 1-5 | Sprint 1 | ✅ fusionnés dans `claude/front-nuit-17-11` (dernier commit `d02a690`) | Sonnet (lot 1), Fable (2 à 5) | voir `2026-11-17/compte-rendu.md` |
| 6 | Benchmark | ✅ fusionné (`68baf17`) | Sonnet 5.5 | 20 sites, 39 fonctionnalités, 780 cases : 155 oui, 18 partiel, 36 non, **571 non vérifié (73 %)** — dix sites en 403 ; à compléter à la main (`docs/benchmark/synthese.md`) |
| 7 | Journal de décisions (rattrapage) | ✅ fusionné (`8447ede`) | Sonnet 5.5 | 51 notes + index dans `docs/decisions/` : 37 acceptées, 14 « à valider par Thomas » |
| 8 | Boutons smooth | ✅ fusionné (`4a15e25`, `486ab01`, `8045820`) | Fable 5.2 | source unique `components/ds/control.tsx` + bloc `.ctl` ; JS inchangé, pire contraste 4,52:1 (mesures de la session) ; 36 références régénérées ; `check.py --visuel` vert après fusion |
| 9 | TOK-114 Decks | ✅ fusionné (`c71b794`, `5673777`, `fdfeedc`) | Fable 5.2 | `/decks` + `/decks/{slug}`, 3 tables nouvelles dans `yugioh.db` (4 309 / 167 / 7 303 lignes ; aucune table existante modifiée, vérifié contre la sauvegarde `backup_avant_tok114_20261116.db`) ; `serving.db` 10,7 → 11,6 Mo ; seuils 80 % / 20 %, fiche dès 8 listes ; `check.py --visuel` vert après fusion (45 captures) |
| 10 | TOK-92 images | 🏗️ en cours (téléchargement des images en arrière-plan, ~8 500 fichiers à 23 h) | Sonnet 5.5 (demandé) | session « Lot 10 — TOK-92 images de cartes » |
| 11 | TOK-103 boutique | à faire | | |
| 12 | TOK-55 Ban Predictor historique | à faire | | |
| 13 | Outillage | 🏗️ démarré le 16/11, en parallèle du lot 10 (demande de Thomas) | Sonnet 5.5 (demandé) | session « Lot 13 — Outillage » ; avancé avant 11 et 12 (aucun fichier commun avec le lot 10) |
| 14 | TOK-35 | à faire | | |
| 15 | Charte + explication graphique | à faire | | |
| 16 | Réécriture des textes | à faire | | |

Dernière mise à jour : 2026-11-16, lots 10 et 13 en cours en parallèle. Modèle front à partir du lot 11 : Opus 5.5 (consigne de Thomas). Seul l'orchestrateur écrit le tableau des lots.

## Tâches de fond
| # | Tâche | Dernier passage | Note |
|---|---|---|---|
| 1 | Revue du code fusionné | jamais | |
| 2 | Vérification des données | jamais | |
| 3 | Documentation désynchronisée | jamais | |
| 4 | Tests | jamais | |
| 5 | Confrontation tier list d'experts (Angelechy, YCS Paris) | jamais | |

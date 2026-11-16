# État de la file

| # | Lot | Statut | Modèle utilisé | Note |
|---|---|---|---|---|
| 1-5 | Sprint 1 | ✅ fusionnés dans `claude/front-nuit-17-11` (dernier commit `d02a690`) | Sonnet (lot 1), Fable (2 à 5) | voir `2026-11-17/compte-rendu.md` |
| 6 | Benchmark | ✅ fusionné (`68baf17`) | Sonnet 5.5 | 20 sites, 39 fonctionnalités, 780 cases : 155 oui, 18 partiel, 36 non, **571 non vérifié (73 %)** — dix sites en 403 ; à compléter à la main (`docs/benchmark/synthese.md`) |
| 7 | Journal de décisions (rattrapage) | ✅ fusionné (`8447ede`) | Sonnet 5.5 | 51 notes + index dans `docs/decisions/` : 37 acceptées, 14 « à valider par Thomas » |
| 8 | Boutons smooth | ✅ fusionné (`4a15e25`, `486ab01`, `8045820`) | Fable 5.2 | source unique `components/ds/control.tsx` + bloc `.ctl` ; JS inchangé, pire contraste 4,52:1 (mesures de la session) ; 36 références régénérées ; `check.py --visuel` vert après fusion |
| 9 | TOK-114 Decks | ✅ fusionné (`c71b794`, `5673777`, `fdfeedc`) | Fable 5.2 | `/decks` + `/decks/{slug}`, 3 tables nouvelles dans `yugioh.db` (4 309 / 167 / 7 303 lignes ; aucune table existante modifiée, vérifié contre la sauvegarde `backup_avant_tok114_20261116.db`) ; `serving.db` 10,7 → 11,6 Mo ; seuils 80 % / 20 %, fiche dès 8 listes ; `check.py --visuel` vert après fusion (45 captures) |
| 10 | TOK-92 images | ✅ fusionné (`8834e37`, `f3ed788`) | Sonnet 5.5 | 14 034 cartes, 3 tailles WebP, 1,1 Go hors Git dans `data/card-images/` (ignoré, vérifié), 0 échec, 116 variantes absentes chez YGOPRODeck (repli) ; route locale `/card-images/...` (lecture limitée à 2 segments, dossier connu, nom numérique) ; 0 requête vers YGOPRODeck (mesure de la session) ; `fetch_new_cards.py` + téléchargement incrémental dans `refresh_all.py` ; reste : stockage définitif (lot 14) ; `check.py --visuel` vert après fusion |
| 11 | TOK-103 boutique | 🏗️ démarré le 17/11, en parallèle du lot 12 | Opus 5.5 (demandé) | session « Lot 11 — TOK-103 boutique par archétype » ; pas de nav, pas d'écriture en base |
| 12 | TOK-55 Ban Predictor historique | 🏗️ démarré le 17/11, en parallèle du lot 11 | Opus 5.5 (demandé) | session « Lot 12 — TOK-55 Ban Predictor » ; onglet du Ban Center, pas de nav, pas d'écriture en base |
| 13 | Outillage | ✅ fusionné (`3e1ad8b`) | Sonnet 5.5 | `.claude/settings.json` (38 commandes pré-autorisées, 13 refus), hook `garde_fou.py` (28 bloquées / 24 autorisées, étape de `check.py`), `/fin-de-journee`, règle d'or + journal de décisions + plan mode dans `CLAUDE.md`. Vérifié après fusion : le hook laisse passer fusion, commit, `worktree remove`, `check.py`, copie de sauvegarde, et bloque push et `rm -rf data`. **Faux positif constaté** : une commande dont un heredoc cite la commande de push entre accents graves est bloquée (contournement : éditer le fichier sans heredoc). Non mesuré : « zéro invite » en session interactive. `npm run lighthouse` non pré-autorisé (lance un serveur). |
| 14 | TOK-35 | ✅ fusionné (`d18beb5`) | Sonnet 5.5 | `vercel.json`, `.vercelignore`, `.env.example`, guide `docs/deploiement.md` ; l'API ouvre la base en lecture seule et lit `backend/data/serving.db` sur Vercel (ignoré par Git) ; aucun déploiement. **Trois blocages avant le premier déploiement** (guide §0) : le build du front appelle l'API (lot de code à prévoir, §8.1) ; images 1,17 Go trop grosses pour Vercel Blob gratuit (recommandé : Cloudflare R2) ; protection à choisir. Formulaire pour Thomas au §9. `check.py` vert après fusion (44 tests sur chaque base) |
| 15 | Charte + explication graphique | ⏸ étape 1 fusionnée et **validée par Thomas le 17/11** (`4c4d86e`, réponses dans `decisions-prises.md`) ; étape 2 (composants, `/methode` sans formule) après les lots 11 et 12 | Opus 5.5 | 6 infobulles et 8 formules relevées (annexe A), 10 exemples avant/après ; étape 2 (composants, `/methode`) après validation et après les lots 11 et 12 ; la session reste ouverte pour l'étape 2 |
| 16 | Réécriture des textes | à faire | | |

Dernière mise à jour : 2026-11-17, lot 14 fusionné ; lots 11 et 12 en cours en parallèle. Seul l’orchestrateur écrit le tableau des lots.

## Tâches de fond
| # | Tâche | Dernier passage | Note |
|---|---|---|---|
| 1 | Revue du code fusionné | jamais | |
| 2 | Vérification des données | jamais | |
| 3 | Documentation désynchronisée | jamais | |
| 4 | Tests | jamais | |
| 5 | Confrontation tier list d'experts (Angelechy, YCS Paris) | jamais | |

# Decks : index des archétypes et fiche de composition (TOK-114, lot 9, 2026-11-16)

Branche `claude/lot09-tok-114-decks-99ff00`. Le graphe de synergies est mis en attente (décision du 16/11) : une
liste de deck dit mieux qu'un graphe quelles cartes se jouent ensemble.

## Ce qui est livré

- `scripts/build_archetype_profiles.py` (ajouté à `scripts/refresh_all.py`, après `card_impact`) : pour chaque
  archétype et chaque zone (main, extra, side), part des listes qui contiennent la carte et médiane des exemplaires
  parmi ces listes. Population et fenêtre de la tier list : TCG, `deck_legality.legal = 1`, mois récents cumulés
  jusqu'à `MIN_WINDOW_DECKS` (importé de `backend/app/tiering.py`, pas recopié).
- Trois tables, créées par ce script et lui seul, ajoutées à `SERVED_TABLES` :

| Table | Lignes (2026-11-16) | Contenu |
|---|---|---|
| `archetype_card_profile` | 4 309 | (archétype, zone, carte) : `n_lists`, `n_decks`, `share`, `median_copies`, fenêtre, date de calcul |
| `archetype_recent_decks` | 167 | les 5 listes les plus récentes par archétype (auteur, tournoi, résultat, date) |
| `archetype_recent_deck_cards` | 7 303 | le contenu de ces listes |

- `GET /api/v1/decks` (index) et `GET /api/v1/decks/{slug}` (fiche + listes récentes), `backend/app/routers/decks.py`.
  Slug servi par l'API (`app/slugs.py`), résolution insensible à la casse, 404 si l'archétype n'a aucune liste dans la
  fenêtre.
- Pages `/decks` et `/decks/[archetype]`, lien « composition » sur chaque ligne de la tier list, bouton « Composition
  du deck » sur la page d'archétype, entrée « Decks » dans le groupe Méta de la navigation.

## Seuils (analyse de `data-scientist-ygo`, lecture seule, 396 decks, 60 archétypes, oct. et nov. 2026)

Un seul endroit : `backend/app/deck_profile.py`. Le script ne pose aucun seuil, il compte.

| Règle | Valeur | Justification mesurée |
|---|---|---|
| Carte « de base » | part ≥ 80 % des listes | Somme des exemplaires médians des cartes de base du main : 26 à 34 cartes pour 7 des 8 archétypes à ≥ 10 listes (Ars Magna Chaos Ritual : 40). À 70 %, 4 sur 8 dépassent 35 ; à 90 %, Branded tombe à 19. |
| Carte « d'appoint » | 20 % ≤ part < 80 % | Stabilité par bootstrap (300 tirages, main) : 9,3 % d'étiquettes changées à 80/20, contre 8,1 à 9,4 % pour 75/20, 70/20, 75/25, 90/20, 80/30. Aucun autre couple ne fait mieux de façon mesurable. |
| Effectif minimal d'une fiche | 8 listes | Elfnote (82 listes) et Angelechy (65) ramenés à n listes (1 000 tirages sans remise) : étiquettes changées 19 % / 24 % à n = 5, 9 % / 13 % à n = 8, 7 % / 14 % à n = 10. De 5 à 8 l'erreur est divisée par deux, 10 n'apporte rien. |
| Intervalle de confiance | non affiché | À n = 8, Wilson 95 % pour 7/8 va de 53 à 98 % : trop large pour informer. L'effectif « k sur n » est écrit à côté de chaque pourcentage. |

Ce que ces seuils ne sont pas :
- **Pas des optimums.** La distribution des parts est en U (101 cartes du main sur 390 entre 95 et 100 %), sans creux
  net à 80 %. 80 et 20 sont des seuils ronds, cohérents avec la taille d'un deck.
- **Mesurés sur deux archétypes**, avec leur propre échantillon complet pour référence : estimation optimiste.
  L'extra deck est moins stable (11 à 18 % d'étiquettes changées à n = 8).
- À petit effectif le seuil est grossier : 80 % vaut 7 listes sur 8 (87,5 %) ou 8 sur 10.

Couverture : 13 archétypes ont une fiche, soit 292 listes sur 396 (74 %). Les 47 autres ont une page qui ne montre
que leurs listes récentes, sans aucune part.

## Sauvegardes et tailles

- `data/backup_avant_tok114_20261116.db` : 270 700 544 octets (copie `.backup` de `yugioh.db`, `quick_check` ok).
- `data/backup_serving_avant_tok114_20261116.db` : 10 719 232 octets.
- `yugioh.db` : 43 → 46 tables. `serving.db` : 10,7 → 11,6 Mo (+0,9 Mo). Les deux tables à clé composite sont
  `WITHOUT ROWID` : avec un index de clé primaire en double, la base de service montait à 12,3 Mo.

## Mesures (build de production, mobile, `LH_THROTTLING=devtools`)

| Page | Performance | Accessibilité | LCP | CLS |
|---|---|---|---|---|
| `/decks` | 98 | 100 | 1,87 s | 0 |
| `/decks/branded` | 99 | 100 | 1,75 s | 0 |
| `/decks/elfnote` | 98 | 100 | 1,77 s | 0 |
| `/decks/chaos-ritual` (listes seules) | 99 | 100 | 1,76 s | 0 |
| `/tier-list` | 98 | 100 | 1,81 s | 0 |

`npm run check:meta` : 11 pages principales, 63 pages d'archétype, 13 fiches de deck, 87 adresses dans le sitemap.

## Pièges

- **Une illustration de tuile chargée d'emblée devient l'élément LCP sur mobile** : `/decks` mesurait 2,63 s avec les
  deux premières illustrations en `eager`, 1,85 s une fois différées et masquées sous 760 px.
- **Pas de colonne masquée dans un tableau à largeurs fixes** : les cellules en `display: none` sortent de la grille
  et les suivantes se décalent (colonne du nom à 93 px, lignes de 152 px, page de 16 849 px à 375 px). La barre vit
  dans la cellule de la part.
- **WebP plafonne à 16 383 px** : une capture de page plus haute fait échouer `visual_tests.py --update` après avoir
  vidé le dossier de références. Les listes récentes sont repliées (`<details>`) ; la fiche mobile fait 7 216 px.
- **Une route sans `opengraph-image.tsx` n'a pas d'image de partage** : celle de la racine ne descend pas aux pages
  qui fournissent leur propre `openGraph`. `/decks` et `/decks/[archetype]` ont chacune la leur.
- **Tests visuels** : la fausse API répond 404 hors de `DECKS` (`scripts/visual_tests.py`), comme pour `ARCHETYPES`.
  Les trois réponses figées ont été enregistrées à la main, sans `--refresh-fixtures`, pour ne pas toucher aux autres.
- **Le worktree n'a pas de base** : `build_archetype_profiles.py --db <dépôt principal>/data/yugioh.db`.
  `build_serving_db.py` n'a pas d'option de chemin (lancé ici en redéfinissant `SOURCE_DB` et `SERVING_DB`).
- **Si le schéma des trois tables change**, `CREATE TABLE IF NOT EXISTS` ne les migre pas : les supprimer à la main
  (elles se recalculent en moins d'une seconde).
- Le main deck va de 40 à 60 cartes (moyenne 42,25 dans la fenêtre) : la page écrit « sur 40 à 60 », jamais « sur 40 ».
- « Chaos Ritual » (7 listes) est un libellé fourre-tout de yugiohmeta : 90 cartes distinctes au main. Trois libellés
  se partagent la famille (Dark Magician Chaos Ritual 19, Ars Magna Chaos Ritual 10, Chaos Ritual 7).

## Limites connues

- L'archétype est celui de `tournament_decks` (libellé yugiohmeta), pas `cards.archetype`.
- La règle d'étiquette est la même dans les trois zones ; au side deck presque aucune carte n'atteint 80 %
  (une seule entre 80 et 90 % sur 365 pour les archétypes à ≥ 10 listes).
- Les noms de joueurs affichés sont ceux publiés par yugiohmeta avec les résultats de tournoi.

# TOK-55 — Ban Radar contre l'historique (lot 12, 2026-11-17)

Branche `claude/lot12-tok-55-ban-historique-206ce4` (coupée de `claude/front-nuit-17-11`), non fusionnée.

## Ce qui a été livré

- `scripts/build_ban_radar.py` : la boucle de `backtest()` extraite dans `backtest_lists(conn, fmt)`, sans changer le
  calcul ni `WEIGHTS`. Sortie de `--backtest` identique octet pour octet avant et après (`cmp`).
- `scripts/build_ban_history.py` (nouveau) : tables `ban_backtest_lists` (une ligne par banlist, retenue ou écartée)
  et `ban_backtest_cards` (top 25 de la veille + toutes les cartes touchées). Ajoute la bande du hasard (5e-95e
  centiles du rang médian de k cartes tirées au hasard parmi n, 20 000 tirages, graine 55), la base « staples les plus
  jouées » (même univers classé par part des decks seule) et la place de chaque liste par rapport au calage des poids.
- `GET /api/v1/ban-radar/history` (`routers/ban_radar.py`) : réponse vide si les tables manquent. Tables ajoutées à
  `SERVED_TABLES`.
- Onglet `/ban?tab=historique` (`app/ban/BanHistoryView.tsx`) : bilan par format, frise par format, listes écartées,
  détail par liste (`&liste=tcg-2026-10-19`), tableau des données, méthode repliée.

## Commande sur la base de référence (après fusion)

```
python scripts/build_ban_history.py        # ≈ 15 s, écrit les deux tables dans data/yugioh.db
python scripts/build_serving_db.py         # reconstruit serving.db avec les deux tables
```

Ordre obligatoire : `build_serving_db.py` échoue (« Table absente ») si `build_ban_history.py` n'a pas tourné.
À relancer après chaque nouvelle banlist (`fetch_banlist_history.py`) et chaque `build_ban_radar.py`.
Pas encore dans `refresh_all.py` (hors périmètre du lot).

## Vérification par `data-scientist-ygo` (lecture seule)

- 20 listes retenues, 0 écart sur `n_cards`, `n_decks`, `n_hits`, `n_hits_ranked`, `median_rank`, `random_rank`,
  `top10pct_hits`, `top25pct_hits` ; 225 cartes touchées classées, 0 écart de rang ou de score. 144 listes écartées
  (70 TCG + 74 OCG), comme le backtest ; la page n'en montre que 6 (celles dont la fenêtre contient au moins un deck).
- Base staples validée (sans fuite, comparaison naïve pertinente : `ubiquity` est le critère le plus lourd).
- Bande du hasard validée : intervalle à 90 % ; centre exact (n+1)/2, le backtest imprime n/2 (écart 0,5 rang).
  Pas de lecture globale : environ 1 faux positif attendu sur 20, fenêtres de 6 mois qui se chevauchent.
- Top N : 25 recommandé (à 10, 5 listes sur 20 avec 0 carte touchée, dont la liste de calage).
- Fuites : `bridge` (betweenness du graphe actuel) mesurée négligeable (au plus 7 rangs, dans les deux sens).
  Fenêtre arrêtée la veille de l'**entrée en vigueur**, pas de l'annonce (1 à 3 semaines plus tôt) : les 14 derniers
  jours pèsent jusqu'à 10 % des decks. Test à J-30 : médiane des rangs médians TCG 80 → 120, OCG 28 → 34 ; non
  tranché (ce test retire aussi le dernier mois légitime). À creuser avec les dates d'annonce.
- Échantillon : TCG 2026-05-18 = liste de calage ; OCG 2026-07-01 vue au calage ; seules 3 listes sont
  postérieures au calage (TCG 2026-09-21, TCG 2026-10-19, OCG 2026-10-01).

### Phrases à ne pas écrire (relevé du data scientist)

« L'omniprésence seule ne prédit rien » ; « le score bat les cartes les plus jouées » sans dire la mesure ;
« validé hors échantillon sur 20 listes » ; « meilleur que le hasard sur toutes les listes » (19 sur 20) ;
« les dernières listes confirment le modèle » ; « classement établi avant l'annonce » ; toute lecture en probabilité.

## Résultats (calcul du 2026-11-17 sur une copie de la base du 2026-11-16)

| | TCG | OCG |
|---|---|---|
| Rang médian sous la bande du hasard | 9 listes sur 10 (2025-10-27 dans la bande) | 10 sur 10 |
| Rang médian meilleur que les staples | 3 sur 10 | 8 sur 10 |
| Top 25 touché, Ban Radar | 29 places sur 250 | 41 sur 250 |
| Top 25 touché, staples | 16 sur 250 | 18 sur 250 |

Lecture : le score classe mieux la tête de liste ; en TCG, la simple part des decks place mieux l'ensemble des cartes
touchées. **Ceci contredit le piège « l'omniprésence seule ne prédit rien » de `context.md`** (constat de la v1, sur des
données biaisées par le drapeau `illegal`) : à corriger après validation de Thomas.

### Sortie de `build_ban_history.py`

```
format effective_date  n_cards  n_decks  n_hits  n_hits_ranked  median_rank  random_rank  random_low  random_high  top_n_hits  top10pct_hits  top25pct_hits  baseline_median_rank  baseline_top_n_hits
   TCG     2024-04-15      724     1067       5              5           44          362         139          589           2              3              3                    41                    1
   TCG     2024-09-02      911     1943      13             13           76          456         265          648           3              8             11                    83                    2
   TCG     2024-12-09      837     1582       6              6          168          418         196          646           0              2              3                    83                    0
   TCG     2025-04-07      830     1682      16             16           18          415         262          572          10             13             14                    39                    4
   TCG     2025-09-15      830     2063      12             12           58          415         242          592           3              7              8                    98                    1
   TCG     2025-10-27      834     1996       7              5          350          417         160          676           0              0              1                   224                    0
   TCG     2026-02-02      731     1649      12             12           68          366         214          520           2              7              8                    54                    3
   TCG     2026-05-18      889     1618      12             11           84          444         242          648           1              6              8                    58                    1
   TCG     2026-09-21      981     1834      11              9          206          490         250          736           2              4              5                    99                    0
   TCG     2026-10-19      905     1787      43             37          308          452         335          569           6              7             10                   128                    4
   OCG     2024-04-01      730      901       7              7           22          365         168          565           4              4              5                    43                    2
   OCG     2024-07-01     1016     1819       9              8           19          508         258          758           4              6              7                    62                    2
   OCG     2024-10-01      996     1795      11             11           58          498         274          723           3              9             10                    35                    2
   OCG     2025-01-01      956     1777       7              7           80          478         215          737           3              4              5                    84                    0
   OCG     2025-04-01     1006     2270       7              7           26          503         226          777           3              4              7                    48                    0
   OCG     2025-10-01      869     2161       9              9           30          434         222          652           4              6              8                    52                    1
   OCG     2026-01-01      976     2035      14             14           26          488         295          682           7              9             10                    49                    5
   OCG     2026-04-01     1131     2128      10             10          145          566         309          819           1              5              8                   143                    2
   OCG     2026-07-01     1236     2447      11             11           19          618         342          903           6              6              9                    54                    3
   OCG     2026-10-01     1212     2363      15             15           52          606         364          849           6             12             15                    63                    1

20 listes retenues, 144 écartées, 667 lignes de cartes (top 25 + cartes touchées)
Tables ban_backtest_lists et ban_backtest_cards écrites
```

### Recalculs du data scientist (bridge à 0, veille à J-30, staples, p unilatéral par Monte Carlo)

```
fmt,eff,n,k,med,med_bridge0,med_j30,med_staples,p_score,p_staples
TCG,2024-04-15,724,5,44.0,44.0,138.0,41.0,0.0016999150042497876,0.0014999250037498126
TCG,2024-09-02,911,13,76.0,83.0,69.0,83.0,4.999750012499375e-05,4.999750012499375e-05
TCG,2024-12-09,837,6,168.5,167.0,208.5,82.75,0.03344832758362082,0.0024998750062496873
TCG,2025-04-07,830,16,18.0,20.0,18.0,39.0,4.999750012499375e-05,4.999750012499375e-05
TCG,2025-09-15,830,12,58.0,57.0,101.5,98.25,4.999750012499375e-05,0.00024998750062496874
TCG,2025-10-27,834,5,350.0,350.0,342.0,223.5,0.3511824408779561,0.12099395030248487
TCG,2026-02-02,731,12,68.0,68.0,57.5,54.5,4.999750012499375e-05,4.999750012499375e-05
TCG,2026-05-18,889,11,84.0,85.0,66.0,58.5,0.00039998000099995,9.99950002499875e-05
TCG,2026-09-21,981,9,206.0,204.0,200.0,99.0,0.025098745062746862,0.0011499425028748563
TCG,2026-10-19,905,37,308.0,304.0,351.0,128.5,0.01974901254937253,4.999750012499375e-05
OCG,2024-04-01,730,7,22.0,21.0,16.0,43.0,4.999750012499375e-05,0.000199990000499975
OCG,2024-07-01,1016,8,19.0,19.0,19.0,62.0,4.999750012499375e-05,9.99950002499875e-05
OCG,2024-10-01,996,11,58.0,58.0,37.0,35.0,4.999750012499375e-05,4.999750012499375e-05
OCG,2025-01-01,956,7,80.0,86.0,63.0,84.0,0.000999950002499875,0.00119994000299985
OCG,2025-04-01,1006,7,26.0,25.0,48.0,48.0,9.99950002499875e-05,0.000199990000499975
OCG,2025-10-01,869,9,30.0,30.0,31.0,52.0,4.999750012499375e-05,4.999750012499375e-05
OCG,2026-01-01,976,14,26.0,25.5,22.0,49.25,4.999750012499375e-05,4.999750012499375e-05
OCG,2026-04-01,1131,10,145.0,142.0,122.5,143.25,0.0010499475026248687,0.0009499525023748813
OCG,2026-07-01,1236,11,19.0,19.0,21.0,54.0,4.999750012499375e-05,4.999750012499375e-05
OCG,2026-10-01,1212,15,52.0,52.0,38.0,63.0,4.999750012499375e-05,4.999750012499375e-05
```

### Sortie de `build_ban_radar.py --backtest` (extrait : en-têtes et lignes de synthèse)

```
--- Liste du 2024-04-15 — 5 cartes touchées
    univers noté : 724 cartes (1067 decks sur 6 mois)
    -> rang médian 44/724 (aléatoire ≈ 362) | top-10% : 3/5 | top-25% : 3/5
--- Liste du 2024-09-02 — 13 cartes touchées
    univers noté : 911 cartes (1943 decks sur 6 mois)
    -> rang médian 76/911 (aléatoire ≈ 456) | top-10% : 8/13 | top-25% : 11/13
--- Liste du 2024-12-09 — 6 cartes touchées
    univers noté : 837 cartes (1582 decks sur 6 mois)
    -> rang médian 168/837 (aléatoire ≈ 418) | top-10% : 2/6 | top-25% : 3/6
--- Liste du 2025-04-07 — 16 cartes touchées
    univers noté : 830 cartes (1682 decks sur 6 mois)
    -> rang médian 18/830 (aléatoire ≈ 415) | top-10% : 13/16 | top-25% : 14/16
--- Liste du 2025-09-15 — 12 cartes touchées
    univers noté : 830 cartes (2063 decks sur 6 mois)
    -> rang médian 58/830 (aléatoire ≈ 415) | top-10% : 7/12 | top-25% : 8/12
--- Liste du 2025-10-27 — 7 cartes touchées
    univers noté : 834 cartes (1996 decks sur 6 mois)
    hors univers (<5 decks) : 2
    -> rang médian 350/834 (aléatoire ≈ 417) | top-10% : 0/5 | top-25% : 1/5
--- Liste du 2026-02-02 — 12 cartes touchées
    univers noté : 731 cartes (1649 decks sur 6 mois)
    -> rang médian 68/731 (aléatoire ≈ 366) | top-10% : 7/12 | top-25% : 8/12
--- Liste du 2026-05-18 — 12 cartes touchées
    univers noté : 889 cartes (1618 decks sur 6 mois)
    hors univers (<5 decks) : 1
    -> rang médian 84/889 (aléatoire ≈ 444) | top-10% : 6/11 | top-25% : 8/11
--- Liste du 2026-09-21 — 11 cartes touchées
    univers noté : 981 cartes (1834 decks sur 6 mois)
    hors univers (<5 decks) : 2
    -> rang médian 206/981 (aléatoire ≈ 490) | top-10% : 4/9 | top-25% : 5/9
--- Liste du 2026-10-19 — 43 cartes touchées
    univers noté : 905 cartes (1787 decks sur 6 mois)
    hors univers (<5 decks) : 6
    -> rang médian 308/905 (aléatoire ≈ 452) | top-10% : 7/37 | top-25% : 10/37
    70 listes écartées faute de matière (<600 decks ou <5 cartes touchées) — les plus récentes : 2023-06-05 (86 decks, 14 touchées), 2023-09-25 (95 decks, 3 touchées), 2024-01-01 (8 decks, 12 touchées)
--- Liste du 2024-04-01 — 7 cartes touchées
    univers noté : 730 cartes (901 decks sur 6 mois)
    -> rang médian 22/730 (aléatoire ≈ 365) | top-10% : 4/7 | top-25% : 5/7
--- Liste du 2024-07-01 — 9 cartes touchées
    univers noté : 1016 cartes (1819 decks sur 6 mois)
    hors univers (<5 decks) : 1
    -> rang médian 19/1016 (aléatoire ≈ 508) | top-10% : 6/8 | top-25% : 7/8
--- Liste du 2024-10-01 — 11 cartes touchées
    univers noté : 996 cartes (1795 decks sur 6 mois)
    -> rang médian 58/996 (aléatoire ≈ 498) | top-10% : 9/11 | top-25% : 10/11
--- Liste du 2025-01-01 — 7 cartes touchées
    univers noté : 956 cartes (1777 decks sur 6 mois)
    -> rang médian 80/956 (aléatoire ≈ 478) | top-10% : 4/7 | top-25% : 5/7
--- Liste du 2025-04-01 — 7 cartes touchées
    univers noté : 1006 cartes (2270 decks sur 6 mois)
    -> rang médian 26/1006 (aléatoire ≈ 503) | top-10% : 4/7 | top-25% : 7/7
--- Liste du 2025-10-01 — 9 cartes touchées
    univers noté : 869 cartes (2161 decks sur 6 mois)
    -> rang médian 30/869 (aléatoire ≈ 434) | top-10% : 6/9 | top-25% : 8/9
--- Liste du 2026-01-01 — 14 cartes touchées
    univers noté : 976 cartes (2035 decks sur 6 mois)
    -> rang médian 26/976 (aléatoire ≈ 488) | top-10% : 9/14 | top-25% : 10/14
--- Liste du 2026-04-01 — 10 cartes touchées
    univers noté : 1131 cartes (2128 decks sur 6 mois)
    -> rang médian 145/1131 (aléatoire ≈ 566) | top-10% : 5/10 | top-25% : 8/10
--- Liste du 2026-07-01 — 11 cartes touchées
    univers noté : 1236 cartes (2447 decks sur 6 mois)
    -> rang médian 19/1236 (aléatoire ≈ 618) | top-10% : 6/11 | top-25% : 9/11
--- Liste du 2026-10-01 — 15 cartes touchées
    univers noté : 1212 cartes (2363 decks sur 6 mois)
    -> rang médian 52/1212 (aléatoire ≈ 606) | top-10% : 12/15 | top-25% : 15/15
    74 listes écartées faute de matière (<600 decks ou <5 cartes touchées) — les plus récentes : 2023-10-01 (1 decks, 9 touchées), 2024-01-01 (7 decks, 6 touchées), 2025-07-01 (2434 decks, 3 touchées)
```

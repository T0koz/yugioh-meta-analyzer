# TOK-137 — Fenêtre du backtest du Ban Radar : seulement les decks connus à la coupure (jalon n°4, 2026-11-18)

Branche `claude/jalon-4-graphe-backtest-vues-e1f982`, session sur Opus 5.5. Suite d'une fuite relevée par le data
scientist au TOK-120 (`ban-radar-rangs-tok-120.md`, tableau des fuites). **Lecture seule** de la base de référence
(md5 identique avant et après). **Rien d'affiché ne change** : le paramètre ajouté vaut `False` par défaut, `--backtest`
redonne les chiffres de référence (TCG 2026-05-18 84/889, OCG 2026-07-01 19/1236, les 20 listes identiques).

## En clair (pour Thomas)

1. Le backtest classe les cartes « la veille » de chaque banlist avec les decks des 6 mois précédents. Il choisissait
   ces decks par la **date du tournoi**. Or un deck est mis en ligne 5,5 jours après le tournoi en moyenne : 2,5 % des
   decks de ces fenêtres n'étaient pas encore publiés le jour de la coupure. Le classement de « la veille » voyait donc
   des decks que personne ne connaissait ce jour-là.
2. Avec le filtre (« deck mis en ligne avant la coupure »), le Ban Radar paraît **un peu meilleur**, pas moins bon :
   top 25 TCG 29 → 32 cartes touchées, OCG 41 → 45 ; en OCG, le rang médian bat les staples sur 9 listes sur 10 au lieu
   de 8.
3. Pourquoi : ces decks tardifs sont presque tous des 14 derniers jours de la fenêtre, et en OCG 675 sur 702 ont été
   joués **après la publication du contenu** de la liste. Les joueurs y avaient déjà commencé à retirer les cartes
   visées. L'ancienne mesure était donc pessimiste ; **le radar n'est pas meilleur, c'est la mesure qui est plus juste**.
4. Le verdict de l'onglet Historique tiendrait sur le fond, mais sa phrase sur la significativité deviendrait fausse
   (deux écarts OCG à p = 0,021 au lieu d'un) : nouvelle formulation proposée au formulaire.

## Écart avec le brief

Le brief demandait de filtrer « sur la date du tournoi (aujourd'hui sur la mise en ligne) ». Le code faisait l'inverse :
la fenêtre porte déjà sur la date du tournoi (`tournament_decks.created`) et la fuite vient des decks **mis en ligne**
après la coupure (`uploaded`), comme l'écrit le journal de TOK-120 (« le filtre porte sur la date du tournoi
(`created`), pas sur la mise en ligne »). Le correctif suit le constat : la fenêtre reste définie par la date du tournoi
et exige en plus `uploaded ≤ coupure`. Décision prise par défaut, notée au formulaire.

## Le code

`scripts/build_ban_radar.py` : paramètre `require_uploaded: bool = False` sur `load_usage`, `build`, `backtest_lists` et
`backtest` (une seule implémentation : `build_ban_history.py` et les diagnostics passent par `backtest_lists`). À `True`,
la requête ajoute `AND td.uploaded <= :as_of`, même comparaison de chaînes que `created` (les decks du jour de la
coupure en sont exclus dans les deux cas). Le seuil `BACKTEST_MIN_DECKS` (600) se compte sur les mêmes decks filtrés :
aucune liste ne passe dessous (la plus petite, OCG 2024-04-01, passe de 901 à 831 decks).

Commandes :

```bash
python scripts/build_ban_radar.py --backtest                          # référence, inchangée
python scripts/build_ban_radar.py --backtest --connus-a-la-coupure    # fenêtre filtrée
python scripts/diagnose_backtest_variantes.py --db <base> --out <dossier> --label actuel
python scripts/diagnose_backtest_variantes.py --db <base> --out <dossier> --label connus --connus-a-la-coupure
python scripts/diagnose_backtest_variantes.py --compare <dossier>/actuel <dossier>/connus
```

`--connus-a-la-coupure` n'est accepté qu'avec `--backtest` : le classement du jour n'a pas de coupure (sa date est le
dernier deck relevé ; aucun deck n'y est « mis en ligne après »).

Test : `backend/tests/test_ban_radar_window.py` (base synthétique en mémoire : défaut inchangé, deck joué avant et mis
en ligne après exclu, valeurs par défaut des quatre signatures).

## Mesures (base de référence du 18/11, dernier deck du 14/11, veille de l'entrée en vigueur)

Decks retirés par liste retenue : 0,1 % (TCG 2026-02-02) à 7,8 % (OCG 2024-04-01), 2,5 % en tout.

| Liste | Decks | Rang médian actuel → connus | Top 25 | Staples (rang médian / top 25) |
|---|---|---|---|---|
| TCG 2024-04-15 | 1 067 → 1 022 | 44 → 47 | 2 → 2 | 41 → 41 / 1 → 1 |
| TCG 2024-09-02 | 1 943 → 1 920 | 76 → 76 | 3 → 3 | 83 → 85 / 2 → 2 |
| TCG 2024-12-09 | 1 582 → 1 544 | 168 → 164 | 0 → 0 | 83 → 83 / 0 → 0 |
| TCG 2025-04-07 | 1 682 → 1 643 | 18 → 18 | 10 → 9 | 39 → 39 / 4 → 4 |
| TCG 2025-09-15 | 2 063 → 1 995 | 58 → 54 | 3 → 4 | 98 → 99 / 1 → 1 |
| TCG 2025-10-27 | 1 996 → 1 967 | 350 → 348 | 0 → 0 | 224 → 224 / 0 → 0 |
| TCG 2026-02-02 | 1 649 → 1 647 | 68 → 68 | 2 → 2 | 54 → 54 / 3 → 3 |
| TCG 2026-05-18 (référence) | 1 618 → 1 548 | **84/889 → 81/877** | 1 → 4 | 58 → 55 / 1 → 1 |
| TCG 2026-09-21 | 1 834 → 1 779 | 206 → 202 | 2 → 2 | 99 → 98 / 0 → 0 |
| TCG 2026-10-19 | 1 787 → 1 768 | 308 → 311 | 6 → 6 | 128 → 134 / 4 → 4 |
| OCG 2024-04-01 | 901 → 831 | 22 → 15 | 4 → 4 | 43 → 42 / 2 → 2 |
| OCG 2024-07-01 | 1 819 → 1 786 | 19 → 16 | 4 → 5 | 62 → 62 / 2 → 2 |
| OCG 2024-10-01 | 1 795 → 1 746 | 58 → 53 | 3 → 4 | 35 → 34 / 2 → 2 |
| OCG 2025-01-01 | 1 777 → 1 746 | 80 → 79 | 3 → 3 | 84 → 85 / 0 → 0 |
| OCG 2025-04-01 | 2 270 → 2 158 | 26 → 25 | 3 → 4 | 48 → 47 / 0 → 0 |
| OCG 2025-10-01 | 2 161 → 2 118 | 30 → 27 | 4 → 4 | 52 → 52 / 1 → 1 |
| OCG 2026-01-01 | 2 035 → 1 962 | 26 → 22 | 7 → 8 | 49 → 48 / 5 → 5 |
| OCG 2026-04-01 | 2 128 → 2 018 | 145 → 119 | 1 → 1 | 143 → 139 / 2 → 2 |
| OCG 2026-07-01 (référence) | 2 447 → 2 361 | **19/1 236 → 19/1 226** | 6 → 6 | 54 → 54 / 3 → 2 |
| OCG 2026-10-01 | 2 363 → 2 222 | 52 → 48 | 6 → 6 | 63 → 64 / 1 → 1 |

Sommes par format (celles de `SITE_FACTS.banTop25`), test du signe entre parenthèses :

| | TCG actuel | TCG connus | OCG actuel | OCG connus | TCG connus + TOK-136 | OCG connus + TOK-136 |
|---|---|---|---|---|---|---|
| Top 25 radar / staples | 29 / 16 | **32** / 16 | 41 / 18 | **45 / 17** | 32 / 16 | 44 / 17 |
| Listes radar mieux / moins bien au top 25 | 6 / 1 (p = 0,13) | 7 / 1 (p = 0,07) | 9 / 1 (p = 0,021) | 9 / 1 (p = 0,021) | 7 / 1 | 9 / 1 |
| Listes où le rang médian bat les staples | 3 (p = 0,34) | 3 (p = 0,34) | 8 (p = 0,11) | **9 (p = 0,021)** | 3 | 9 |
| Rang médian moyen, % de l'univers (staples) | 15,9 (10,6) | 16,0 (10,8) | 4,6 (6,2) | 4,2 (6,3) | 15,9 (10,8) | 4,2 (6,3) |

Écart par liste, connus − actuel (bootstrap par liste, 10 000 tirages, graine 137, intervalle à 90 %) :

| Format | Rang médian (points d'univers, négatif = mieux) | Top 25 (cartes touchées) |
|---|---|---|
| TCG | +0,03 [−0,11 ; +0,17], 5 listes mieux, 4 moins bien | +0,3 [−0,2 ; +0,9], 2 mieux, 1 moins bien |
| OCG | −0,44 [−0,76 ; −0,18], 9 mieux, 1 moins bien | +0,4 [+0,2 ; +0,7], 4 mieux, 0 moins bien |

En TCG, l'effet est nul. En OCG, il est petit mais de signe constant ; une liste (OCG 2026-04-01, −1,94 point) en porte
une grande part (sans elle, ≈ −0,27).

### Le verdict de l'onglet Historique tiendrait-il ?

`frontend/src/lib/ban-verdict.ts`, avec les chiffres de la fenêtre filtrée :
- phrase « measures » : **vraie sur le fond** (« plus de cartes touchées dans son top 25 que le classement par part des
  decks (32 contre 16), mais situe moins bien l'ensemble des cartes touchées (rang médian meilleur sur 3 listes sur
  10). En OCG, il fait mieux sur les deux mesures (45 contre 17 ; 9 listes sur 10) ») ;
- phrase « significance » (« seul l'écart de top 25 en OCG dépasse ce que le hasard produit couramment ») : **fausse**,
  l'écart de rang médian OCG passe aussi à p = 0,021 (non corrigé ; avec 4 comparaisons, Bonferroni demanderait
  p < 0,0125 et aucun écart ne passerait) ;
- `verdictMatches` deviendrait faux dès que `ban_backtest_lists` serait recalculée sans réécrire `SITE_FACTS.banTop25` :
  le verdict serait masqué (échec sans danger).

## Fuites de données

| Variable | Connue à quelle date | Risque |
|---|---|---|
| Decks de la fenêtre (actuel) | date du tournoi ≤ coupure | **fuite** : 2,5 % des decks publiés après la coupure, surtout dans les 14 derniers jours (358 sur 388 retirés en TCG, 702 sur 748 en OCG), joués en OCG après la publication du contenu (675 sur 702) |
| Decks de la fenêtre (connus) | date du tournoi ≤ coupure ET mise en ligne ≤ coupure | aucune pour les decks ; la coupure reste « la veille de l'entrée en vigueur » : des decks joués après l'annonce et mis en ligne à temps restent (voir TOK-121, coupure « contenu ») |
| Critère pont | graphe du jour (TOK-120, TOK-136) | inchangé par ce ticket |

## Relecture `data-scientist-ygo`

Lecture seule. Liste OCG 2026-04-01 rejouée depuis la base (2 128 → 2 018 decks, rang médian 145 → 119, identique au
CSV), sommes recalculées depuis les CSV (32/16, 45/17), écart OCG −0,44 retrouvé. Mécanisme vérifié : decks retirés
concentrés en fin de fenêtre, mis en ligne 4 à 5 jours après le tournoi, avec moins de cartes touchées par deck que les
decks gardés de la même période (OCG 1,85 contre 2,22 ; TCG 1,99 contre 2,16). Lecture : on retrouve une partie de
l'effet de la coupure « contenu » du TOK-121 (≈ 5 rangs en OCG) ; **le backtest actuel était pessimiste, ne pas
présenter ce gain comme une amélioration du radar**. Recommandation : adopter le filtre comme défaut de
`backtest_lists` seulement (pas du classement du jour), sur le principe (« ce qui était connu à la coupure ») et non pour
le gain ; une seule réécriture des chiffres du site avec TOK-136 si les deux sont acceptés. Formulation proposée pour la
phrase de significativité, reprise au formulaire.

## À relire par la collaboratrice

1. La définition de « connu à la coupure » : `uploaded` de yugiohmeta est-il bien la date de publication publique du
   deck (et non une date de modification) ?
2. L'interaction avec la coupure « contenu » (TOK-121) : les deux corrections se recouvrent en partie ; faut-il mesurer
   les deux ensemble avant de changer le défaut ?
3. Les tests du signe sur 10 listes non indépendantes (fenêtres de 6 mois qui se recouvrent) : p optimistes.

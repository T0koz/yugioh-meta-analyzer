# TOK-121 — Dates d'annonce des banlists et effet sur le backtest du Ban Radar (lot 21, 2026-11-18)

Branche `claude/lot21-dates-annonce-65588d`, non fusionnée. Session Sonnet 5.5. Suite de la question 4 du diagnostic
TOK-115 (`ban-radar-tcg-diagnostic.md`) : le backtest classe « la veille de l'entrée en vigueur », donc les decks
joués entre l'annonce et l'entrée en vigueur sont dans la fenêtre. **Aucun poids modifié, rien d'affiché ne change**
(ni front, ni endpoint, ni table servie) ; `banlist_history` n'est pas touchée.

Reproduire (réseau : Yugipedia, ≈ 5 min ; mesure ≈ 50 s, graine fixée) :

```
python scripts/fetch_banlist_announcements.py --db <base>            # écrit banlist_announcements
python scripts/diagnose_ban_radar.py --annonces --db <base> --out <dossier>
```

---

## La réponse en quatre phrases

1. **La date d'annonce est trouvée, avec sa preuve, pour les 20 listes du backtest** : 16 ont le jour où les cartes
   sont devenues publiques ; 4 listes TCG récentes n'ont qu'une source citée (borne haute, date non écrite par Yugipedia),
   dites comme telles.
2. **« Annoncée » ne veut pas dire la même chose partout.** Konami OCG publie la *date* de la prochaine liste une dizaine
   de jours avant son *contenu* ; Yugipedia écrit « first announced on » pour l'une ou l'autre selon la page (les listes OCG
   de 2026 et la liste TCG de septembre 2024 portent la date de sortie, pas les cartes). Seule la publication des cartes
   change ce que les joueurs peuvent anticiper : la table sépare les deux.
3. **Le décalage est petit.** Couper à la publication des cartes retire 8 à 11 jours en OCG (3,6 à 9,7 % des decks de la
   fenêtre, médiane 7,8 %) et 1 à 3 jours en TCG (0,7 à 4,7 %, médiane 1,8 % ; deux listes sans date écrite à 7 et 12 jours).
   Le « jusqu'à 10 % » du diagnostic est confirmé comme plafond.
4. **L'effet sur le score est faible et exploratoire** : en OCG le rang médian s'améliore dans 9 listes sur 10
   (≈ 5 rangs sur 1 100 cartes), mais aucun des 60 tests ne survit à la correction pour comparaisons multiples ; en TCG, rien
   de net. **Le verdict de la page Historique ne change pas** (formulaire).

---

## 1. La table `banlist_announcements`

Une ligne par liste de `banlist_history` (170 listes avec date d'entrée en vigueur ; « February 2022 Lists » n'en a pas).
Clé `(format, list_name)`. Table nouvelle, reconstruite à chaque exécution dans une transaction unique, sauvegarde de la
base à la première création seulement ; une page en échec réseau garde sa ligne précédente.

| Colonne | Sens |
|---|---|
| `announced_date`, `announced_precision` | ce que dit la page Yugipedia (« announced on … ») ; `jour`, `jour_deduit` (« on the day prior », accepté seulement si une référence citée porte ce jour), `debut_evenement` (« on the weekend of … ») |
| `announced_kind` | `liste` (les cartes) ou `date_seule` (une source citée titrée « Announcement », « Date For… », « To Be Revealed » porte le même jour : date de sortie annoncée, pas les cartes) |
| `full_list_date` | liste complète publiée plus tard que la première annonce, si la page le dit |
| `first_source_date` | plus ancienne source citée qui reprend le contenu : **borne haute** (le contenu était public ce jour-là ou avant), jamais la date elle-même |
| `content_date`, `content_basis` | jour où les cartes touchées sont devenues publiques : l'annonce Yugipedia si `liste`, sinon la liste complète, sinon l'article de la liste. **Vide** sans preuve |
| `cited_url`, `cited_source` | source datée du jour retenu (Konami = comptes officiels, vidéos YCS, yu-gi-oh.jp ; YGOrganization ; Beyond the Duel) |
| `evidence`, `missing_reason`, `source_url`, `fetched_at` | phrase relevée, raison d'un vide, page lue, horodatage |

Couverture : 170 listes ; phrase d'annonce sur 19 (toutes depuis 2023), borne haute seule sur 74, rien sur 77 (listes
anciennes, avant les sources en ligne : raison écrite dans `missing_reason`). **Aucune date n'est devinée.** Le site officiel
de Konami ne publie pas de date d'annonce exploitable pour les listes passées ; il n'est cité que via les liens de Yugipedia
(comptes officiels, yu-gi-oh.jp).

### Les 20 listes du backtest, ligne par ligne

| Format | Entrée en vigueur | Annonce (Yugipedia) | Nature | Cartes publiques le | Preuve |
|---|---|---|---|---|---|
| OCG | 2024-04-01 | 2024-03-24 | liste | 2024-03-24 | YGOrganization `weirdscience` |
| OCG | 2024-07-01 | 2024-06-23 | liste | 2024-06-23 | phrase Yugipedia (aucune référence de ce jour) |
| OCG | 2024-10-01 | 2024-09-23 | liste | 2024-09-23 | phrase Yugipedia (aucune référence de ce jour) |
| OCG | 2025-01-01 | 2024-12-22 | liste | 2024-12-22 | YGOrganization `afarewelltoryzealarms` |
| OCG | 2025-04-01 | 2025-03-23 | liste | 2025-03-23 | YGOrganization `ripscythe` |
| OCG | 2025-10-01 | 2025-09-21 | liste | 2025-09-21 | Konami JP `yu-gi-oh.jp` (id 2341) |
| OCG | 2026-01-01 | 2025-12-21 | liste | 2025-12-21 | YGOrganization `metamorphosisreturns` |
| OCG | 2026-04-01 | 2026-03-13 | **date seule** | **2026-03-22** | YGOrganization `ocgapril1st2026limitregulation` |
| OCG | 2026-07-01 | 2026-06-12 | **date seule** | **2026-06-21** | YGOrganization `ocgjuly1st2026limitregulation` |
| OCG | 2026-10-01 | 2026-09-11 | **date seule** | **2026-09-20** | YGOrganization `theshifterisdead` |
| TCG | 2024-04-15 | — | — | — (borne haute 2024-04-13) | YGOrganization `april-tcg-forbidden-limited-list-update` |
| TCG | 2024-09-02 | 2024-07-10 | **date seule** | **2024-08-31** (« finally released ») | YGOrganization `400horsepower` |
| TCG | 2024-12-09 | 2024-12-08 (jour précédent, confirmé) | liste | 2024-12-08 | vidéo officielle YCS Anaheim, 8 déc. 2024 |
| TCG | 2025-04-07 | 2025-04-06 (jour précédent, confirmé) | liste | 2025-04-06 | vidéo officielle YCS Houston, 6 avr. 2025 |
| TCG | 2025-09-15 | 2025-09-12 | liste | 2025-09-12 | compte officiel Konami `@YuGiOh_TCG` |
| TCG | 2025-10-27 | 2025-10-24 | liste | 2025-10-24 | compte officiel Konami `@YuGiOh_TCG` |
| TCG | 2026-02-02 | — | — | — (borne haute 2026-01-21) | compte officiel Konami Europe + YGOrganization, 21 janv. |
| TCG | 2026-05-18 | — | — | — (borne haute 2026-05-11) | YGOrganization `prematurekewltunenerfs` (relayant le compte officiel) |
| TCG | 2026-09-21 | — | — | — (borne haute 2026-09-20) | YGOrganization `putinvokerbackpls` |
| TCG | 2026-10-19 | 2026-10-16 (« weekend of », début de l'événement) | liste | 2026-10-16 (liste complète le 18) | page Yugipedia, YCS Houston |

Lecture :
- Les trois listes OCG de 2026 et la liste TCG de septembre 2024 sont celles où « annoncée » ne dit que la date de
  sortie. Pour l'OCG, c'est un changement de pratique de la page Yugipedia (2024-2025 : date du contenu ; 2026 : date de
  la première annonce) : sans lire les sources citées, le scénario « annonce » aurait coupé 19 à 20 jours avant au lieu de 10.
- **Les 4 listes TCG sans date écrite** (2024-04-15, 2026-02-02, 2026-05-18, 2026-09-21) n'ont que la date d'un article
  de la liste. Cette date est postérieure ou égale à l'annonce réelle : couper à cette date retire **moins** de decks que
  la vérité, donc sous-estime l'effet. La liste du 2026-10-19 coupe au début de l'événement (16 oct.), jour exact de la
  première révélation non précisé (cinq parties sur trois jours).
- Écart connu : YGOrganization date l'article du lendemain de l'annonce dans un cas (2024-12-09 contre annonce le 8) ;
  d'où « borne haute » et pas « date ».

---

## 2. La mesure : classer la veille de l'annonce

`diagnose_ban_radar.py --annonces` (le comportement par défaut du script ne change pas) rejoue `backtest_lists` avec
une date de coupure différente par liste (paramètre optionnel `as_of_override`, ajouté à `build_ban_radar.backtest_lists` ;
`backtest()` et `build_ban_history.py` ne l'utilisent pas). Mêmes 20 listes (aucune n'est perdue sous `BACKTEST_MIN_DECKS`,
inchangé), mêmes cartes touchées, mêmes six critères recalculés à la nouvelle date. Rien n'est estimé : les poids sont ceux
du script. Quatre scénarios, déclarés avant de regarder les résultats :

| Scénario | Date de coupure = la veille de… | Listes décalées |
|---|---|---|
| `effective` (référence) | l'entrée en vigueur | — |
| `annonce` | la date écrite par Yugipedia (peut n'être qu'une date de sortie) | OCG 10, TCG 6 |
| `contenu` | la publication des cartes | OCG 10, TCG 6 |
| `contenu+borne` | idem, plus la source citée pour les 4 listes TCG sans date écrite | OCG 10, TCG 10 |

Incertitude : bootstrap par liste (10 000 tirages, graine 115, intervalle 90 %) et test du signe bilatéral, égalités retirées
(même méthode que TOK-115). Les écarts sont calculés sur les seules listes décalées.

### Décalage de la coupure (scénario `contenu+borne`)

| | OCG (10 listes) | TCG (10 listes) |
|---|---|---|
| Jours retirés avant la veille de l'entrée en vigueur | 8 à 11 (médiane 10) | 1 à 12 (médiane 2,5 ; 8 listes sur 10 à 3 jours ou moins) |
| Part des decks de la fenêtre retirés | 3,6 à 9,7 % (médiane 7,8 %) | 0 à 4,7 % (médiane 1,8 %) |

### Classement par scénario (10 listes par format)

| Format | Scénario | Score : rang médian (médiane des listes) | Score : rang médian moyen en % | Score : top 25 | Score : AUC | Staples : rang médian | Staples : % | Staples : top 25 |
|---|---|---|---|---|---|---|---|---|
| OCG | référence | 28 | 4,6 | 41 | 0,887 | 53 | 6,2 | 18 |
| OCG | annonce | 23 | 4,0 | 46 | 0,895 | 55 | 6,6 | 16 |
| OCG | contenu | 23 | 4,1 | 46 | 0,895 | 53,5 | 6,6 | 16 |
| TCG | référence | 80 | 15,9 | 29 | 0,773 | 82,9 | 10,6 | 16 |
| TCG | annonce | 80,8 | 15,9 | 31 | 0,768 | 73,9 | 10,5 | 15 |
| TCG | contenu | 78 | 15,8 | 30 | 0,772 | 83,8 | 10,7 | 16 |
| TCG | contenu+borne | 77,8 | 15,9 | 33 | 0,775 | 83,8 | 10,8 | 15 |

(Les cartes touchées classées passent de 126 à 123 en TCG `annonce` : une carte qui n'entre dans l'univers que dans les
derniers jours disparaît. Rien d'autre ne change.)

### Écart à la référence, score seul (listes décalées)

| Format | Scénario | Rang médian en points de % (négatif = mieux) | Top 25 | AUC |
|---|---|---|---|---|
| OCG | contenu | −0,54 pt [−0,79 ; −0,32], mieux 9/10, p = 0,02 | +5 [+3 ; +8], 5 mieux, 0 pire, 5 égalités, p = 0,06 | +0,008 [+0,003 ; +0,012], 7/10, p = 0,34 |
| TCG | contenu | −0,16 pt [−0,31 ; −0,01], 4/6, p = 0,69 | +1 [0 ; +3], 1 mieux, 5 égalités | −0,000, 3/6 |
| TCG | contenu+borne | −0,07 pt [−0,21 ; +0,08], 6/10, p = 0,75 | +4 [+1 ; +8], 3 mieux, 7 égalités, p = 0,25 | +0,003, 6/10 |

Un rang médian de −0,54 pt, c'est ≈ 5 à 7 rangs sur un univers de 1 100 cartes (médiane des rangs médians 28 → 23).

### Le score contre les staples, par scénario (poids actuels moins staples)

| Format | Scénario | Rang médian (pts de %) | Top 25 | AUC |
|---|---|---|---|---|
| TCG | référence | +5,3 [+1,4 ; +9,5], score mieux 3/10, p = 0,34 | +13 [+4 ; +23], 6 mieux, 3 égalités, p = 0,125 | −0,055, 1/10, p = 0,02 |
| TCG | contenu | +5,1, 3/10, p = 0,34 | +14, 6 mieux, 3 égalités, p = 0,125 | −0,053, 1/10, p = 0,02 |
| TCG | contenu+borne | +5,1, 3/10, p = 0,34 | **+18 [+10 ; +27], 8 mieux, 2 égalités, p = 0,008** | −0,048, 1/10, p = 0,02 |
| OCG | référence | −1,6 [−2,5 ; −0,6], 8/10, p = 0,11 | +23 [+15 ; +31], 9/10, p = 0,02 | −0,008, 4/10 |
| OCG | contenu | −2,5 [−3,2 ; −1,6], 9/10, p = 0,02 | +30 [+21 ; +38], 9/10, p = 0,02 | +0,001, 6/10 |

**Ce qui ne bouge pas** : en TCG, les staples font mieux que le score en rang médian sur 7 listes sur 10 dans tous les
scénarios ; le score reste devant en OCG et en tête de classement (OCG, top 25, 9 listes sur 10, p = 0,02 avant comme
après). Le verdict de l'Historique tient.

---

## 3. Ce qu'on peut en conclure, et pas plus (relecture `data-scientist-ygo`, 18/11)

- **Pas de fuite d'information** : la coupure ne regarde jamais plus loin que la veille de la publication, le statut de
  banlist est lu à cette date, les 20 listes restent retenues. Trois réserves mineures : décaler la coupure fait aussi
  glisser le début de la fenêtre de 6 mois et la césure du critère de tendance (la liste TCG de février 2026 change de
  classement avec 0 deck retiré) ; la fenêtre ne compte pas exactement les mêmes cartes ; la « borne » est conservatrice.
- **60 tests du signe, aucun ne survit** (seuil de Bonferroni ≈ 0,0008 ; le plus petit p vaut 0,002). Les scénarios
  `contenu` et `contenu+borne` sont presque identiques, donc ces tests ne sont pas indépendants ; les fenêtres de 6 mois
  se recouvrent entre listes voisines (≈ 90 % en TCG), ce qui rend les p optimistes.
- **Le p = 0,008 du TCG (top 25, score contre staples, `contenu+borne`) ne se cite pas seul** : il passe de 6 sur 10 à
  8 sur 10 parce que trois listes changent de statut après l'ajout de bornes, c'est la seule valeur sous 0,05 sur 12 lignes
  TCG de cette comparaison. Lecture : la tendance du diagnostic (score devant en tête de classement en TCG) ne se dément pas.
- **Sens de l'effet OCG** : cohérent avec des joueurs qui s'adaptent à la liste connue (les cartes visées sont moins
  jouées dans les derniers jours, donc moins bien classées). Mais les staples se dégradent aussi dans 8 listes sur 10
  (+0,34 pt) : une partie de l'effet est mécanique (fenêtre plus ancienne). **Il manque un placebo** (même décalage sans
  événement d'annonce) ; non fait ici.
- **Formulation retenue** : « Couper 8 à 11 jours plus tôt (OCG) ou 1 à 3 jours (TCG) change peu le classement. Le score
  gagne environ 5 rangs médians en OCG, dans 9 listes sur 10 ; cet écart ne résiste pas à la correction pour 60
  comparaisons. Le TCG ne montre aucun écart net. Exploratoire : 10 listes par format, fenêtres qui se recouvrent. »
- Le test « à J-30 » du lot 12 (rang médian TCG 80 → 120) mélangeait l'effet de l'annonce et la perte d'un mois de decks :
  l'effet de l'annonce, lui, est de l'ordre de 0 à 5 rangs médians. L'écart du lot 12 ne s'explique donc pas par l'annonce seule (la perte d'un mois de decks pèse bien davantage).
- Sur le site, ne jamais écrire « avant l'annonce » pour le TCG : la coupure y reste à 1 à 3 jours de l'entrée en vigueur.

## 4. À faire relire par la collaboratrice

1. **Dépendance entre listes** (fenêtres de 6 mois qui se recouvrent) : test par blocs ou par permutation plutôt que test du signe ?
2. **Correction pour comparaisons multiples** (Holm ou Benjamini-Hochberg) sur les 60 tests.
3. **Placebo** : même décalage de coupure sans événement d'annonce, pour séparer « adaptation des joueurs » et « fenêtre plus ancienne ».
4. **Choix du scénario `contenu+borne`** (fixé avant les résultats, mais ajouté après avoir lu les pages) : le garder ?
5. **Les dates de `banlist_announcements`** : surtout les 4 bornes TCG, la règle `date_seule` (même jour ± 1 qu'un article « Announcement »)
   et la définition de `content_date`.

## 5. Limites

- Une seule source de date (Yugipedia et les références qu'elle cite) ; pas de lecture directe des pages Konami pour les listes passées.
- Le contenu a pu fuiter avant l'annonce officielle (spéculation, aperçus) : la date retenue est la publication officielle.
- TCG : une liste annoncée en cinq parties (2026-10-19) est coupée au début de l'événement.
- La page Yugipedia peut être amendée : la table se reconstruit à chaque exécution (`refresh_all.py`, en dernière étape).

## 6. Pour l'orchestrateur (base de référence)

La base de référence n'est pas touchée par cette branche. Après fusion, depuis la racine du dépôt principal :

```
cp data/yugioh.db data/backup_avant_lot21_yugioh_AAAAMMJJ.db     # le script la fait seul à la première création
python scripts/fetch_banlist_announcements.py                     # crée la table (≈ 5 min, réseau)
python scripts/diagnose_ban_radar.py --annonces --out /tmp/lot21  # relance de la mesure, mêmes chiffres attendus
```

La table n'est lue par aucun endpoint : elle n'entre pas dans `SERVED_TABLES`, `serving.db` n'a pas à être reconstruite.
